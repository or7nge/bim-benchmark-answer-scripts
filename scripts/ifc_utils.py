import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom
import ifcopenshell.util.placement
import math


def is_external_wall(wall):
    """Check if a wall is external (simplified heuristic)"""
    psets = ifcopenshell.util.element.get_psets(wall)
    is_external = False

    # Check IsExternal property
    for pset_data in psets.values():
        if "IsExternal" in pset_data and pset_data["IsExternal"]:
            is_external = True
            break

    # Check name for external keywords
    if not is_external and hasattr(wall, "Name") and wall.Name:
        external_keywords = ["наружн", "внешн", "external", "exterior", "фасад", "outer"]
        is_external = any(keyword in wall.Name.lower() for keyword in external_keywords)

    # Check wall type
    if not is_external and hasattr(wall, "IsDefinedBy"):
        for definition in wall.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByType"):
                wall_type = definition.RelatingType
                if wall_type and hasattr(wall_type, "Name") and wall_type.Name:
                    external_keywords = ["наружн", "внешн", "external", "exterior", "фасад"]
                    is_external = any(keyword in wall_type.Name.lower() for keyword in external_keywords)
                    break

    return is_external


def get_property_value(element, property_names):
    """Get a numerical property value from an element's property sets."""
    psets = ifcopenshell.util.element.get_psets(element)
    for pset_data in psets.values():
        for name in property_names:
            if name in pset_data and pset_data[name] is not None:
                try:
                    value = float(pset_data[name])
                    if value > 0:
                        return value
                except (ValueError, TypeError):
                    continue
    return 0.0


def get_element_area(element):
    """Get area of any IFC element using multiple methods."""
    # Method 1: Quantity sets
    if hasattr(element, "IsDefinedBy"):
        for rel in element.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                    for qty in rel.RelatingPropertyDefinition.Quantities:
                        if qty.is_a("IfcQuantityArea"):
                            return qty.AreaValue

    # Method 2: Property sets
    psets = ifcopenshell.util.element.get_psets(element)
    for pset_data in psets.values():
        area = (
            pset_data.get("Area")
            or pset_data.get("NetArea")
            or pset_data.get("GrossArea")
            or pset_data.get("NetSideArea")
            or pset_data.get("FloorArea")
        )
        if area:
            return area

    # Method 3: Geometric calculation from dimensions
    width = getattr(element, "OverallWidth", None)
    height = getattr(element, "OverallHeight", None)
    if width and height:
        return width * height

    # Method 4: Geometric calculation from representation
    return get_element_area_from_geometry(element)


def get_element_area_from_geometry(element):
    """Calculate the area of an element from its geometry as a fallback."""
    area = 0.0
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    if hasattr(element, "Representation") and element.Representation:
        try:
            shape = ifcopenshell.geom.create_shape(settings, element)
            if shape:
                verts = shape.geometry.verts
                if len(verts) >= 9:
                    x_coords = [verts[i] for i in range(0, len(verts), 3)]
                    y_coords = [verts[i] for i in range(1, len(verts), 3)]
                    z_coords = [verts[i] for i in range(2, len(verts), 3)]

                    if x_coords and y_coords and z_coords:
                        width = max(x_coords) - min(x_coords)
                        depth = max(y_coords) - min(y_coords)
                        height = max(z_coords) - min(z_coords)

                        # Take the larger face area
                        area1 = width * height
                        area2 = depth * height
                        area = max(area1, area2)
        except Exception:
            pass  # Ignore geometry creation errors
    return area


def get_space_volume(space):
    """Get volume of a space using multiple methods."""
    # Method 1: Quantity sets
    if hasattr(space, "IsDefinedBy"):
        for rel in space.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                    for qty in rel.RelatingPropertyDefinition.Quantities:
                        if qty.is_a("IfcQuantityVolume"):
                            return qty.VolumeValue

    # Method 2: Property sets
    psets = ifcopenshell.util.element.get_psets(space)
    for pset_data in psets.values():
        volume = pset_data.get("Volume") or pset_data.get("NetVolume") or pset_data.get("GrossVolume")
        if volume:
            return volume

    # Method 3: Geometric calculation from representation
    return get_space_volume_from_geometry(space)

    return 0.0


def get_space_volume_from_geometry(space):
    """Calculate the volume of a space from its geometry."""
    volume = 0.0
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    if hasattr(space, "Representation") and space.Representation:
        try:
            shape = ifcopenshell.geom.create_shape(settings, space)
            if shape:
                # Method 1: Try to get volume directly from shape
                if hasattr(shape.geometry, "volume"):
                    return shape.geometry.volume
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
                            return width * depth * height
        except Exception:
            pass  # Ignore geometry creation errors
    return volume


def get_space_height(space):
    """Get height of a space using multiple methods"""
    # Method 1: From quantity sets
    if hasattr(space, "IsDefinedBy"):
        for rel in space.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                    for qty in rel.RelatingPropertyDefinition.Quantities:
                        if qty.is_a("IfcQuantityLength") and "height" in qty.Name.lower():
                            return qty.LengthValue

    # Method 2: From property sets
    psets = ifcopenshell.util.element.get_psets(space)
    for pset_data in psets.values():
        height = pset_data.get("Height") or pset_data.get("CeilingHeight") or pset_data.get("NetHeight")
        if height:
            return height

    return None


def get_wall_length(wall):
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


def get_wall_direction(wall):
    try:
        if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
            matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
            y_dir = matrix[1][:3]
            angle = math.atan2(y_dir[0], y_dir[1]) * 180 / math.pi
            angle = (angle + 360) % 360
            if 315 <= angle or angle < 45:
                return "North"
            elif 45 <= angle < 135:
                return "East"
            elif 135 <= angle < 225:
                return "South"
            else:
                return "West"
    except Exception:
        pass
    return None


def find_storey_for_element(element, storeys):
    """Find which storey contains an element"""
    if hasattr(element, "ContainedInStructure"):
        for rel in element.ContainedInStructure:
            if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                return rel.RelatingStructure
    return None


def get_spaces_in_storey(storey, spaces):
    """Get all spaces contained in a storey"""
    storey_spaces = []

    for space in spaces:
        if hasattr(space, "ContainedInStructure"):
            for rel in space.ContainedInStructure:
                if rel.RelatingStructure == storey:
                    storey_spaces.append(space)
                    break

    return storey_spaces
