import ifcopenshell
import ifcopenshell.util.element


def window_to_wall_ratio(ifc_file_path):
    """Calculate ratio of window area to wall area"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        windows = ifc_file.by_type("IfcWindow")
        walls = ifc_file.by_type("IfcWall")

        total_window_area = 0.0
        total_wall_area = 0.0

        # Calculate window areas
        for window in windows:
            psets = ifcopenshell.util.element.get_psets(window)
            for pset_name, pset_data in psets.items():
                area = pset_data.get("Area") or pset_data.get("OverallArea")
                if area:
                    total_window_area += float(area)
                    break
            else:
                # Fallback: estimate from width x height if available
                if hasattr(window, "OverallWidth") and hasattr(window, "OverallHeight"):
                    if window.OverallWidth and window.OverallHeight:
                        total_window_area += window.OverallWidth * window.OverallHeight

        # Calculate wall areas
        for wall in walls:
            psets = ifcopenshell.util.element.get_psets(wall)
            for pset_name, pset_data in psets.items():
                area = pset_data.get("NetSideArea") or pset_data.get("GrossArea") or pset_data.get("Area")
                if area:
                    total_wall_area += float(area)
                    break

        if total_wall_area == 0:
            return 0.0

        ratio = total_window_area / total_wall_area
        return round(ratio, 3)

    except Exception as e:
        return f"Error: {str(e)}"
