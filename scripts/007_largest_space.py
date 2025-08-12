# scripts/largest_space.py
import ifcopenshell
import ifcopenshell.util.element


def largest_space(ifc_file_path):
    """Find the name and area of the largest space"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        max_area = 0.0
        max_space_name = "No spaces found"

        for space in spaces:
            # Get space area from property sets
            psets = ifcopenshell.util.element.get_psets(space)
            space_area = 0.0

            for pset_data in psets.values():
                area_keys = ["Area", "FloorArea", "NetFloorArea", "GrossFloorArea"]
                for key in area_keys:
                    if key in pset_data and pset_data[key] is not None:
                        space_area = float(pset_data[key])
                        break
                if space_area > 0:
                    break

            # Update maximum if this space is larger
            if space_area > max_area:
                max_area = space_area
                max_space_name = space.Name if space.Name else f"Space_{space.id()}"

        return {"name": max_space_name, "area": round(max_area, 2)}

    except Exception as e:
        return f"Error: {str(e)}"
