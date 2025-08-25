import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom


def external_wall_area(ifc_file_path):
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = [w for w in ifc_file.by_type("IfcWall") if hasattr(w, "is_a")]
        total_external_area = 0.0

        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)

        for wall in walls:
            try:
                if not _is_external_wall(wall):
                    continue

                wall_area = 0.0

                # METHOD 1: Try to get area from properties (more accurate)
                psets = ifcopenshell.util.element.get_psets(wall)
                area_keys = ["NetSideArea", "GrossSideArea", "Area", "SideArea"]
                for pset_data in psets.values():
                    for key in area_keys:
                        if key in pset_data and pset_data[key] is not None:
                            try:
                                wall_area = float(pset_data[key])
                                print(wall_area)
                                if wall_area > 0:
                                    break
                            except:
                                continue
                    if wall_area > 0:
                        break

                # METHOD 2: Geometric calculation as fallback
                if wall_area == 0:
                    if hasattr(wall, "Representation") and wall.Representation:
                        shape = ifcopenshell.geom.create_shape(settings, wall)
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
                                    wall_area = max(area1, area2)

                total_external_area += wall_area

            except Exception as e:
                continue

        return round(total_external_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"


def _is_external_wall(wall):
    """Check if a wall is external (simplified heuristic)"""
    # Same external wall detection logic
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
