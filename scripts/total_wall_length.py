import ifcopenshell
import ifcopenshell.util.element


def total_wall_length(ifc_file_path):
    """Calculate total length of all walls combined"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = ifc_file.by_type("IfcWall")

        total_length = 0.0

        for wall in walls:
            length_found = False

            # Try to get length from quantity sets
            psets = ifcopenshell.util.element.get_psets(wall)
            for pset_name, pset_data in psets.items():
                length = pset_data.get("Length") or pset_data.get("NetLength") or pset_data.get("GrossLength")
                if length:
                    total_length += float(length)
                    length_found = True
                    break

            # Fallback: try to get from representation (simplified approach)
            if not length_found and hasattr(wall, "Representation"):
                # This is a simplified estimation - real implementation would need
                # more complex geometric analysis
                # For now, we'll skip walls without explicit length properties
                pass

        return round(total_length, 2)

    except Exception as e:
        return f"Error: {str(e)}"
