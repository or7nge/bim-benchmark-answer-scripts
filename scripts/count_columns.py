import ifcopenshell


def count_columns(ifc_file_path):
    """Count all structural columns"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        columns = ifc_file.by_type("IfcColumn")
        return len(columns)
    except Exception as e:
        return f"Error: {str(e)}"
