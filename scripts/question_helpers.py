"""Utility helpers for question scripts to reduce duplication."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, TypeVar

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.placement

from scripts.ifc_utils import find_storey_for_element, get_element_area, get_length_scale


Storey = TypeVar("Storey")
Element = TypeVar("Element")


SPACE_USAGE_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "Office": ("office", "work", "workspace"),
    "Meeting": ("meeting", "conference", "board"),
    "Corridor": ("corridor", "hall", "hallway", "passage"),
    "Lobby": ("lobby", "atrium", "reception"),
    "Bathroom": ("bath", "toilet", "wc", "lavatory", "restroom", "sanitary"),
    "Kitchen": ("kitchen", "galley", "canteen"),
    "Storage": ("storage", "store", "closet"),
    "Mechanical": ("mechanical", "plant", "service", "utility"),
    "Residential": ("bed", "living", "apartment", "residential"),
    "Classroom": ("class", "lecture", "training"),
}


def open_ifc(ifc_file_path: str) -> ifcopenshell.file:
    """Open an IFC file and raise a descriptive error on failure."""
    try:
        return ifcopenshell.open(ifc_file_path)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Error opening IFC file: {exc}") from exc


def safe_by_type(model: ifcopenshell.file, entity: str, *, include_subtypes: bool = True):
    """Return all entities of the given type; if absent in schema, return an empty list."""
    try:
        return list(model.by_type(entity, include_subtypes=include_subtypes))
    except RuntimeError:
        return []


def unique_elements(elements: Iterable) -> List:
    """Return elements deduplicated by GlobalId/id to avoid double counting types."""
    unique: List = []
    seen_ids: set = set()
    for element in elements:
        global_id = getattr(element, "GlobalId", None)
        if global_id:
            key = ("guid", global_id)
        else:
            key = ("id", getattr(element, "id", lambda: id(element))())
        if key in seen_ids:
            continue
        seen_ids.add(key)
        unique.append(element)
    return unique


def _placement_elevation(storey) -> Optional[float]:
    if not hasattr(storey, "ObjectPlacement") or not storey.ObjectPlacement:
        return None
    try:
        matrix = ifcopenshell.util.placement.get_local_placement(storey.ObjectPlacement)
        if matrix and len(matrix) > 3:
            return float(matrix[3][2])
    except Exception:
        return None
    return None


def storey_elevation(storey) -> float:
    elevation = getattr(storey, "Elevation", None)
    if elevation is None:
        elevation = _placement_elevation(storey)
    if elevation is None:
        elevation = 0.0
    try:
        return float(elevation)
    except (TypeError, ValueError):
        return 0.0


def storey_sort_key(storey) -> Tuple[float, str, int]:
    elevation = storey_elevation(storey)
    name = getattr(storey, "Name", None) or ""
    return elevation, name, getattr(storey, "id", lambda: 0)()


def get_ordered_storeys(model: ifcopenshell.file) -> List:
    storeys = list(model.by_type("IfcBuildingStorey"))
    storeys.sort(key=storey_sort_key)
    return storeys


def storey_label(storey) -> str:
    name = getattr(storey, "Name", None)
    if name:
        return str(name)
    long_name = getattr(storey, "LongName", None)
    if long_name:
        return str(long_name)
    return f"Storey_{storey.id()}"


def group_elements_by_storey(
    storeys: Sequence,
    elements: Iterable,
    *,
    default_label: str = "Unassigned",
    storey_filter: Optional[Callable[[Storey], bool]] = None,
) -> Dict[str, List]:
    """Group elements by their containing storey."""
    storey_filter = storey_filter or (lambda _: True)
    valid_storeys = [s for s in storeys if storey_filter(s)]
    element_groups: Dict[str, List] = defaultdict(list)

    storey_lookup = {s.id(): s for s in valid_storeys}

    for element in elements:
        storey = find_storey_for_element(element, valid_storeys)
        if storey is None:
            element_groups[default_label].append(element)
        else:
            element_groups[storey_label(storey)].append(element)

    return dict(element_groups)


def count_elements_by_storey(
    storeys: Sequence,
    elements: Iterable,
    *,
    default_label: str = "Unassigned",
) -> Dict[str, int]:
    """Count elements by storey using containment relationships."""
    counts = defaultdict(int)
    for element in elements:
        storey = find_storey_for_element(element, storeys)
        if storey is None:
            counts[default_label] += 1
        else:
            counts[storey_label(storey)] += 1
    return dict(counts)


def classify_orientation(angle_degrees: float) -> str:
    angle = angle_degrees % 360
    if 315 <= angle or angle < 45:
        return "North"
    if 45 <= angle < 135:
        return "East"
    if 135 <= angle < 225:
        return "South"
    return "West"


def element_orientation(element, axis_index: int = 1) -> Optional[str]:
    """Return cardinal orientation for an element based on its placement."""
    if not hasattr(element, "ObjectPlacement") or not element.ObjectPlacement:
        return None
    try:
        matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
        if matrix is not None and len(matrix) > axis_index:
            direction = matrix[axis_index][:3]
            angle = math.degrees(math.atan2(direction[0], direction[1]))
            return classify_orientation(angle)
    except Exception:
        return None
    return None


def orientation_counts(elements: Iterable, axis_index: int = 1) -> Dict[str, int]:
    counts = defaultdict(int)
    for element in elements:
        orientation = element_orientation(element, axis_index=axis_index)
        if orientation:
            counts[orientation] += 1
        else:
            counts["Unknown"] += 1
    return dict(counts)


def orientation_counts_by_storey(
    storeys: Sequence,
    elements: Iterable,
    *,
    default_label: str = "Unassigned",
    axis_index: int = 1,
) -> Dict[str, Dict[str, int]]:
    """Return orientation counts grouped by storey."""
    grouped = defaultdict(lambda: defaultdict(int))

    for element in elements:
        storey = find_storey_for_element(element, storeys)
        key = storey_label(storey) if storey else default_label
        orientation = element_orientation(element, axis_index=axis_index)
        if orientation:
            grouped[key][orientation] += 1
        else:
            grouped[key]["Unknown"] += 1

    return {storey: dict(orientations) for storey, orientations in grouped.items()}


def aggregate_numeric(
    elements: Iterable[Element],
    value_getter: Callable[[Element], Optional[float]],
) -> Dict[str, float]:
    """Return aggregate statistics (min/max/avg) for a sequence of element values."""
    values = [value for value in (value_getter(element) for element in elements) if value is not None]
    if not values:
        return {"count": 0, "min": 0.0, "max": 0.0, "average": 0.0}
    total = sum(values)
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "average": total / len(values),
    }


def element_area(element) -> Optional[float]:
    try:
        area = get_element_area(element)
        return area if area > 0 else None
    except Exception:
        return None


def elements_area_by_storey(
    storeys: Sequence,
    elements: Iterable,
    *,
    default_label: str = "Unassigned",
) -> Dict[str, float]:
    areas = defaultdict(float)
    for element in elements:
        area = element_area(element)
        if area is None:
            continue
        storey = find_storey_for_element(element, storeys)
        key = storey_label(storey) if storey else default_label
        areas[key] += area
    return dict(areas)


def get_element_dimensions(element) -> Tuple[Optional[float], Optional[float]]:
    """Return (width, height) in project units for doors/windows."""
    width = getattr(element, "OverallWidth", None)
    height = getattr(element, "OverallHeight", None)

    # Convert to float when possible
    try:
        width = float(width) if width is not None else None
    except (TypeError, ValueError):
        width = None
    try:
        height = float(height) if height is not None else None
    except (TypeError, ValueError):
        height = None

    if width is None or height is None:
        # Try from property sets as fallback
        psets = ifcopenshell.util.element.get_psets(element)
        width_candidates = ["Width", "OverallWidth", "NominalWidth", "ClearWidth"]
        height_candidates = ["Height", "OverallHeight", "NominalHeight", "ClearHeight"]

        if width is None:
            for pset in psets.values():
                for key in width_candidates:
                    if key in pset and pset[key]:
                        try:
                            width = float(pset[key])
                            break
                        except (TypeError, ValueError):
                            continue
                if width is not None:
                    break

        if height is None:
            for pset in psets.values():
                for key in height_candidates:
                    if key in pset and pset[key]:
                        try:
                            height = float(pset[key])
                            break
                        except (TypeError, ValueError):
                            continue
                if height is not None:
                    break

    if width is not None:
        width *= get_length_scale(element)
    if height is not None:
        height *= get_length_scale(element)

    return width, height


def classify_space_usage(space) -> str:
    """Classify a space into a coarse usage bucket based on metadata keywords."""
    labels: List[str] = []
    for attr in ("LongName", "Name", "ObjectType", "Description"):
        value = getattr(space, attr, None)
        if value:
            labels.append(str(value))

    psets = ifcopenshell.util.element.get_psets(space)
    for data in psets.values():
        for key in ("Name", "Usage", "Category", "SpaceType", "Function", "OccupancyType"):
            value = data.get(key)
            if value:
                labels.append(str(value))

    combined = " ".join(labels).lower()
    for category, keywords in SPACE_USAGE_KEYWORDS.items():
        if any(keyword in combined for keyword in keywords):
            return category
    return "Other"


def value_distribution_buckets(
    values: Iterable[float],
    bucket_size: float,
    *,
    precision: int = 2,
) -> Dict[str, int]:
    buckets: Dict[str, int] = defaultdict(int)
    for value in values:
        if value < 0:
            continue
        lower = math.floor(value / bucket_size) * bucket_size
        upper = lower + bucket_size
        label = f"{lower:.{precision}f}-{upper:.{precision}f}"
        buckets[label] += 1
    return dict(buckets)
