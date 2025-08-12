# scripts/building_footprint.py - Q019 (Hard)
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom
import ifcopenshell.util.placement
from collections import defaultdict


def building_footprint(ifc_file_path):
    """Calculate building's footprint area using multiple methods"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Method 1: Try to find ground floor slabs first
        footprint_area = _get_footprint_from_slabs(ifc_file)
        if footprint_area > 0:
            return round(footprint_area, 2)

        # Method 2: Sum all space areas on the lowest floor
        footprint_area = _get_footprint_from_spaces(ifc_file)
        if footprint_area > 0:
            return round(footprint_area, 2)

        # Method 3: Calculate from wall footprints on ground floor
        footprint_area = _get_footprint_from_walls(ifc_file)
        if footprint_area > 0:
            return round(footprint_area, 2)

        # Method 4: Geometric calculation - project all building elements to 2D
        footprint_area = _get_footprint_from_geometry(ifc_file)
        return round(footprint_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"


def _get_footprint_from_slabs(ifc_file):
    """Method 1: Get footprint from ground floor slabs"""
    try:
        slabs = ifc_file.by_type("IfcSlab")
        ground_floor_area = 0.0

        for slab in slabs:
            # Check if this is a floor slab (not roof, etc.)
            predefined_type = getattr(slab, "PredefinedType", None)
            if predefined_type and "FLOOR" in str(predefined_type).upper():
                # Try quantity sets first
                if hasattr(slab, "IsDefinedBy"):
                    for rel in slab.IsDefinedBy:
                        if rel.is_a("IfcRelDefinesByProperties"):
                            if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                                for qty in rel.RelatingPropertyDefinition.Quantities:
                                    if qty.is_a("IfcQuantityArea"):
                                        ground_floor_area += qty.AreaValue
                                        break
                        if ground_floor_area > 0:
                            break

                # Try property sets
                if ground_floor_area == 0:
                    psets = ifcopenshell.util.element.get_psets(slab)
                    for pset_name, pset_data in psets.items():
                        area = pset_data.get("NetArea") or pset_data.get("GrossArea") or pset_data.get("Area")
                        if area:
                            ground_floor_area += float(area)
                            break

        return ground_floor_area
    except Exception:
        return 0.0


def _get_footprint_from_spaces(ifc_file):
    """Method 2: Get footprint from spaces on lowest floor"""
    try:
        storeys = ifc_file.by_type("IfcBuildingStorey")
        if not storeys:
            return 0.0

        # Find lowest storey by elevation
        lowest_storey = None
        min_elevation = float("inf")

        for storey in storeys:
            if storey.Elevation is not None:
                if storey.Elevation < min_elevation:
                    min_elevation = storey.Elevation
                    lowest_storey = storey

        if not lowest_storey:
            # If no elevation data, take first storey
            lowest_storey = storeys[0]

        spaces = ifc_file.by_type("IfcSpace")
        footprint_area = 0.0

        for space in spaces:
            if hasattr(space, "ContainedInStructure"):
                for rel in space.ContainedInStructure:
                    if rel.RelatingStructure == lowest_storey:
                        # Try quantity sets first
                        if hasattr(space, "IsDefinedBy"):
                            for rel_def in space.IsDefinedBy:
                                if rel_def.is_a("IfcRelDefinesByProperties"):
                                    if rel_def.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                                        for qty in rel_def.RelatingPropertyDefinition.Quantities:
                                            if qty.is_a("IfcQuantityArea"):
                                                footprint_area += qty.AreaValue
                                                break

                        # Try property sets if no quantity found
                        if footprint_area == 0:
                            psets = ifcopenshell.util.element.get_psets(space)
                            for pset_name, pset_data in psets.items():
                                area = pset_data.get("FloorArea") or pset_data.get("Area") or pset_data.get("NetFloorArea")
                                if area:
                                    footprint_area += float(area)
                                    break
                        break

        return footprint_area
    except Exception:
        return 0.0


def _get_footprint_from_walls(ifc_file):
    """Method 3: Calculate footprint from wall positions (simplified)"""
    try:
        walls = ifc_file.by_type("IfcWall")
        if not walls:
            return 0.0

        # Get wall coordinates and try to estimate footprint
        wall_points = []

        for wall in walls:
            if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
                try:
                    matrix = ifcopenshell.util.placement.get_local_placement(wall.ObjectPlacement)
                    # Extract X,Y coordinates (ignore Z for footprint)
                    x, y = matrix[3][0], matrix[3][1]  # Translation components
                    wall_points.append((x, y))
                except Exception:
                    continue

        if len(wall_points) < 3:
            return 0.0

        # Simple bounding rectangle calculation
        min_x = min(p[0] for p in wall_points)
        max_x = max(p[0] for p in wall_points)
        min_y = min(p[1] for p in wall_points)
        max_y = max(p[1] for p in wall_points)

        # Calculate rectangular footprint area
        area = (max_x - min_x) * (max_y - min_y)
        return area if area > 0 else 0.0

    except Exception:
        return 0.0


def _get_footprint_from_geometry(ifc_file):
    """Method 4: Calculate footprint from actual 3D geometry"""
    try:
        # Get building elements that contribute to footprint
        elements = []
        elements.extend(ifc_file.by_type("IfcWall"))
        elements.extend(ifc_file.by_type("IfcSlab"))
        elements.extend(ifc_file.by_type("IfcColumn"))

        if not elements:
            return 0.0

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)

        all_points = []

        for element in elements:
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
                if shape:
                    geometry = shape.geometry
                    if hasattr(geometry, "verts"):
                        verts = geometry.verts
                        # Extract X,Y coordinates (project to ground plane)
                        for i in range(0, len(verts), 3):
                            x, y = verts[i], verts[i + 1]
                            all_points.append((x, y))
            except Exception:
                continue

        if len(all_points) < 3:
            return 0.0

        # Calculate bounding rectangle area
        min_x = min(p[0] for p in all_points)
        max_x = max(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_y = max(p[1] for p in all_points)

        area = (max_x - min_x) * (max_y - min_y)
        return area if area > 0 else 0.0

    except Exception:
        return 0.0
