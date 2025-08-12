import ifcopenshell
import ifcopenshell.util.placement
import math


def window_orientation(ifc_file_path):
    """Determine which direction most windows face"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        windows = ifc_file.by_type("IfcWindow")

        if not windows:
            return "No windows found"

        orientations = {"North": 0, "South": 0, "East": 0, "West": 0}

        for window in windows:
            if hasattr(window, "ObjectPlacement") and window.ObjectPlacement:
                try:
                    # Get placement matrix
                    matrix = ifcopenshell.util.placement.get_local_placement(window.ObjectPlacement)

                    # Extract the Y direction (typically the facing direction for windows)
                    y_dir = matrix[1][:3]  # Y-axis direction vector

                    # Calculate angle from north (assuming Y+ is north)
                    angle = math.atan2(y_dir[0], y_dir[1]) * 180 / math.pi
                    angle = (angle + 360) % 360  # Normalize to 0-360

                    # Classify direction
                    if 315 <= angle or angle < 45:
                        orientations["North"] += 1
                    elif 45 <= angle < 135:
                        orientations["East"] += 1
                    elif 135 <= angle < 225:
                        orientations["South"] += 1
                    else:
                        orientations["West"] += 1

                except:
                    continue

        # Return the direction with most windows
        max_direction = max(orientations, key=orientations.get)
        return max_direction if orientations[max_direction] > 0 else "Undetermined"

    except Exception as e:
        return f"Error: {str(e)}"
