# scripts/total_space_volume.py
import ifcopenshell
import ifcopenshell.util.element


def total_space_volume(ifc_file_path):
    """Calculate total volume of all enclosed spaces"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        total_volume = 0.0

        for space in spaces:
            psets = ifcopenshell.util.element.get_psets(space)
            space_volume = 0.0

            # Try to get volume directly
            for pset_data in psets.values():
                volume_keys = ["Volume", "NetVolume", "GrossVolume"]
                for key in volume_keys:
                    if key in pset_data and pset_data[key]:
                        space_volume = float(pset_data[key])
                        break
                if space_volume > 0:
                    break

            # Fallback: calculate from area × height
            if space_volume == 0:
                area, height = 0.0, 0.0
                for pset_data in psets.values():
                    if "Area" in pset_data or "FloorArea" in pset_data:
                        area = float(pset_data.get("Area") or pset_data.get("FloorArea") or 0)
                    if "Height" in pset_data:
                        height = float(pset_data.get("Height") or 0)

                if area > 0:
                    height = height if height > 0 else 2.7  # default ceiling height
                    space_volume = area * height

            total_volume += space_volume

        return round(total_volume, 2)

    except Exception as e:
        return f"Error: {str(e)}"
