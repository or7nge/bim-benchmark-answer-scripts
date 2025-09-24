from collections import defaultdict

from scripts.ifc_utils import find_storey_for_element, map_elements_to_spaces
from scripts.question_helpers import get_ordered_storeys, open_ifc, storey_label


def windowed_space_ratio_by_storey(ifc_file_path):
    """Share of spaces with windows on each storey."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        windows = list(model.by_type("IfcWindow"))
        if not spaces:
            return {}

        storeys = get_ordered_storeys(model)
        storey_map = {}
        storey_counts = defaultdict(int)
        for space in spaces:
            storey = find_storey_for_element(space, storeys)
            key = storey_label(storey) if storey else "Unassigned"
            storey_map[space.id()] = key
            storey_counts[key] += 1

        if not windows:
            return {key: 0.0 for key in storey_counts}

        window_map = map_elements_to_spaces(
            model,
            windows,
            spaces=spaces,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=1,
        )

        storey_window_counts = defaultdict(int)
        seen = set()
        for mapped_spaces in window_map.values():
            if not mapped_spaces:
                continue
            space = mapped_spaces[0]
            sid = space.id()
            if sid in seen:
                continue
            seen.add(sid)
            key = storey_map.get(sid, "Unassigned")
            storey_window_counts[key] += 1

        ratios = {}
        for key, total in storey_counts.items():
            if total == 0:
                ratios[key] = 0.0
            else:
                ratios[key] = storey_window_counts.get(key, 0) / total
        return ratios
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
