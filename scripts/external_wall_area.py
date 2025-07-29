# scripts/external_wall_area.py
import ifcopenshell
import ifcopenshell.util.element


def external_wall_area(ifc_file_path):
    """Calculate total area of external walls"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = ifc_file.by_type("IfcWall")
        total_external_area = 0.0

        for wall in walls:
            is_external = False

            # Check IsExternal property
            psets = ifcopenshell.util.element.get_psets(wall)
            for pset_data in psets.values():
                if "IsExternal" in pset_data:
                    is_external = pset_data["IsExternal"]
                    break

            # Fallback: check name for external keywords
            if not is_external and wall.Name:
                external_keywords = ["external", "exterior", "outer", "facade"]
                is_external = any(keyword in wall.Name.lower() for keyword in external_keywords)

            if is_external:
                # Get wall area from quantity sets
                for pset_data in psets.values():
                    area_keys = ["NetSideArea", "GrossSideArea", "Area"]
                    for key in area_keys:
                        if key in pset_data and pset_data[key]:
                            total_external_area += float(pset_data[key])
                            break

        return round(total_external_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"
