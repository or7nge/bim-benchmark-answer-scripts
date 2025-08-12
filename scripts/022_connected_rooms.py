# scripts/connected_rooms.py - Q022 (Hard)
import ifcopenshell
import ifcopenshell.util.element


def connected_rooms(ifc_file_path):
    """Find which rooms are directly connected to each other"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        doors = ifc_file.by_type("IfcDoor")
        print(f"Found {len(spaces)} spaces, {len(doors)} doors")
        if not spaces:
            return {"error": "No rooms found"}

        connections = {}
        space_dict = {space.id(): space.Name or f"Room_{space.id()}" for space in spaces}

        # Build a map from element id to space(s) via IfcRelSpaceBoundary
        element_to_spaces = {}
        for space in spaces:
            if hasattr(space, "BoundedBy"):
                for boundary in space.BoundedBy:
                    if hasattr(boundary, "RelatedBuildingElement") and boundary.RelatedBuildingElement:
                        el = boundary.RelatedBuildingElement
                        if el.id() not in element_to_spaces:
                            element_to_spaces[el.id()] = set()
                        element_to_spaces[el.id()].add(space)
        print(f"element_to_spaces mapping (element id -> [space names]):")
        for elid, sp_set in element_to_spaces.items():
            print(f"  {elid}: {[space_dict[s.id()] for s in sp_set]}")

        # Print door relationships for first 3 doors
        for door in doors[:3]:
            print(f"Door id {door.id()} name {getattr(door, 'Name', None)}")
            print(f"  FillsVoids: {getattr(door, 'FillsVoids', None)}")
            print(f"  ConnectedTo: {getattr(door, 'ConnectedTo', None)}")
            print(f"  ConnectedFrom: {getattr(door, 'ConnectedFrom', None)}")

        import math
        import numpy as np

        def get_centroid(obj):
            # Try to get the centroid from the ObjectPlacement
            if hasattr(obj, "ObjectPlacement") and obj.ObjectPlacement:
                try:
                    placement = obj.ObjectPlacement
                    if hasattr(placement, "RelativePlacement") and placement.RelativePlacement:
                        loc = placement.RelativePlacement.Location
                        if hasattr(loc, "Coordinates"):
                            coords = loc.Coordinates
                            centroid = tuple(float(c) for c in coords)
                            if centroid != (0.0, 0.0, 0.0):
                                print(f"Centroid for {getattr(obj, 'Name', obj.id())}: {centroid}")
                                return centroid
                except Exception as e:
                    print(f"Error getting centroid for {getattr(obj, 'Name', obj.id())}: {e}")
            # Fallback: Try to get centroid from geometry representation
            if hasattr(obj, "Representation") and obj.Representation:
                try:
                    reps = obj.Representation.Representations
                    for rep in reps:
                        if hasattr(rep, "Items"):
                            points = []
                            for item in rep.Items:
                                if hasattr(item, "Points") and item.Points:
                                    for p in item.Points:
                                        pt = tuple(float(x) for x in p.Coordinates)
                                        points.append(pt)
                                elif hasattr(item, "Coordinates") and item.Coordinates:
                                    pt = tuple(float(x) for x in item.Coordinates)
                                    points.append(pt)
                            if points:
                                arr = np.array(points)
                                centroid = tuple(np.mean(arr, axis=0))
                                print(f"[Geom] Centroid for {getattr(obj, 'Name', obj.id())}: {centroid}")
                                return centroid
                except Exception as e:
                    print(f"Error getting centroid from geometry for {getattr(obj, 'Name', obj.id())}: {e}")
            return None

        # Check if all space centroids are (0,0,0) or None
        space_centroids_list = [get_centroid(space) for space in spaces]
        if all(c is None or c == (0.0, 0.0, 0.0) for c in space_centroids_list):
            print("Warning: All space centroids are (0,0,0) or missing. Cannot infer room connections.")
            return {"error": "No valid space placement or geometry found in IFC. Room connections cannot be determined."}

        # For each door, find the spaces it connects (via walls or directly)
        for door in doors:
            connected_spaces = set()
            # 1. Spaces directly bounded by the door
            if door.id() in element_to_spaces:
                connected_spaces.update(element_to_spaces[door.id()])

            # 2. Spaces bounded by walls that are connected to this door (via IfcRelConnectsElements)
            if hasattr(door, "ConnectedTo"):
                for rel in door.ConnectedTo:
                    if hasattr(rel, "RelatedElement") and rel.RelatedElement:
                        wall = rel.RelatedElement
                        if wall.id() in element_to_spaces:
                            connected_spaces.update(element_to_spaces[wall.id()])
            if hasattr(door, "ConnectedFrom"):
                for rel in door.ConnectedFrom:
                    if hasattr(rel, "RelatingElement") and rel.RelatingElement:
                        wall = rel.RelatingElement
                        if wall.id() in element_to_spaces:
                            connected_spaces.update(element_to_spaces[wall.id()])

            # 3. Fallback: Use FillsVoids to find host wall, then spaces bounded by that wall
            if hasattr(door, "FillsVoids"):
                for rel in door.FillsVoids:
                    if hasattr(rel, "RelatingBuildingElement") and rel.RelatingBuildingElement:
                        wall = rel.RelatingBuildingElement
                        if wall.id() in element_to_spaces:
                            connected_spaces.update(element_to_spaces[wall.id()])

            # 4. Geometric fallback: find two closest spaces by centroid
            if len(connected_spaces) < 2:
                door_centroid = get_centroid(door)
                if door_centroid:
                    space_centroids = [(space, get_centroid(space)) for space in spaces]
                    space_centroids = [(s, c) for s, c in space_centroids if c]
                    # Compute distances
                    dists = [(s, math.dist(door_centroid, c)) for s, c in space_centroids]
                    dists.sort(key=lambda x: x[1])
                    print(f"Door {getattr(door, 'Name', door.id())} centroid: {door_centroid}")
                    for idx, (s, dist) in enumerate(dists[:5]):
                        print(f"  Closest space {idx+1}: {getattr(s, 'Name', s.id())}, dist={dist}")
                    # Use a threshold (e.g., 30 meters) to avoid spurious matches
                    if len(dists) >= 2 and dists[0][1] < 30 and dists[1][1] < 30:
                        connected_spaces = [dists[0][0], dists[1][0]]

            # If two or more spaces found, connect them
            connected_spaces = list(connected_spaces)
            if len(connected_spaces) >= 2:
                for i, space1 in enumerate(connected_spaces):
                    for space2 in connected_spaces[i + 1 :]:
                        name1 = space_dict[space1.id()]
                        name2 = space_dict[space2.id()]
                        if name1 not in connections:
                            connections[name1] = set()
                        if name2 not in connections:
                            connections[name2] = set()
                        connections[name1].add(name2)
                        connections[name2].add(name1)

        # Optionally: repeat for openings (less reliable, but can help)
        openings = ifc_file.by_type("IfcOpeningElement")
        for opening in openings:
            connected_spaces = set()
            if opening.id() in element_to_spaces:
                connected_spaces.update(element_to_spaces[opening.id()])
            connected_spaces = list(connected_spaces)
            if len(connected_spaces) >= 2:
                for i, space1 in enumerate(connected_spaces):
                    for space2 in connected_spaces[i + 1 :]:
                        name1 = space_dict[space1.id()]
                        name2 = space_dict[space2.id()]
                        if name1 not in connections:
                            connections[name1] = set()
                        if name2 not in connections:
                            connections[name2] = set()
                        connections[name1].add(name2)
                        connections[name2].add(name1)

        # Convert sets to lists for JSON serialization
        result = {room: list(connected) for room, connected in connections.items()}
        return result if result else {"message": "No room connections found"}
    except Exception as e:
        return f"Error: {str(e)}"


def _find_spaces_connected_by_element(element, spaces):
    """Find spaces that are connected by a door or opening"""
    connected_spaces = []

    # Check which spaces contain this element
    for space in spaces:
        if hasattr(space, "BoundedBy"):
            for boundary in space.BoundedBy:
                if hasattr(boundary, "RelatedBuildingElement"):
                    if boundary.RelatedBuildingElement == element:
                        connected_spaces.append(space)
                        break

    return connected_spaces
