import ifcopenshell

from scripts.ifc_utils import get_length_scale, get_space_height


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
            try:
                height = get_space_height(space)
            except Exception:
                continue
            if height and height > 0:
                total_height += height
                valid_spaces += 1

        if valid_spaces == 0:
            # Fallback: use storey heights
            storeys = [s for s in ifc_file.by_type("IfcBuildingStorey") if s.Elevation is not None]
            if len(storeys) >= 2:
                length_scale = get_length_scale(ifc_file=ifc_file)
                elevations = sorted(float(s.Elevation) * length_scale for s in storeys)
                diffs = [elevations[i + 1] - elevations[i] for i in range(len(elevations) - 1)]
                positive_diffs = [d for d in diffs if d > 0]
                if positive_diffs:
                    return round(sum(positive_diffs) / len(positive_diffs), 2)

            return 0.0

        average = total_height / valid_spaces
        return round(average, 2)

    except Exception as e:
        return f"Error: {str(e)}"
