import ifcopenshell
from scripts.ifc_utils import get_element_area


def vertical_circulation_percentage(ifc_file_path):
    """Calculate percentage of floor area dedicated to vertical circulation"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = list(ifc_file.by_type("IfcSpace"))

        if not spaces:
            return 0.0

        # Calculate total floor area
        total_floor_area = 0.0
        vertical_circulation_area = 0.0

        # Keywords for vertical circulation spaces
        vertical_keywords = ["stair", "elevator", "escalator", "lift", "vertical", "stairwell", "stairway", "staircase", "shaft"]

        for space in spaces:
            try:
                space_area = get_element_area(space)
            except Exception:
                continue
            if not space_area or space_area <= 0:
                continue

            total_floor_area += space_area

            if _is_vertical_circulation_space(space, vertical_keywords):
                vertical_circulation_area += space_area

        if total_floor_area == 0:
            return 0.0

        percentage = (vertical_circulation_area / total_floor_area) * 100
        return round(percentage, 2)

    except Exception as e:
        return f"Error: {str(e)}"


def _is_vertical_circulation_space(space, vertical_keywords):
    """Check if a space is used for vertical circulation"""
    # Check space identifiers
    identifiers = [(space.Name or "").lower(), (getattr(space, "LongName", "") or "").lower(), (getattr(space, "ObjectType", "") or "").lower()]

    for identifier in identifiers:
        if any(keyword in identifier for keyword in vertical_keywords):
            return True

    # Check predefined type
    if hasattr(space, "PredefinedType"):
        predefined = str(space.PredefinedType).lower()
        if any(keyword in predefined for keyword in vertical_keywords):
            return True

    return False
