import math
from typing import Any, Dict, Iterable, List, Optional, Tuple

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
from ifcopenshell.util import unit as ifc_unit


BoundingBox = Tuple[float, float, float, float, float, float]


_UNIT_SCALE_CACHE: Dict[int, Dict[str, float]] = {}


def is_external_wall(wall):
    """Check if a wall is external (simplified heuristic)"""
    psets = ifcopenshell.util.element.get_psets(wall)
    is_external = False

    # Check IsExternal property
    for pset_data in psets.values():
        if "IsExternal" in pset_data and pset_data["IsExternal"]:
            is_external = True
            break

    # Check name for external keywords
    if not is_external and hasattr(wall, "Name") and wall.Name:
        external_keywords = ["наружн", "внешн", "external", "exterior", "фасад", "outer"]
        is_external = any(keyword in wall.Name.lower() for keyword in external_keywords)

    # Check wall type
    if not is_external and hasattr(wall, "IsDefinedBy"):
        for definition in wall.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByType"):
                wall_type = definition.RelatingType
                if wall_type and hasattr(wall_type, "Name") and wall_type.Name:
                    external_keywords = ["наружн", "внешн", "external", "exterior", "фасад"]
                    is_external = any(keyword in wall_type.Name.lower() for keyword in external_keywords)
                    break

    return is_external


def get_property_value(element, property_names):
    """Get a numerical property value from an element's property sets."""
    psets = ifcopenshell.util.element.get_psets(element)
    for pset_data in psets.values():
        for name in property_names:
            if name in pset_data and pset_data[name] is not None:
                try:
                    value = float(pset_data[name])
                    if value > 0:
                        return value
                except (ValueError, TypeError):
                    continue
    return 0.0


def _get_file_from_element(element: Any) -> Optional[ifcopenshell.file]:
    try:
        return element.wrapped_data.file  # type: ignore[attr-defined]
    except AttributeError:
        return None


def _get_unit_scales_from_file(ifc_file: Optional[ifcopenshell.file]) -> Dict[str, float]:
    if ifc_file is None:
        return {"length": 1.0, "area": 1.0, "volume": 1.0}

    cache_key = id(ifc_file)
    if cache_key in _UNIT_SCALE_CACHE:
        return _UNIT_SCALE_CACHE[cache_key]

    def _calculate(prefix_unit: Optional[Any], target_unit: str) -> float:
        if prefix_unit is None:
            return 1.0
        return ifc_unit.convert(
            1.0,
            getattr(prefix_unit, "Prefix", None),
            prefix_unit.Name,
            None,
            target_unit,
        )

    length_unit = ifc_unit.get_project_unit(ifc_file, "LENGTHUNIT")
    area_unit = ifc_unit.get_project_unit(ifc_file, "AREAUNIT")
    volume_unit = ifc_unit.get_project_unit(ifc_file, "VOLUMEUNIT")

    length_scale = _calculate(length_unit, "METRE") if length_unit else ifc_unit.calculate_unit_scale(ifc_file)
    area_scale = _calculate(area_unit, "SQUARE_METRE") if area_unit else length_scale * length_scale
    volume_scale = _calculate(volume_unit, "CUBIC_METRE") if volume_unit else length_scale ** 3

    scales = {"length": length_scale, "area": area_scale, "volume": volume_scale}
    _UNIT_SCALE_CACHE[cache_key] = scales
    return scales


def _get_unit_scales(element: Optional[Any]) -> Dict[str, float]:
    if element is None:
        return {"length": 1.0, "area": 1.0, "volume": 1.0}
    return _get_unit_scales_from_file(_get_file_from_element(element))


def get_length_scale(obj: Optional[Any] = None, *, ifc_file=None) -> float:
    """Get the model's length scale (project units -> metres)."""
    if ifc_file is not None:
        return _get_unit_scales_from_file(ifc_file)["length"]
    return _get_unit_scales(obj)["length"]


def get_area_scale(obj: Optional[Any] = None, *, ifc_file=None) -> float:
    if ifc_file is not None:
        return _get_unit_scales_from_file(ifc_file)["area"]
    return _get_unit_scales(obj)["area"]


def get_volume_scale(obj: Optional[Any] = None, *, ifc_file=None) -> float:
    if ifc_file is not None:
        return _get_unit_scales_from_file(ifc_file)["volume"]
    return _get_unit_scales(obj)["volume"]


