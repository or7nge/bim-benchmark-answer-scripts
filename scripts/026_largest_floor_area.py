import ifcopenshell
from scripts.ifc_utils import get_spaces_in_storey, find_storey_for_element, get_element_area


def largest_floor_area(ifc_file_path):
    """Find which floor has the largest total area"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        storeys = ifc_file.by_type("IfcBuildingStorey")
        spaces = ifc_file.by_type("IfcSpace")

        if not storeys:
            return "No floors found"

        floor_areas = {}

        # Method 1: Sum space areas per floor
        for storey in storeys:
            storey_name = storey.Name or f"Floor_{storey.id()}"
            total_area = 0.0

            # Find spaces in this storey
            storey_spaces = get_spaces_in_storey(storey, spaces)
            for space in storey_spaces:
                area = get_element_area(space)
                total_area += area

            if total_area > 0:
                floor_areas[storey_name] = total_area

        # Method 2: If no spaces, try slabs
        if not floor_areas:
            slabs = ifc_file.by_type("IfcSlab")
            for slab in slabs:
                # Try to associate slab with storey
                storey = find_storey_for_element(slab, storeys)
                if storey:
                    storey_name = storey.Name or f"Floor_{storey.id()}"
                    area = get_element_area(slab)
                    floor_areas[storey_name] = floor_areas.get(storey_name, 0) + area

        if not floor_areas:
            return "No floor areas found"

        # Return floor with largest area
        largest_floor = max(floor_areas, key=floor_areas.get)
        largest_area = floor_areas[largest_floor]
        return f"{largest_floor} ({largest_area:.1f} sq units)"

    except Exception as e:
        return f"Error: {str(e)}"
