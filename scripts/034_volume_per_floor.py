import ifcopenshell
import ifcopenshell.util.placement
from scripts.ifc_utils import get_space_volume


def volume_per_floor(ifc_file_path):
    """Calculate total volume of enclosed spaces per floor using multiple relationship methods"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        storeys = ifc_file.by_type("IfcBuildingStorey")

        if not spaces:
            return {"error": "No rooms (IfcSpace) found"}
        if not storeys:
            return {"error": "No floors (IfcBuildingStorey) found"}

        # Create storey lookup
        storey_dict = {storey.id(): storey.Name or f"Floor_{storey.id()}" for storey in storeys}

        # Dictionary to hold spaces per storey
        spaces_per_storey = {name: [] for name in storey_dict.values()}

        # Start with all spaces as unassigned
        unassigned_spaces = list(spaces)

        # Method 1: Try direct ContainedInStructure relationship
        unassigned_spaces = _get_spaces_method1(unassigned_spaces, storey_dict, spaces_per_storey)

        # Method 2: Try through spatial containment relationships
        if unassigned_spaces:
            unassigned_spaces = _get_spaces_method2(ifc_file, unassigned_spaces, storey_dict, spaces_per_storey)

        # Method 3: Try through spatial decomposition (RelAggregates)
        if unassigned_spaces:
            unassigned_spaces = _get_spaces_method3(ifc_file, unassigned_spaces, storey_dict, spaces_per_storey)

        # Method 4: Try by elevation/geometric analysis
        if unassigned_spaces:
            _get_spaces_method4(unassigned_spaces, storeys, spaces_per_storey)

        # Calculate volumes
        floor_volumes = {}
        for storey_name, storey_spaces in spaces_per_storey.items():
            total_volume = 0.0
            for space in storey_spaces:
                volume = get_space_volume(space)
                if volume > 0:
                    total_volume += volume

            if total_volume > 0:
                floor_volumes[storey_name] = round(total_volume, 2)

        return floor_volumes if floor_volumes else {"message": "No volumes calculated for any floor"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


def _get_spaces_method1(spaces, storey_dict, spaces_per_storey):
    """Method 1: Direct ContainedInStructure relationship"""
    assigned_space_ids = set()
    for space in spaces:
        if hasattr(space, "ContainedInStructure"):
            for rel in space.ContainedInStructure:
                if rel.RelatingStructure.is_a("IfcBuildingStorey"):
                    storey_id = rel.RelatingStructure.id()
                    if storey_id in storey_dict:
                        storey_name = storey_dict[storey_id]
                        spaces_per_storey[storey_name].append(space)
                        assigned_space_ids.add(space.id())
                        break  # Move to next space once assigned
    return [s for s in spaces if s.id() not in assigned_space_ids]


def _get_spaces_method2(ifc_file, spaces, storey_dict, spaces_per_storey):
    """Method 2: Through IfcRelContainedInSpatialStructure relationships"""
    assigned_space_ids = set()
    space_ids_to_check = {s.id() for s in spaces}

    spatial_rels = ifc_file.by_type("IfcRelContainedInSpatialStructure")
    for rel in spatial_rels:
        if rel.RelatingStructure.is_a("IfcBuildingStorey"):
            storey_id = rel.RelatingStructure.id()
            if storey_id in storey_dict:
                storey_name = storey_dict[storey_id]
                for elem in rel.RelatedElements:
                    if elem.is_a("IfcSpace") and elem.id() in space_ids_to_check:
                        spaces_per_storey[storey_name].append(elem)
                        assigned_space_ids.add(elem.id())

    return [s for s in spaces if s.id() not in assigned_space_ids]


def _get_spaces_method3(ifc_file, spaces, storey_dict, spaces_per_storey):
    """Method 3: Through spatial decomposition relationships (IfcRelAggregates)"""
    assigned_space_ids = set()
    space_ids_to_check = {s.id() for s in spaces}

    decomposition_rels = ifc_file.by_type("IfcRelAggregates")
    for rel in decomposition_rels:
        if rel.RelatingObject.is_a("IfcBuildingStorey"):
            storey_id = rel.RelatingObject.id()
            if storey_id in storey_dict:
                storey_name = storey_dict[storey_id]
                for obj in rel.RelatedObjects:
                    if obj.is_a("IfcSpace") and obj.id() in space_ids_to_check:
                        spaces_per_storey[storey_name].append(obj)
                        assigned_space_ids.add(obj.id())

    return [s for s in spaces if s.id() not in assigned_space_ids]


def _get_spaces_method4(spaces, storeys, spaces_per_storey):
    """Method 4: Geometric/elevation-based assignment"""
    try:
        storeys_by_elevation = []
        for storey in storeys:
            elevation = storey.Elevation if storey.Elevation is not None else 0.0
            storey_name = storey.Name or f"Floor_{storey.id()}"
            storeys_by_elevation.append((elevation, storey_name))

        if not storeys_by_elevation:
            return

        storeys_by_elevation.sort(key=lambda x: x[0])

        for space in spaces:
            space_elevation = None
            if hasattr(space, "ObjectPlacement") and space.ObjectPlacement:
                try:
                    matrix = ifcopenshell.util.placement.get_local_placement(space.ObjectPlacement)
                    space_elevation = matrix[2][3]  # Z coordinate from 4x4 matrix
                except Exception:
                    continue

            if space_elevation is not None:
                # Find closest storey by elevation
                closest_storey = min(storeys_by_elevation, key=lambda x: abs(x[0] - space_elevation))
                storey_name = closest_storey[1]
                spaces_per_storey[storey_name].append(space)
    except Exception:
        # This method is a fallback, so we don't want to fail the whole script
        pass
