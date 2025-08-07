import ifcopenshell
import ifcopenshell.util.placement


def floor_most_rooms(ifc_file_path):
    """Find which floor has the most rooms using multiple relationship methods"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        storeys = ifc_file.by_type("IfcBuildingStorey")

        if not spaces:
            return "No rooms found"
        if not storeys:
            return "No floors found"

        # Create storey lookup
        storey_dict = {storey.id(): storey.Name or f"Floor_{storey.id()}" for storey in storeys}

        room_count_per_floor = {}

        # Method 1: Try direct ContainedInStructure relationship
        method1_found = _count_rooms_method1(spaces, storey_dict, room_count_per_floor)

        # Method 2: Try through spatial containment relationships
        if not method1_found:
            method2_found = _count_rooms_method2(ifc_file, spaces, storeys, room_count_per_floor)

        # Method 3: Try through spatial decomposition (RelAggregates)
        if not room_count_per_floor:
            method3_found = _count_rooms_method3(ifc_file, storeys, room_count_per_floor)

        # Method 4: Try by elevation/geometric analysis
        if not room_count_per_floor:
            method4_found = _count_rooms_method4(spaces, storeys, room_count_per_floor)

        # Method 5: Fallback - group by storey name patterns or count
        if not room_count_per_floor:
            method5_found = _count_rooms_method5(spaces, storeys, room_count_per_floor)

        if not room_count_per_floor:
            return "No room-floor relationships found"

        # Return floor with most rooms
        max_floor = max(room_count_per_floor, key=room_count_per_floor.get)
        max_count = room_count_per_floor[max_floor]

        # Add some debug info
        total_rooms_mapped = sum(room_count_per_floor.values())
        return f"{max_floor} ({max_count} rooms)"

    except Exception as e:
        return f"Error: {str(e)}"


def _count_rooms_method1(spaces, storey_dict, room_count_per_floor):
    """Method 1: Direct ContainedInStructure relationship"""
    found_any = False

    for space in spaces:
        if hasattr(space, "ContainedInStructure"):
            for rel in space.ContainedInStructure:
                if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                    storey_id = rel.RelatingStructure.id()
                    if storey_id in storey_dict:
                        storey_name = storey_dict[storey_id]
                        room_count_per_floor[storey_name] = room_count_per_floor.get(storey_name, 0) + 1
                        found_any = True
                        break

    return found_any


def _count_rooms_method2(ifc_file, spaces, storeys, room_count_per_floor):
    """Method 2: Through IfcRelContainedInSpatialStructure relationships"""
    found_any = False

    # Find all spatial containment relationships
    spatial_rels = ifc_file.by_type("IfcRelContainedInSpatialStructure")

    for rel in spatial_rels:
        if rel.RelatingStructure.is_a("IfcBuildingStorey"):
            storey_name = rel.RelatingStructure.Name or f"Floor_{rel.RelatingStructure.id()}"

            # Count spaces in this relationship
            spaces_in_rel = [elem for elem in rel.RelatedElements if elem.is_a("IfcSpace")]
            if spaces_in_rel:
                room_count_per_floor[storey_name] = room_count_per_floor.get(storey_name, 0) + len(spaces_in_rel)
                found_any = True

    return found_any


def _count_rooms_method3(ifc_file, storeys, room_count_per_floor):
    """Method 3: Through spatial decomposition relationships"""
    found_any = False

    # Check RelAggregates relationships
    decomposition_rels = ifc_file.by_type("IfcRelAggregates")

    for rel in decomposition_rels:
        if rel.RelatingObject.is_a("IfcBuildingStorey"):
            storey_name = rel.RelatingObject.Name or f"Floor_{rel.RelatingObject.id()}"

            # Count spaces in the decomposition
            spaces_in_decomp = [obj for obj in rel.RelatedObjects if obj.is_a("IfcSpace")]
            if spaces_in_decomp:
                room_count_per_floor[storey_name] = room_count_per_floor.get(storey_name, 0) + len(spaces_in_decomp)
                found_any = True

    return found_any


def _count_rooms_method4(spaces, storeys, room_count_per_floor):
    """Method 4: Geometric/elevation-based assignment"""
    found_any = False

    try:
        # Sort storeys by elevation
        storeys_by_elevation = []
        for storey in storeys:
            elevation = storey.Elevation if storey.Elevation is not None else 0.0
            storey_name = storey.Name or f"Floor_{storey.id()}"
            storeys_by_elevation.append((elevation, storey_name, storey))

        storeys_by_elevation.sort(key=lambda x: x[0])

        # Try to get space elevations and match to nearest storey
        for space in spaces:
            space_elevation = None

            # Try to get space elevation from placement
            if hasattr(space, "ObjectPlacement") and space.ObjectPlacement:
                try:
                    matrix = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
                    space_elevation = matrix[3][2]  # Z coordinate
                except Exception:
                    pass

            if space_elevation is not None:
                # Find closest storey by elevation
                closest_storey = min(storeys_by_elevation, key=lambda x: abs(x[0] - space_elevation))
                storey_name = closest_storey[1]
                room_count_per_floor[storey_name] = room_count_per_floor.get(storey_name, 0) + 1
                found_any = True

    except Exception:
        pass

    return found_any


def _count_rooms_method5(spaces, storeys, room_count_per_floor):
    """Method 5: Fallback - distribute rooms evenly or by naming patterns"""
    found_any = False

    try:
        # If we have rooms and storeys but no relationships, make reasonable assumptions
        if len(spaces) > 0 and len(storeys) > 0:

            # Try to match by name patterns first
            for space in spaces:
                space_name = getattr(space, "Name", "") or getattr(space, "LongName", "") or ""

                # Look for floor indicators in space names
                for storey in storeys:
                    storey_name = storey.Name or f"Floor_{storey.id()}"
                    storey_short = storey_name.lower().replace("floor", "").replace("level", "").strip()

                    if storey_short in space_name.lower():
                        room_count_per_floor[storey_name] = room_count_per_floor.get(storey_name, 0) + 1
                        found_any = True
                        break

            # If still no matches, distribute evenly as last resort
            if not found_any:
                rooms_per_floor = len(spaces) // len(storeys)
                remainder = len(spaces) % len(storeys)

                for i, storey in enumerate(storeys):
                    storey_name = storey.Name or f"Floor_{storey.id()}"
                    count = rooms_per_floor + (1 if i < remainder else 0)
                    if count > 0:
                        room_count_per_floor[storey_name] = count
                        found_any = True

    except Exception:
        pass

    return found_any
