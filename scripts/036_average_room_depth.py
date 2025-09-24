import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element

from scripts.ifc_utils import get_element_area, get_length_scale


def average_room_depth(ifc_file_path):
    """Calculate average room depth (shortest dimension)"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        total_depth = 0.0
        valid_rooms = 0

        for space in spaces:
            depth = _get_room_depth(space)
            if depth and depth > 0:
                total_depth += depth
                valid_rooms += 1

        if valid_rooms == 0:
            return 0.0

        average_depth = total_depth / valid_rooms
        return round(average_depth, 2)

    except Exception as e:
        return f"Error: {str(e)}"


def _get_room_depth(space):
    """Get the shortest dimension (depth) of a room using multiple methods"""

    # Method 1: From quantity sets (look for Width/Depth/Length properties)
    dimensions = []
    length_scale = get_length_scale(space)

    if hasattr(space, "IsDefinedBy"):
        for rel in space.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                    for qty in rel.RelatingPropertyDefinition.Quantities:
                        if qty.is_a("IfcQuantityLength"):
                            qty_name = qty.Name.lower()
                            if any(keyword in qty_name for keyword in ["width", "depth", "length"]):
                                if getattr(qty, "LengthValue", None):
                                    dimensions.append(float(qty.LengthValue) * length_scale)

    if len(dimensions) >= 2:
        return min(dimensions)  # Return shortest dimension

    # Method 2: From property sets
    try:
        psets = ifcopenshell.util.element.get_psets(space)
        for pset_data in psets.values():
            width = pset_data.get("Width") or pset_data.get("RoomWidth")
            depth = pset_data.get("Depth") or pset_data.get("RoomDepth")
            length = pset_data.get("Length") or pset_data.get("RoomLength")

            room_dims = []
            for value in [width, depth, length]:
                try:
                    if value and float(value) > 0:
                        room_dims.append(float(value) * length_scale)
                except (TypeError, ValueError):
                    continue
            if len(room_dims) >= 2:
                return min(room_dims)
    except Exception:
        pass

    # Method 3: Geometric analysis from representation
    try:
        depth = _calculate_depth_from_geometry(space)
        if depth > 0:
            return depth
    except Exception:
        pass

    # Method 4: Estimate from area and assume square room
    try:
        area = get_element_area(space)
        if area > 0:
            # For square room, depth = sqrt(area)
            estimated_depth = area**0.5
            return estimated_depth
    except Exception:
        pass

    return None


def _calculate_depth_from_geometry(space):
    """Calculate room depth from geometric representation"""
    try:
        if hasattr(space, "Representation") and space.Representation:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)

            shape = ifcopenshell.geom.create_shape(settings, space)
            if shape:
                geometry = shape.geometry
                if hasattr(geometry, "verts"):
                    verts = geometry.verts

                    # Extract X,Y coordinates
                    points = []
                    for i in range(0, len(verts), 3):
                        points.append((verts[i] * length_scale, verts[i + 1] * length_scale))

                    if len(points) >= 4:
                        # Calculate bounding box dimensions
                        min_x = min(p[0] for p in points)
                        max_x = max(p[0] for p in points)
                        min_y = min(p[1] for p in points)
                        max_y = max(p[1] for p in points)

                        width = max_x - min_x
                        height = max_y - min_y

                        return min(width, height)  # Return shorter dimension
    except Exception:
        pass

    return 0.0
