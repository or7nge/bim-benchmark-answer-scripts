import ifcopenshell
import ifcopenshell.util.element


def total_floor_area(ifc_file_path):
    """Calculate total floor area of all spaces"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        total_area = 0.0

        for space in spaces:
            # Try to get area from quantity sets
            psets = ifcopenshell.util.element.get_psets(space)
            area_found = False

            for pset_name, pset_data in psets.items():
                if "Area" in pset_data or "FloorArea" in pset_data:
                    area = pset_data.get("Area") or pset_data.get("FloorArea")
                    if area:
                        total_area += float(area)
                        area_found = True
                        break

            # Fallback: try to get from space geometry if no area property
            if not area_found and hasattr(space, "Representation"):
                # This would require more complex geometric calculation
                pass

        return round(total_area, 2)
    except Exception as e:
        return f"Error: {str(e)}"
