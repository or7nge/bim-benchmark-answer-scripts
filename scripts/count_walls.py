import ifcopenshell


def count_walls(ifc_file_path):
    """Count all walls in the IFC model"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = ifc_file.by_type("IfcWall")
        return len(walls)
    except Exception as e:
        return f"Error: {str(e)}"
