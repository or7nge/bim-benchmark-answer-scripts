import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom


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
                if hasattr(space, "Representation") and space.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, space)
                    if shape:
                        # Method 1: Try to get volume directly from shape
                        if hasattr(shape.geometry, "volume"):
                            volume = shape.geometry.volume
                            total_volume += volume
                        else:
                            # Method 2: Calculate from bounding box
                            verts = shape.geometry.verts
                            if len(verts) >= 9:
                                x_coords = [verts[i] for i in range(0, len(verts), 3)]
                                y_coords = [verts[i] for i in range(1, len(verts), 3)]
                                z_coords = [verts[i] for i in range(2, len(verts), 3)]

                                if x_coords and y_coords and z_coords:
                                    width = max(x_coords) - min(x_coords)
                                    depth = max(y_coords) - min(y_coords)
                                    height = max(z_coords) - min(z_coords)
                                    volume = width * depth * height
                                    total_volume += volume
            except:
                continue

        # Fallback: use calculated floor area × average height
        if total_volume == 0:
            from total_floor_area import total_floor_area

            floor_area = total_floor_area(ifc_file_path)
            if isinstance(floor_area, (int, float)) and floor_area > 0:
                average_ceiling_height = 2.7  # meters
                total_volume = floor_area * average_ceiling_height

        return round(total_volume, 2)

    except Exception as e:
        return f"Error: {str(e)}"
