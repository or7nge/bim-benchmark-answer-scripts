from scripts.ifc_utils import map_elements_to_spaces
from scripts.question_helpers import element_orientation, open_ifc


def spaces_with_multi_orientation_windows(ifc_file_path):
    """List spaces receiving daylight from at least two orientations."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        windows = list(model.by_type("IfcWindow"))
        if not spaces or not windows:
            return []

        window_map = map_elements_to_spaces(
            model,
            windows,
            spaces=spaces,
            tolerance_horizontal=0.75,
            tolerance_vertical=1.5,
            max_matches=1,
        )

        orientation_map = {}
        for window in windows:
            mapped_spaces = window_map.get(window.id())
            if not mapped_spaces:
                continue
            orientation = element_orientation(window)
            if not orientation:
                continue
            space = mapped_spaces[0]
            key = space.id()
            if key not in orientation_map:
                orientation_map[key] = {"name": getattr(space, "Name", None) or getattr(space, "LongName", None) or getattr(space, "GlobalId", "Unknown"), "orientations": set()}
            orientation_map[key]["orientations"].add(orientation)

        result = []
        for data in orientation_map.values():
            if len(data["orientations"]) >= 2:
                result.append({"name": str(data["name"]), "orientations": sorted(data["orientations"])})
        return result
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
