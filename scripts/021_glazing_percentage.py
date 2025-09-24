import ifcopenshell
from scripts.ifc_utils import get_element_area


def glazing_percentage(ifc_file_path):
    """Calculate percentage of building that is glazed (windows vs walls)"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        total_window_area = 0
        for window in ifc_file.by_type("IfcWindow"):
            total_window_area += get_element_area(window)
        for curtain_wall in ifc_file.by_type("IfcCurtainWall"):
            total_window_area += get_element_area(curtain_wall)

        total_wall_area = 0
        for wall in ifc_file.by_type("IfcWall"):
            total_wall_area += get_element_area(wall)

        if total_wall_area == 0:
            return 0.0

        glazing_ratio = (total_window_area / total_wall_area) * 100
        return round(glazing_ratio, 2)

    except Exception as e:
        return f"Error: {str(e)}"
