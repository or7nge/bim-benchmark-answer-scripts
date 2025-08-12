import ifcopenshell
import ifcopenshell.util.placement
import math


def building_perimeter(ifc_file_path):
    """Calculate total perimeter length of the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Method 1: From external walls
        perimeter = _calculate_perimeter_from_walls(ifc_file)
        if perimeter > 0:
            return round(perimeter, 2)

        # Method 2: From building footprint
        perimeter = _calculate_perimeter_from_footprint(ifc_file)
        if perimeter > 0:
            return round(perimeter, 2)

        # Method 3: From bounding box (rectangular approximation)
        perimeter = _calculate_perimeter_from_bounding_box(ifc_file)
        return round(perimeter, 2)

    except Exception as e:
        return f"Error: {str(e)}"


# Helper functions (stubs for workspace consistency)
def _calculate_perimeter_from_walls(ifc_file):
    # ...existing code...
    pass


def _is_external_wall(wall):
    # ...existing code...
    pass


def _get_wall_length(wall):
    # ...existing code...
    pass


def _calculate_perimeter_from_footprint(ifc_file):
    # ...existing code...
    pass


def _calculate_perimeter_from_bounding_box(ifc_file):
    # ...existing code...
    pass
