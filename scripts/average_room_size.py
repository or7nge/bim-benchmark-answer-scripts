import ifcopenshell
import ifcopenshell.util.element


def average_room_size(ifc_file_path):
    """Calculate average room size in the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        total_area = 0.0
        valid_spaces = 0

        for space in spaces:
            psets = ifcopenshell.util.element.get_psets(space)
            area_found = False

            for pset_name, pset_data in psets.items():
                area = pset_data.get("Area") or pset_data.get("FloorArea") or pset_data.get("NetFloorArea")
                if area:
                    total_area += float(area)
                    valid_spaces += 1
                    area_found = True
                    break

        if valid_spaces == 0:
            return 0.0

        average = total_area / valid_spaces
        return round(average, 2)

    except Exception as e:
        return f"Error: {str(e)}"
