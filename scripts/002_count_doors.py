import ifcopenshell


def count_doors(ifc_file_path):
    """Count all doors in the IFC model"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        doors = ifc_file.by_type("IfcDoor")
        return len(doors)
    except Exception as e:
        return f"Error: {str(e)}"
