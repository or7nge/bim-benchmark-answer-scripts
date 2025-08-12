import ifcopenshell


def list_storeys(ifc_file_path):
    """List all storey names in the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        storeys = ifc_file.by_type("IfcBuildingStorey")
        storey_names = []
        for storey in storeys:
            name = storey.Name if storey.Name else f"Storey_{storey.id()}"
            storey_names.append(name)
        return sorted(storey_names)
    except Exception as e:
        return f"Error: {str(e)}"
