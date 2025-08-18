import ifcopenshell
import ifcopenshell.util.placement
import math


def building_perimeter(ifc_file_path):
    """Calculate total perimeter length of the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Method 1: From external walls
        perimeter = _calculate_perimeter_from_walls(ifc_file)
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
def _calculate_perimeter_from_walls(ifc_file):
    # Sum the lengths of all external walls
    walls = ifc_file.by_type("IfcWall")
    perimeter = 0.0
    for wall in walls:
        if _is_external_wall(wall):
            length = _get_wall_length(wall)
            if length:
                perimeter += length
    return perimeter


def _is_external_wall(wall):
    """Check if a wall is external (robust heuristic)"""
    # Check for 'IsExternal' property in property sets
    try:
        for rel in getattr(wall, "IsDefinedBy", []):
            prop_set = getattr(rel, "RelatingPropertyDefinition", None)
            if prop_set and hasattr(prop_set, "HasProperties"):
                for prop in prop_set.HasProperties:
                    if prop.Name.lower() == "isexternal" and hasattr(prop, "NominalValue"):
                        if str(prop.NominalValue.wrappedValue).lower() == "true":
                            return True
    except Exception:
        pass
    # Fallback: check for 'external' in name/description
    if "external" in (getattr(wall, "Name", "") or "").lower() or "external" in (getattr(wall, "Description", "") or "").lower():
        return True
    # Fallback: check PredefinedType
    if hasattr(wall, "PredefinedType"):
        if "EXTERNAL" in str(wall.PredefinedType):
            return True
    return False


def _get_wall_length(wall):
    # Try to get wall length from IfcQuantityLength or geometry
    # 1. Try IfcElementQuantity
    try:
        for rel in getattr(wall, "IsDefinedBy", []):
            prop_set = getattr(rel, "RelatingPropertyDefinition", None)
            if prop_set and prop_set.is_a("IfcElementQuantity"):
                for qty in getattr(prop_set, "Quantities", []):
                    if qty.is_a("IfcQuantityLength") and qty.Name.lower() in ["length", "perimeter"]:
                        return float(qty.LengthValue)
    except Exception:
        pass
    # 2. Try geometry (bounding box of wall)
    try:
        shape = wall.Representation.Representations[0]
        items = shape.Items
        if items:
            # Use the first polyline or extrusion
            for item in items:
                if hasattr(item, "Points") and item.Points:
                    pts = item.Points
                    length = 0.0
                    for i in range(1, len(pts)):
                        p1 = pts[i - 1].Coordinates
                        p2 = pts[i].Coordinates
                        length += math.dist(p1, p2)
                    return length
    except Exception:
        pass
    return 0.0


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