def get_element_area(element):
    """Get area of any IFC element using multiple methods."""
    scales = _get_unit_scales(element)
    area_scale = scales["area"]
    length_scale = scales["length"]

    # Method 1: Quantity sets
    if hasattr(element, "IsDefinedBy"):
        for rel in element.IsDefinedBy or []:
            if rel.is_a("IfcRelDefinesByProperties"):
                prop_def = getattr(rel, "RelatingPropertyDefinition", None)
                if prop_def and prop_def.is_a("IfcElementQuantity"):
                    for qty in getattr(prop_def, "Quantities", []):
                        if qty.is_a("IfcQuantityArea") and getattr(qty, "AreaValue", None):
                            return float(qty.AreaValue) * area_scale

    # Method 2: Property sets
    psets = ifcopenshell.util.element.get_psets(element)
    for pset_data in psets.values():
        area = (
            pset_data.get("Area")
            or pset_data.get("NetArea")
            or pset_data.get("GrossArea")
            or pset_data.get("NetSideArea")
            or pset_data.get("FloorArea")
        )
        if area:
            try:
                return float(area) * area_scale
            except (TypeError, ValueError):
                continue

    # Method 3: Geometric calculation from dimensions
    width = getattr(element, "OverallWidth", None)
    height = getattr(element, "OverallHeight", None)
    if width and height:
        try:
            return float(width) * length_scale * float(height) * length_scale
        except (TypeError, ValueError):
            pass

    # Method 4: Geometric calculation from representation
    return get_element_area_from_geometry(element)


def _init_geom_settings(settings: Optional[ifcopenshell.geom.settings] = None) -> ifcopenshell.geom.settings:
    if settings is not None:
        return settings
    new_settings = ifcopenshell.geom.settings()
    new_settings.set(new_settings.USE_WORLD_COORDS, True)
    return new_settings


def get_element_area_from_geometry(element, settings: Optional[ifcopenshell.geom.settings] = None) -> float:
    """Calculate the area of an element from its geometry as a fallback."""
    settings = _init_geom_settings(settings)
    area = 0.0

    if hasattr(element, "Representation") and element.Representation:
        try:
            shape = ifcopenshell.geom.create_shape(settings, element)
            if shape:
                verts = shape.geometry.verts
                if len(verts) >= 9:
                    x_coords = [verts[i] for i in range(0, len(verts), 3)]
                    y_coords = [verts[i] for i in range(1, len(verts), 3)]
                    z_coords = [verts[i] for i in range(2, len(verts), 3)]

                    if x_coords and y_coords and z_coords:
                        width = max(x_coords) - min(x_coords)
                        depth = max(y_coords) - min(y_coords)
                        height = max(z_coords) - min(z_coords)

                        area1 = width * height
                        area2 = depth * height
                        area = max(area1, area2)
        except Exception:
            pass  # Ignore geometry creation errors
    return area


def get_space_volume(space):
    """Get volume of a space using multiple methods."""
    scales = _get_unit_scales(space)
    volume_scale = scales["volume"]
    length_scale = scales["length"]

    # Method 1: Quantity sets
    if hasattr(space, "IsDefinedBy"):
        for rel in space.IsDefinedBy or []:
            if rel.is_a("IfcRelDefinesByProperties"):
                prop_def = getattr(rel, "RelatingPropertyDefinition", None)
                if prop_def and prop_def.is_a("IfcElementQuantity"):
                    for qty in getattr(prop_def, "Quantities", []):
                        if qty.is_a("IfcQuantityVolume") and getattr(qty, "VolumeValue", None):
                            value = float(qty.VolumeValue) * volume_scale
                            if volume_scale == 1.0 and length_scale != 1.0:
                                value *= length_scale
                            return value

    # Method 2: Property sets
    psets = ifcopenshell.util.element.get_psets(space)
    for pset_data in psets.values():
        volume = pset_data.get("Volume") or pset_data.get("NetVolume") or pset_data.get("GrossVolume")
        if volume:
            try:
                value = float(volume) * volume_scale
                if volume_scale == 1.0 and length_scale != 1.0:
                    value *= length_scale
                return value
            except (TypeError, ValueError):
                continue

    # Method 3: Geometric calculation from representation
    return get_space_volume_from_geometry(space)


