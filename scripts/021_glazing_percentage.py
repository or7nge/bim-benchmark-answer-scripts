import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.geom


def glazing_percentage(ifc_file_path):
    """Calculate percentage of building that is glazed (windows vs walls)"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Get total window area using multiple methods
        total_window_area = _calculate_total_window_area(ifc_file)

        # Get total wall area using multiple methods
        total_wall_area = _calculate_total_wall_area(ifc_file)

        if total_wall_area == 0:
            return 0.0

        glazing_ratio = (total_window_area / total_wall_area) * 100
        return round(glazing_ratio, 2)

    except Exception as e:
        return f"Error: {str(e)}"


def _calculate_total_window_area(ifc_file):
    """Calculate total window area with multiple fallback methods"""
    windows = ifc_file.by_type("IfcWindow")
    curtain_walls = ifc_file.by_type("IfcCurtainWall")

    total_area = 0.0

    # Method 1: From window properties
    for window in windows:
        area = None

        # Try quantity sets first
        if hasattr(window, "IsDefinedBy"):
            for rel in window.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                        for qty in rel.RelatingPropertyDefinition.Quantities:
                            if qty.is_a("IfcQuantityArea"):
                                area = qty.AreaValue
                                break
                if area:
                    break

        # Try property sets
        if not area:
            psets = ifcopenshell.util.element.get_psets(window)
            for pset_data in psets.values():
                area = pset_data.get("Area") or pset_data.get("OverallArea") or pset_data.get("GlazingArea")
                if area:
                    break

        # Try geometric calculation from dimensions
        if not area:
            width = getattr(window, "OverallWidth", None)
            height = getattr(window, "OverallHeight", None)
            if width and height:
                area = width * height

        if area and area > 0:
            total_area += area

    # Add curtain wall areas (fully glazed)
    for curtain_wall in curtain_walls:
        area = _get_element_area(curtain_wall)
        if area > 0:
            total_area += area

    return total_area


def _calculate_total_wall_area(ifc_file):
    """Calculate total wall area with multiple methods"""
    walls = ifc_file.by_type("IfcWall")
    total_area = 0.0

    for wall in walls:
        area = _get_element_area(wall)
        if area > 0:
            total_area += area

    return total_area


def _get_element_area(element):
    """Generic function to get area from any IFC element"""
    area = None

    # Method 1: Quantity sets
    if hasattr(element, "IsDefinedBy"):
        for rel in element.IsDefinedBy:
            if rel.is_a("IfcRelDefinesByProperties"):
                if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                    for qty in rel.RelatingPropertyDefinition.Quantities:
                        if qty.is_a("IfcQuantityArea"):
                            area = qty.AreaValue
                            break
            if area:
                break

    # Method 2: Property sets
    if not area:
        psets = ifcopenshell.util.element.get_psets(element)
        for pset_data in psets.values():
            area = pset_data.get("NetSideArea") or pset_data.get("GrossArea") or pset_data.get("Area") or pset_data.get("NetArea")
            if area:
                break

    return area if area else 0.0
