import ifcopenshell


def count_structural_elements(ifc_file_path):
    """Count all structural elements (beams + columns + load-bearing walls)"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Direct structural elements
        beams = ifc_file.by_type("IfcBeam")
        columns = ifc_file.by_type("IfcColumn")
        structural_members = ifc_file.by_type("IfcStructuralMember")

        count = len(beams) + len(columns) + len(structural_members)

        # Check walls for structural/load-bearing ones
        walls = ifc_file.by_type("IfcWall")
        structural_walls = 0

        for wall in walls:
            is_structural = False

            # Check if wall is load-bearing
            if hasattr(wall, "PredefinedType"):
                predefined = str(wall.PredefinedType).upper()
                if "LOADBEARING" in predefined or "STRUCTURAL" in predefined:
                    is_structural = True

            # Check property sets
            if not is_structural:
                psets = ifcopenshell.util.element.get_psets(wall)
                for pset_data in psets.values():
                    load_bearing = pset_data.get("LoadBearing") or pset_data.get("IsLoadBearing")
                    if load_bearing:
                        is_structural = True
                        break

            if is_structural:
                structural_walls += 1

        return count + structural_walls

    except Exception as e:
        return f"Error: {str(e)}"