def get_space_volume_from_geometry(space, settings: Optional[ifcopenshell.geom.settings] = None) -> float:
    """Calculate the volume of a space from its geometry."""
    settings = _init_geom_settings(settings)
    if hasattr(space, "Representation") and space.Representation:
        try:
            shape = ifcopenshell.geom.create_shape(settings, space)
            if shape:
                geometry = shape.geometry
                if hasattr(geometry, "volume") and geometry.volume:
                    return geometry.volume

                verts = geometry.verts
                if len(verts) >= 9:
                    x_coords = [verts[i] for i in range(0, len(verts), 3)]
                    y_coords = [verts[i] for i in range(1, len(verts), 3)]
                    z_coords = [verts[i] for i in range(2, len(verts), 3)]

                    if x_coords and y_coords and z_coords:
                        width = max(x_coords) - min(x_coords)
                        depth = max(y_coords) - min(y_coords)
                        height = max(z_coords) - min(z_coords)
                        return width * depth * height
        except Exception:
            pass  # Ignore geometry creation errors
    return 0.0


def get_space_height(space):
    """Get height of a space using multiple methods"""
    length_scale = get_length_scale(space)

    # Method 1: From quantity sets
    if hasattr(space, "IsDefinedBy"):
        for rel in space.IsDefinedBy or []:
            if rel.is_a("IfcRelDefinesByProperties"):
                prop_def = getattr(rel, "RelatingPropertyDefinition", None)
                if prop_def and prop_def.is_a("IfcElementQuantity"):
                    for qty in getattr(prop_def, "Quantities", []):
                        if qty.is_a("IfcQuantityLength") and "height" in qty.Name.lower() and getattr(qty, "LengthValue", None):
                            return float(qty.LengthValue) * length_scale

    # Method 2: From property sets
    psets = ifcopenshell.util.element.get_psets(space)
    for pset_data in psets.values():
        height = pset_data.get("Height") or pset_data.get("CeilingHeight") or pset_data.get("NetHeight")
        if height:
            try:
                return float(height) * length_scale
            except (TypeError, ValueError):
                continue

    return None


def get_wall_length(wall):
    length_scale = get_length_scale(wall)

    # 1. Try IfcElementQuantity
    try:
        for rel in getattr(wall, "IsDefinedBy", []) or []:
            prop_set = getattr(rel, "RelatingPropertyDefinition", None)
            if prop_set and prop_set.is_a("IfcElementQuantity"):
                for qty in getattr(prop_set, "Quantities", []):
                    if qty.is_a("IfcQuantityLength") and qty.Name.lower() in {"length", "perimeter"}:
                        if getattr(qty, "LengthValue", None):
                            return float(qty.LengthValue) * length_scale
    except Exception:
        pass

    # 2. Try geometry (bounding box of wall axis)
    try:
        shape = wall.Representation.Representations[0]
        items = shape.Items
        if items:
            for item in items:
                if hasattr(item, "Points") and item.Points:
                    pts = item.Points
                    length = 0.0
                    for i in range(1, len(pts)):
                        p1 = pts[i - 1].Coordinates
                        p2 = pts[i].Coordinates
                        length += math.dist(p1, p2)
                    return length * length_scale
    except Exception:
        pass
    return 0.0


def get_wall_direction(wall):
    try:
        if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
            matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
            y_dir = matrix[1][:3]
            angle = math.atan2(y_dir[0], y_dir[1]) * 180 / math.pi
            angle = (angle + 360) % 360
            if 315 <= angle or angle < 45:
                return "North"
            elif 45 <= angle < 135:
                return "East"
            elif 135 <= angle < 225:
                return "South"
            else:
                return "West"
    except Exception:
        pass
    return None


def find_storey_for_element(element, storeys):
    """Find which storey contains an element"""
    if hasattr(element, "ContainedInStructure"):
        for rel in element.ContainedInStructure:
            if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                return rel.RelatingStructure
    return None


def get_spaces_in_storey(storey, spaces):
    """Get all spaces contained in a storey"""
    storey_spaces = []

    for space in spaces:
        if hasattr(space, "ContainedInStructure"):
            for rel in space.ContainedInStructure:
                if rel.RelatingStructure == storey:
                    storey_spaces.append(space)
                    break

    return storey_spaces


def get_element_bbox(element, settings: Optional[ifcopenshell.geom.settings] = None) -> Optional[BoundingBox]:
    """Return the element bounding box in metres."""
    settings = _init_geom_settings(settings)
    if not hasattr(element, "Representation") or not element.Representation:
        return None
    try:
        shape = ifcopenshell.geom.create_shape(settings, element)
    except Exception:
        return None
    if not shape or not hasattr(shape.geometry, "verts"):
        return None

    verts = shape.geometry.verts
    if not verts:
        return None

    xs = [verts[i] for i in range(0, len(verts), 3)]
    ys = [verts[i] for i in range(1, len(verts), 3)]
    zs = [verts[i] for i in range(2, len(verts), 3)]

    if not xs or not ys or not zs:
        return None

    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))


