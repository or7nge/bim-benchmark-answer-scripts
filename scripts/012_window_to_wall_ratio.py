import ifcopenshell
from scripts.ifc_utils import get_element_area


def window_to_wall_ratio(ifc_file_path):
    """Calculate ratio of window area to wall area, using geometry if properties are missing."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        windows = ifc_file.by_type("IfcWindow")
        walls = ifc_file.by_type("IfcWall")

        total_window_area = 0.0
        total_wall_area = 0.0

        for window in windows:
            total_window_area += get_element_area(window)

        for wall in walls:
            total_wall_area += get_element_area(wall)

        if total_wall_area == 0:
            return 0.0

        ratio = total_window_area / total_wall_area
        return round(ratio, 3)

    except Exception as e:
        return f"Error: {str(e)}"
