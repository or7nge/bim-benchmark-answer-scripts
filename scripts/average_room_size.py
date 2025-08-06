import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom


def average_room_size(ifc_file_path):
    """Calculate average room size in the building, using geometry if properties are missing."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        total_area = 0.0
        valid_spaces = 0

        # Method 1: Try to get area from properties
        for space in spaces:
            psets = ifcopenshell.util.element.get_psets(space)
            for pset_name, pset_data in psets.items():
                area = pset_data.get("Area") or pset_data.get("FloorArea") or pset_data.get("NetFloorArea")
                if area:
                    total_area += float(area)
                    valid_spaces += 1
                    break

        # Method 2: If property-based fails, try geometry
        if valid_spaces == 0:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            for space in spaces:
                try:
                    if hasattr(space, "Representation") and space.Representation:
                        shape = ifcopenshell.geom.create_shape(settings, space)
                        if shape:
                            verts = shape.geometry.verts
                            if len(verts) >= 9:
                                x_coords = [verts[i] for i in range(0, len(verts), 3)]
                                y_coords = [verts[i] for i in range(1, len(verts), 3)]
                                width = max(x_coords) - min(x_coords)
                                depth = max(y_coords) - min(y_coords)
                                area = width * depth
                                total_area += area
                                valid_spaces += 1
                except:
                    continue

        if valid_spaces == 0:
            return 0.0

        average = total_area / valid_spaces
        return round(average, 2)

    except Exception as e:
        return f"Error: {str(e)}"