def get_bbox_center(bbox: BoundingBox) -> Tuple[float, float, float]:
    min_x, min_y, min_z, max_x, max_y, max_z = bbox
    return (
        (min_x + max_x) / 2.0,
        (min_y + max_y) / 2.0,
        (min_z + max_z) / 2.0,
    )


def _point_within_prism(
    point: Tuple[float, float, float],
    bbox: BoundingBox,
    tolerance_horizontal: float,
    tolerance_vertical: float,
) -> bool:
    px, py, pz = point
    min_x, min_y, min_z, max_x, max_y, max_z = bbox
    return (
        min_x - tolerance_horizontal <= px <= max_x + tolerance_horizontal
        and min_y - tolerance_horizontal <= py <= max_y + tolerance_horizontal
        and min_z - tolerance_vertical <= pz <= max_z + tolerance_vertical
    )


def _horizontal_distance_to_bbox(point: Tuple[float, float, float], bbox: BoundingBox) -> float:
    px, py, _ = point
    min_x, min_y, _, max_x, max_y, _ = bbox

    dx = 0.0
    if px < min_x:
        dx = min_x - px
    elif px > max_x:
        dx = px - max_x

    dy = 0.0
    if py < min_y:
        dy = min_y - py
    elif py > max_y:
        dy = py - max_y

    return (dx**2 + dy**2) ** 0.5


def map_elements_to_spaces(
    model: ifcopenshell.file,
    elements: Iterable[Any],
    *,
    spaces: Optional[List[Any]] = None,
    tolerance_horizontal: float = 0.5,
    tolerance_vertical: float = 1.0,
    max_matches: Optional[int] = None,
) -> Dict[int, List[Any]]:
    """Associate elements (doors/windows) with nearby spaces using bounding boxes."""

    spaces = spaces or list(model.by_type("IfcSpace"))
    if not spaces:
        return {}

    settings = _init_geom_settings()
    storeys = list(model.by_type("IfcBuildingStorey"))
    space_storey_map: Dict[int, Optional[int]] = {}
    space_bboxes: Dict[int, BoundingBox] = {}

    for space in spaces:
        bbox = get_element_bbox(space, settings)
        if not bbox:
            continue
        space_bboxes[space.id()] = bbox
        storey = find_storey_for_element(space, storeys)
        space_storey_map[space.id()] = storey.id() if storey else None

    if not space_bboxes:
        return {}

    element_map: Dict[int, List[Any]] = {}

    for element in elements:
        bbox = get_element_bbox(element, settings)
        if not bbox:
            continue
        center = get_bbox_center(bbox)
        element_storey = find_storey_for_element(element, storeys)
        element_storey_id = element_storey.id() if element_storey else None

        matches: List[Tuple[float, Any]] = []
        for space in spaces:
            space_bbox = space_bboxes.get(space.id())
            if not space_bbox:
                continue

            target_storey = space_storey_map.get(space.id())
            if element_storey_id is not None and target_storey not in (element_storey_id, None):
                continue

            if _point_within_prism(center, space_bbox, tolerance_horizontal, tolerance_vertical):
                distance = _horizontal_distance_to_bbox(center, space_bbox)
                matches.append((distance, space))

        if not matches:
            continue

        matches.sort(key=lambda item: item[0])
        if max_matches is not None:
            matches = matches[:max_matches]

        element_map[element.id()] = [space for _, space in matches]

    return element_map


def _check_space_wall_proximity(space, external_walls):
    """Check if space is near external walls (fallback method)"""
    try:
        if hasattr(space, "ObjectPlacement") and space.ObjectPlacement:
            space_matrix = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
            length_scale = get_length_scale(space)
            space_pos = (space_matrix[3][0] * length_scale, space_matrix[3][1] * length_scale)

            for wall in external_walls:
                if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
                    wall_matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
                    wall_pos = (wall_matrix[3][0] * length_scale, wall_matrix[3][1] * length_scale)

                    distance = ((space_pos[0] - wall_pos[0]) ** 2 + (space_pos[1] - wall_pos[1]) ** 2) ** 0.5
                    if distance < 10.0:
                        return True
    except Exception:
        pass

    return False
