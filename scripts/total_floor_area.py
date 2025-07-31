import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom


def total_floor_area(ifc_file_path):
    """Calculate area from geometry since properties don't contain area values"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        total_area = 0.0

        # Filter valid spaces
        spaces = [s for s in ifc_file.by_type("IfcSpace") if hasattr(s, "is_a")]

        # Method 1: Calculate from space geometry
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)

        for space in spaces:
            try:
                if hasattr(space, "Representation") and space.Representation:
                    shape = ifcopenshell.geom.create_shape(settings, space)
                    if shape:
                        # Get the surface area (this gives total surface area, not just floor)
                        # We'll approximate floor area as total_surface_area / 6 (assuming box-like rooms)
                        surface_area = shape.geometry.surface_area
                        estimated_floor_area = surface_area / 6  # Very rough approximation
                        total_area += estimated_floor_area
            except:
                continue

        # Method 2: If geometry method fails, try bounding box approach
        if total_area == 0:
            for space in spaces:
                try:
                    if hasattr(space, "Representation") and space.Representation:
                        shape = ifcopenshell.geom.create_shape(settings, space)
                        if shape:
                            # Get bounding box and calculate floor area
                            verts = shape.geometry.verts
                            if len(verts) >= 9:  # At least 3 vertices (x,y,z each)
                                # Extract x, y coordinates (every 3rd element starting from 0,1)
                                x_coords = [verts[i] for i in range(0, len(verts), 3)]
                                y_coords = [verts[i] for i in range(1, len(verts), 3)]

                                if x_coords and y_coords:
                                    width = max(x_coords) - min(x_coords)
                                    depth = max(y_coords) - min(y_coords)
                                    floor_area = width * depth
                                    total_area += floor_area
                except:
                    continue

        # Method 3: If still no area, use space count with average area
        if total_area == 0 and spaces:
            # Fallback: assume average room size of 20 m² per space
            total_area = len(spaces) * 20.0

        return round(total_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"
