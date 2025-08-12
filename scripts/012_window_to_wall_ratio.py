import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom


def window_to_wall_ratio(ifc_file_path):
    """Calculate ratio of window area to wall area, using geometry if properties are missing."""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        windows = ifc_file.by_type("IfcWindow")
        walls = ifc_file.by_type("IfcWall")

        total_window_area = 0.0
        total_wall_area = 0.0

        # Method 1: Try to get area from properties
        for window in windows:
            psets = ifcopenshell.util.element.get_psets(window)
            for pset_name, pset_data in psets.items():
                area = pset_data.get("Area") or pset_data.get("OverallArea")
                if area:
                    total_window_area += float(area)
                    break
            else:
                # Fallback: estimate from width x height if available
                if hasattr(window, "OverallWidth") and hasattr(window, "OverallHeight"):
                    if window.OverallWidth and window.OverallHeight:
                        total_window_area += window.OverallWidth * window.OverallHeight

        for wall in walls:
            psets = ifcopenshell.util.element.get_psets(wall)
            for pset_name, pset_data in psets.items():
                area = pset_data.get("NetSideArea") or pset_data.get("GrossArea") or pset_data.get("Area")
                if area:
                    total_wall_area += float(area)
                    break

        # Method 2: If property-based fails, try geometry
        if (total_window_area == 0 or total_wall_area == 0) and (windows or walls):
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)

            if total_window_area == 0:
                for window in windows:
                    try:
                        if hasattr(window, "Representation") and window.Representation:
                            shape = ifcopenshell.geom.create_shape(settings, window)
                            if shape:
                                # Approximate area from bounding box
                                verts = shape.geometry.verts
                                if len(verts) >= 9:
                                    x_coords = [verts[i] for i in range(0, len(verts), 3)]
                                    y_coords = [verts[i] for i in range(1, len(verts), 3)]
                                    width = max(x_coords) - min(x_coords)
                                    height = max(y_coords) - min(y_coords)
                                    area = width * height
                                    total_window_area += area
                    except:
                        continue

            if total_wall_area == 0:
                for wall in walls:
                    try:
                        if hasattr(wall, "Representation") and wall.Representation:
                            shape = ifcopenshell.geom.create_shape(settings, wall)
                            if shape:
                                verts = shape.geometry.verts
                                if len(verts) >= 9:
                                    x_coords = [verts[i] for i in range(0, len(verts), 3)]
                                    y_coords = [verts[i] for i in range(1, len(verts), 3)]
                                    width = max(x_coords) - min(x_coords)
                                    height = max(y_coords) - min(y_coords)
                                    area = width * height
                                    total_wall_area += area
                    except:
                        continue

        if total_wall_area == 0:
            return 0.0

        ratio = total_window_area / total_wall_area
        return round(ratio, 3)

    except Exception as e:
        return f"Error: {str(e)}"
