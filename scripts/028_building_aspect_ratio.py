import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.placement


def building_aspect_ratio(ifc_file_path):
    """Calculate building's aspect ratio (length to width)"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Method 1: From building geometry
        ratio = _get_ratio_from_geometry(ifc_file)
        if ratio > 0:
            return round(ratio, 2)

        # Method 2: From wall positions
        ratio = _get_ratio_from_walls(ifc_file)
        if ratio > 0:
            return round(ratio, 2)

        # Method 3: From spaces bounding box
        ratio = _get_ratio_from_spaces(ifc_file)
        return round(ratio, 2)

    except Exception as e:
        return f"Error: {str(e)}"


def _get_ratio_from_geometry(ifc_file):
    """Calculate ratio from building geometry"""
    try:
        buildings = ifc_file.by_type("IfcBuilding")
        walls = ifc_file.by_type("IfcWall")

        all_elements = buildings + walls
        if not all_elements:
            return 0.0

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)

        all_points = []

        for element in all_elements[:20]:  # Limit to avoid performance issues
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
                if shape:
                    geometry = shape.geometry
                    if hasattr(geometry, "verts"):
                        verts = geometry.verts
                        for i in range(0, len(verts), 3):
                            all_points.append((verts[i], verts[i + 1]))
            except:
                continue

        if len(all_points) < 4:
            return 0.0

        min_x = min(p[0] for p in all_points)
        max_x = max(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_y = max(p[1] for p in all_points)

        length = max(max_x - min_x, max_y - min_y)
        width = min(max_x - min_x, max_y - min_y)

        return length / width if width > 0 else 0.0

    except Exception:
        return 0.0


def _get_ratio_from_walls(ifc_file):
    """Calculate ratio from wall positions"""
    try:
        walls = ifc_file.by_type("IfcWall")
        if not walls:
            return 0.0

        wall_points = []

        for wall in walls:
            if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
                try:
                    matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
                    x, y = matrix[3][0], matrix[3][1]
                    wall_points.append((x, y))
                except:
                    continue

        if len(wall_points) < 4:
            return 0.0

        min_x = min(p[0] for p in wall_points)
        max_x = max(p[0] for p in wall_points)
        min_y = min(p[1] for p in wall_points)
        max_y = max(p[1] for p in wall_points)

        length = max(max_x - min_x, max_y - min_y)
        width = min(max_x - min_x, max_y - min_y)

        return length / width if width > 0 else 0.0

    except Exception:
        return 0.0


def _get_ratio_from_spaces(ifc_file):
    """Calculate ratio from space bounding box"""
    try:
        spaces = ifc_file.by_type("IfcSpace")
        if not spaces:
            return 1.0  # Default square ratio

        space_points = []

        for space in spaces:
            if hasattr(space, "ObjectPlacement") and space.ObjectPlacement:
                try:
                    matrix = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
                    x, y = matrix[3][0], matrix[3][1]
                    space_points.append((x, y))
                except:
                    continue

        if len(space_points) < 2:
            return 1.0

        min_x = min(p[0] for p in space_points)
        max_x = max(p[0] for p in space_points)
        min_y = min(p[1] for p in space_points)
        max_y = max(p[1] for p in space_points)

        length = max(max_x - min_x, max_y - min_y)
        width = min(max_x - min_x, max_y - min_y)

        return length / width if width > 0 else 1.0

    except Exception:
        return 1.0
