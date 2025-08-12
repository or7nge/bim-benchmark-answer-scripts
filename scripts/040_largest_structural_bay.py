import ifcopenshell
import ifcopenshell.util.placement
import itertools


def largest_structural_bay(ifc_file_path):
    """Find which structural bay has the largest area"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        columns = ifc_file.by_type("IfcColumn")
        beams = ifc_file.by_type("IfcBeam")

        if len(columns) < 4:  # Need at least 4 columns to define a bay
            return "Insufficient structural elements to determine bays"

        # Method 1: Analyze column grid to find structural bays
        bays = _analyze_structural_grid(columns)
        if bays:
            largest_bay = max(bays, key=lambda x: x["area"])
            return f"Bay {largest_bay['name']} ({largest_bay['area']:.1f} sq units)"

        # Method 2: Use beam-column intersections to define bays
        bays = _analyze_beam_column_grid(columns, beams)
        if bays:
            largest_bay = max(bays, key=lambda x: x["area"])
            return f"Bay {largest_bay['name']} ({largest_bay['area']:.1f} sq units)"

        # Method 3: Simple rectangular grid assumption
        bay_area = _estimate_typical_bay_area(columns)
        if bay_area > 0:
            return f"Typical structural bay ({bay_area:.1f} sq units)"

        return "No structural bays identified"

    except Exception as e:
        return f"Error: {str(e)}"


def _analyze_structural_grid(columns):
    """Analyze column positions to identify structural bays"""
    try:
        # Get column positions
        column_positions = []
        for column in columns:
            pos = _get_element_position(column)
            if pos:
                column_positions.append(pos)

        if len(column_positions) < 4:
            return []

        # Group columns by similar X and Y coordinates to find grid lines
        x_coords = [pos[0] for pos in column_positions]
        y_coords = [pos[1] for pos in column_positions]

        # Find unique grid lines (with tolerance)
        tolerance = 1.0  # 1 unit tolerance for grid alignment
        x_grid_lines = _find_grid_lines(x_coords, tolerance)
        y_grid_lines = _find_grid_lines(y_coords, tolerance)

        if len(x_grid_lines) < 2 or len(y_grid_lines) < 2:
            return []

        # Generate bays from grid intersections
        bays = []
        for i in range(len(x_grid_lines) - 1):
            for j in range(len(y_grid_lines) - 1):
                x1, x2 = x_grid_lines[i], x_grid_lines[i + 1]
                y1, y2 = y_grid_lines[j], y_grid_lines[j + 1]

                width = abs(x2 - x1)
                height = abs(y2 - y1)
                area = width * height

                if area > 1.0:  # Minimum area threshold
                    bay_name = f"{chr(65+i)}{j+1}"  # A1, B1, etc.
                    bays.append({"name": bay_name, "area": area, "bounds": (x1, y1, x2, y2)})

        return bays

    except Exception:
        return []


def _analyze_beam_column_grid(columns, beams):
    """Use beam-column relationships to identify bays"""
    try:
        if not beams:
            return []

        # This is a simplified approach
        # Real implementation would analyze beam connectivity
        column_positions = []
        for column in columns:
            pos = _get_element_position(column)
            if pos:
                column_positions.append(pos)

        beam_positions = []
        for beam in beams:
            pos = _get_element_position(beam)
            if pos:
                beam_positions.append(pos)

        # Simple rectangular bay estimation
        if len(column_positions) >= 4 and len(beam_positions) >= 2:
            min_x = min(pos[0] for pos in column_positions)
            max_x = max(pos[0] for pos in column_positions)
            min_y = min(pos[1] for pos in column_positions)
            max_y = max(pos[1] for pos in column_positions)

            # Estimate typical bay size
            total_width = max_x - min_x
            total_height = max_y - min_y

            # Assume 2x2 grid minimum
            num_x_bays = max(2, len(set(round(pos[0]) for pos in column_positions)) - 1)
            num_y_bays = max(2, len(set(round(pos[1]) for pos in column_positions)) - 1)

            bay_width = total_width / num_x_bays
            bay_height = total_height / num_y_bays
            bay_area = bay_width * bay_height

            return [{"name": "Typical Bay", "area": bay_area, "bounds": (min_x, min_y, min_x + bay_width, min_y + bay_height)}]

        return []

    except Exception:
        return []


def _get_element_position(element):
    """Get X,Y position of a structural element"""
    try:
        if hasattr(element, "ObjectPlacement") and element.ObjectPlacement:
            matrix = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
            return (matrix[3][0], matrix[3][1])  # X, Y coordinates
    except Exception:
        pass
    return None


def _find_grid_lines(coordinates, tolerance):
    """Find unique grid lines from a list of coordinates"""
    if not coordinates:
        return []

    sorted_coords = sorted(coordinates)
    grid_lines = [sorted_coords[0]]

    for coord in sorted_coords[1:]:
        if abs(coord - grid_lines[-1]) > tolerance:
            grid_lines.append(coord)

    return grid_lines


def _estimate_typical_bay_area(columns):
    """Estimate typical structural bay area from column spacing"""
    try:
        if len(columns) < 4:
            return 0.0

        column_positions = []
        for column in columns:
            pos = _get_element_position(column)
            if pos:
                column_positions.append(pos)

        if len(column_positions) < 4:
            return 0.0

        # Calculate distances between adjacent columns
        distances = []
        for i, pos1 in enumerate(column_positions):
            for pos2 in column_positions[i + 1 :]:
                distance = ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
                if 2.0 < distance < 50.0:  # Reasonable structural bay range
                    distances.append(distance)

        if distances:
            avg_spacing = sum(distances) / len(distances)
            # Assume square bays for simplification
            typical_area = avg_spacing**2
            return typical_area

        return 0.0

    except Exception:
        return 0.0
