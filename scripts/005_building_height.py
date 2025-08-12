import ifcopenshell


def building_height(ifc_file_path):
    """Calculate total building height"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        storeys = ifc_file.by_type("IfcBuildingStorey")

        if not storeys:
            return 0.0

        elevations = []
        for storey in storeys:
            if storey.Elevation is not None:
                elevations.append(storey.Elevation)

        if len(elevations) >= 2:
            # Calculate height as difference between highest and lowest elevation
            height = max(elevations) - min(elevations)

            # Add typical floor height for the top floor
            typical_floor_height = 3.0  # Default assumption
            height += typical_floor_height

            return round(height, 2)
        else:
            return 0.0

    except Exception as e:
        return f"Error: {str(e)}"
