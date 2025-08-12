import ifcopenshell
import ifcopenshell.util.element


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
            storey_spaces = _get_spaces_in_storey(storey, spaces)
            for space in storey_spaces:
                area = _get_space_area(space)
                total_area += area

            if total_area > 0:
                floor_areas[storey_name] = total_area

        # Method 2: If no spaces, try slabs
        if not floor_areas:
            slabs = ifc_file.by_type("IfcSlab")
            for slab in slabs:
                # Try to associate slab with storey
                storey = _find_storey_for_element(slab, storeys)
                if storey:
                    storey_name = storey.Name or f"Floor_{storey.id()}"
                    area = _get_element_area(slab)
                    floor_areas[storey_name] = floor_areas.get(storey_name, 0) + area

        if not floor_areas:
            return "No floor areas found"

        # Return floor with largest area
        largest_floor = max(floor_areas, key=floor_areas.get)
        largest_area = floor_areas[largest_floor]
        return f"{largest_floor} ({largest_area:.1f} sq units)"

    except Exception as e:
        return f"Error: {str(e)}"


def _get_spaces_in_storey(storey, spaces):
    """Get all spaces contained in a storey"""
    storey_spaces = []

    for space in spaces:
        if hasattr(space, "ContainedInStructure"):
            for rel in space.ContainedInStructure:
                if rel.RelatingStructure == storey:
                    storey_spaces.append(space)
                    break

    return storey_spaces


def _find_storey_for_element(element, storeys):
    """Find which storey contains an element"""
    if hasattr(element, "ContainedInStructure"):
        for rel in element.ContainedInStructure:
            if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                return rel.RelatingStructure
    return None


def _get_space_area(space):
    """Get area of a space using multiple methods"""
    # Try quantity sets
    if hasattr(space, "IsDefinedBy"):
        for rel in space.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                    for qty in rel.RelatingPropertyDefinition.Quantities:
                        if qty.is_a("IfcQuantityArea"):
                            return qty.AreaValue

    # Try property sets
    psets = ifcopenshell.util.element.get_psets(space)
    for pset_data in psets.values():
        area = pset_data.get("FloorArea") or pset_data.get("Area") or pset_data.get("NetFloorArea")
        if area:
            return area

    return 0.0


def _get_element_area(element):
    """Generic function to get area from any IFC element"""
    area = None

    # Method 1: Quantity sets
    if hasattr(element, "IsDefinedBy"):
        for rel in element.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                    for qty in rel.RelatingPropertyDefinition.Quantities:
                        if qty.is_a("IfcQuantityArea"):
                            area = qty.AreaValue
                            break
            if area:
                break

    # Method 2: Property sets
    if not area:
        psets = ifcopenshell.util.element.get_psets(element)
        for pset_data in psets.values():
            area = pset_data.get("NetSideArea") or pset_data.get("GrossArea") or pset_data.get("Area") or pset_data.get("NetArea")
            if area:
                break

    return area if area else 0.0
