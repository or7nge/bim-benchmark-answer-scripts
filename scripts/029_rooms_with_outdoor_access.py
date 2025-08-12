import ifcopenshell
import ifcopenshell.geom
import numpy as np
from scipy.spatial import ConvexHull


def verts_array(shape):
    return np.array(shape.geometry.verts).reshape(-1, 3)


def get_external_wall_points(model, settings):
    points = []
    for wall in model.by_type("IfcWall") + model.by_type("IfcWallStandardCase"):
        try:
            shape = ifcopenshell.geom.create_shape(settings, wall)
            pts = verts_array(shape)
            points.extend(pts)
        except:
            continue
    return np.array(points)


def get_door_candidates(model, settings):
    candidates = []
    for el in model.by_type("IfcDoor") + model.by_type("IfcBuildingElementProxy"):
        try:
            shape = ifcopenshell.geom.create_shape(settings, el)
            center = verts_array(shape).mean(axis=0)
            candidates.append((el, center))
        except:
            continue
    return candidates


def get_spaces_geom(model, settings):
    spaces = {}
    for sp in model.by_type("IfcSpace"):
        try:
            shape = ifcopenshell.geom.create_shape(settings, sp)
            spaces[sp] = verts_array(shape).mean(axis=0)
        except:
            continue
    return spaces


def rooms_with_outdoor_access(ifc_file_path):
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    model = ifcopenshell.open(ifc_file_path)

    # 1. Build "external envelope" from wall geometry
    wall_points = get_external_wall_points(model, settings)
    hull = ConvexHull(wall_points)
    hull_pts = wall_points[hull.vertices]
    hull_min = hull_pts.min(axis=0)
    hull_max = hull_pts.max(axis=0)
    tolerance = 0.05 * np.linalg.norm(hull_max - hull_min)  # 5% size

    # 2. Get spaces + door candidates
    spaces_geom = get_spaces_geom(model, settings)
    doors = get_door_candidates(model, settings)

    # 3. Match doors to nearest space if door center is close to hull boundary
    outdoor_rooms = set()
    for door, d_center in doors:
        close_to_edge = (
            abs(d_center[0] - hull_min[0]) < tolerance
            or abs(d_center[0] - hull_max[0]) < tolerance
            or abs(d_center[1] - hull_min[1]) < tolerance
            or abs(d_center[1] - hull_max[1]) < tolerance
        )
        if close_to_edge:
            # Find nearest space
            nearest_space = None
            nearest_dist = np.inf
            for sp, sp_center in spaces_geom.items():
                dist = np.linalg.norm(d_center - sp_center)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_space = sp
            if nearest_space:
                room_type = getattr(nearest_space, "LongName", None) or getattr(nearest_space, "Name", None) or "Unknown"
                outdoor_rooms.add(room_type)

    return list(outdoor_rooms)
