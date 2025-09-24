from scripts.ifc_utils import map_elements_to_spaces
from scripts.question_helpers import element_area, open_ifc


def lit_space_area_ratio(ifc_file_path):
    """Share of total space area that has at least one mapped window."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        windows = list(model.by_type("IfcWindow"))
        if not spaces:
            return 0.0

        total_area = 0.0
        for space in spaces:
            area = element_area(space)
            if area is not None:
                total_area += area

        if total_area == 0:
            return 0.0

        if not windows:
            return 0.0

        window_map = map_elements_to_spaces(
            model,
            windows,
            spaces=spaces,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=1,
        )

        lit_space_ids = {space.id() for matches in window_map.values() for space in matches}
        lit_area = 0.0
        for space in spaces:
            if space.id() not in lit_space_ids:
                continue
            area = element_area(space)
            if area is not None:
                lit_area += area
        return lit_area / total_area if total_area else 0.0
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
