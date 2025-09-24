import ifcopenshell
from scripts.ifc_utils import is_external_wall, get_wall_length
import math


def building_perimeter(ifc_file_path):
    """Calculate total perimeter length of the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Method 1: From external walls
        perimeter = 0
        walls = ifc_file.by_type("IfcWall")
        for wall in walls:
            if is_external_wall(wall):
                length = get_wall_length(wall)
                if length:
                    perimeter += length

        if perimeter > 0:
            return round(perimeter, 2)

        # Method 2: From building footprint
        perimeter = _calculate_perimeter_from_footprint(ifc_file)
        if perimeter > 0:
            return round(perimeter, 2)

        # Method 3: From bounding box (rectangular approximation)
        perimeter = _calculate_perimeter_from_bounding_box(ifc_file)
        return round(perimeter, 2)

    except Exception as e:
        return f"Error: {str(e)}"


# Helper functions (stubs for workspace consistency)
def _calculate_perimeter_from_footprint(ifc_file):
    # Try to get the perimeter from the building's footprint (IfcSite or IfcBuilding)
    try:
        sites = ifc_file.by_type("IfcSite")
        buildings = ifc_file.by_type("IfcBuilding")
        for obj in sites + buildings:
            if hasattr(obj, "Representation") and obj.Representation:
                for rep in obj.Representation.Representations:
                    if rep.RepresentationType == "Curve2D" or rep.RepresentationType == "GeometricCurveSet":
                        for item in rep.Items:
                            if hasattr(item, "Points") and item.Points:
                                pts = item.Points
                                length = 0.0
                                for i in range(1, len(pts)):
                                    p1 = pts[i - 1].Coordinates
                                    p2 = pts[i].Coordinates
                                    length += math.dist(p1, p2)
                                # Close the loop
                                if len(pts) > 2:
                                    p1 = pts[-1].Coordinates
                                    p2 = pts[0].Coordinates
                                    length += math.dist(p1, p2)
                                return length
    except Exception:
        pass
    return 0.0


def _calculate_perimeter_from_bounding_box(ifc_file):
    # Use the bounding box of all IfcWall objects as a fallback
    try:
        walls = ifc_file.by_type("IfcWall")
        xs, ys = [], []
        for wall in walls:
            if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
                loc = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
                if loc:
                    xs.append(loc[0])
                    ys.append(loc[1])
        if xs and ys:
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            width = max_x - min_x
            depth = max_y - min_y
            return 2 * (abs(width) + abs(depth))
    except Exception:
        pass
    return 0.0
