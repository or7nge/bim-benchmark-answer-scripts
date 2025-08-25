import ifcopenshell
from scripts.ifc_utils import get_space_volume


def total_space_volume(ifc_file_path):
    """Calculate total space volume from geometry"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = [s for s in ifc_file.by_type("IfcSpace") if hasattr(s, "is_a")]
        total_volume = 0.0

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)

        for space in spaces:
            try:
                total_volume += get_space_volume(space, settings)
            except:
                continue

        # Fallback: use calculated floor area × average height
        if total_volume == 0:
            from .total_floor_area import total_floor_area

            floor_area = total_floor_area(ifc_file_path)
            if isinstance(floor_area, (int, float)) and floor_area > 0:
                average_ceiling_height = 2.7  # meters
                total_volume = floor_area * average_ceiling_height

        return round(total_volume, 2)

    except Exception as e:
        return f"Error: {str(e)}"
