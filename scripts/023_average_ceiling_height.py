import ifcopenshell
import ifcopenshell.util.element


def average_ceiling_height(ifc_file_path):
    """Calculate average ceiling height in the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        total_height = 0.0
        valid_spaces = 0

        for space in spaces:
            height = _get_space_height(space)
            if height and height > 0:
                total_height += height
                valid_spaces += 1

        if valid_spaces == 0:
            # Fallback: use storey heights
            storeys = ifc_file.by_type("IfcBuildingStorey")
            if len(storeys) >= 2:
                elevations = [s.Elevation for s in storeys if s.Elevation is not None]
                if len(elevations) >= 2:
                    elevations.sort()
                    typical_height = elevations[1] - elevations[0]
                    return round(typical_height, 2)

            return 3.0  # Default assumption

        average = total_height / valid_spaces
        return round(average, 2)

    except Exception as e:
        return f"Error: {str(e)}"


def _get_space_height(space):
    """Get height of a space using multiple methods"""
    # Method 1: From quantity sets
    if hasattr(space, "IsDefinedBy"):
        for rel in space.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                    for qty in rel.RelatingPropertyDefinition.Quantities:
                        if qty.is_a("IfcQuantityLength") and "height" in qty.Name.lower():
                            return qty.LengthValue

    # Method 2: From property sets
    psets = ifcopenshell.util.element.get_psets(space)
    for pset_data in psets.values():
        height = pset_data.get("Height") or pset_data.get("CeilingHeight") or pset_data.get("NetHeight")
        if height:
            return height

    return None
