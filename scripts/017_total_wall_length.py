import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.placement
import math


def total_wall_length(ifc_file_path):
    """Calculate total length of all walls - simplified approach"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = ifc_file.by_type("IfcWall")

        if not walls:
            return 0.0

        total_length = 0.0
        processed_walls = 0

        for wall in walls:
            wall_length = None

            # Method 1: Check BaseQuantities first (most reliable)
            try:
                if hasattr(wall, "IsDefinedBy"):
                    for rel in wall.IsDefinedBy:
                        if rel.is_a("IfcRelDefinesByProperties"):
                            if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                                quantities = rel.RelatingPropertyDefinition.Quantities
                                for qty in quantities:
                                    if qty.is_a("IfcQuantityLength"):
                                        if any(keyword in qty.Name.lower() for keyword in ["length", "gross", "net"]):
                                            wall_length = qty.LengthValue
                                            break
                                if wall_length:
                                    break
                        if wall_length:
                            break
            except Exception:
                pass

            # Method 2: Try property sets
            if wall_length is None:
                try:
                    psets = ifcopenshell.util.element.get_psets(wall)
                    for pset_data in psets.values():
                        for key in ["Length", "NetLength", "GrossLength", "OverallLength"]:
                            if key in pset_data and pset_data[key]:
                                wall_length = float(pset_data[key])
                                break
                        if wall_length:
                            break
                except Exception:
                    pass

            # Method 3: Estimate from wall axis (if ObjectPlacement exists)
            if wall_length is None:
                try:
                    if hasattr(wall, "ObjectPlacement") and wall.ObjectPlacement:
                        # This is a very simplified approach
                        # In real scenarios, you'd need to parse the wall's axis curve
                        # For now, we'll try to get some default length

                        # Check if wall has representation with swept area
                        if hasattr(wall, "Representation") and wall.Representation:
                            for rep in wall.Representation.Representations:
                                for item in rep.Items:
                                    if item.is_a("IfcExtrudedAreaSolid"):
                                        # Depth often represents the wall length for extruded walls
                                        if hasattr(item, "Depth") and item.Depth > 0:
                                            wall_length = item.Depth
                                            break
                                if wall_length:
                                    break
                except Exception:
                    pass

            # Add to total if we found a length
            if wall_length is not None and wall_length > 0:
                total_length += wall_length
                processed_walls += 1

        return round(total_length, 2)

    except Exception as e:
        return f"Error: {str(e)}"
