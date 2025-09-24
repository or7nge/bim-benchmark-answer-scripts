import ifcopenshell
import ifcopenshell.geom

from scripts.ifc_utils import get_element_bbox, get_length_scale, get_space_height, get_spaces_in_storey


def building_height(ifc_file_path):
    """Estimate the building height in metres using space geometry and storey data."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        spaces = list(ifc_file.by_type("IfcSpace"))
        z_extents = []
        if spaces:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            for space in spaces:
                bbox = get_element_bbox(space, settings)
                if bbox:
                    z_extents.extend([bbox[2], bbox[5]])

        if z_extents:
            height = max(z_extents) - min(z_extents)
            if height > 0:
                return round(height, 2)

        storeys = [s for s in ifc_file.by_type("IfcBuildingStorey") if s.Elevation is not None]
        if not storeys:
            return 0.0

        storeys.sort(key=lambda s: s.Elevation)
        length_scale = get_length_scale(ifc_file=ifc_file)
        elevations = [float(s.Elevation) * length_scale for s in storeys]

        if len(elevations) == 1:
            storey_spaces = get_spaces_in_storey(storeys[0], spaces)
            max_height = max((get_space_height(space) or 0.0) for space in storey_spaces) if storey_spaces else 0.0
            return round(max_height, 2)

        base_height = elevations[-1] - elevations[0]

        top_storey_spaces = get_spaces_in_storey(storeys[-1], spaces)
        top_storey_height = max((get_space_height(space) or 0.0) for space in top_storey_spaces) if top_storey_spaces else 0.0

        if top_storey_height <= 0.0:
            diffs = [elevations[i + 1] - elevations[i] for i in range(len(elevations) - 1)]
            positive_diffs = [d for d in diffs if d > 0]
            if positive_diffs:
                top_storey_height = positive_diffs[-1]

        total_height = base_height + max(top_storey_height, 0.0)
        return round(total_height, 2)

    except Exception as e:
        return f"Error: {str(e)}"
