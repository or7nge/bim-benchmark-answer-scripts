import ifcopenshell
from scripts.ifc_utils import get_element_area


def circulation_area(ifc_file_path):
    """Calculate total area of circulation spaces"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        total_circulation_area = 0.0
        circulation_keywords = [
            "corridor",
            "hallway",
            "lobby",
            "foyer",
            "entrance",
            "circulation",
            "passage",
            "walkway",
            "vestibule",
            "atrium",
            "stair",
            "elevator",
        ]

        for space in spaces:
            is_circulation = False

            # Method 1: Check space type/name
            space_name = (space.Name or "").lower()
            space_long_name = (getattr(space, "LongName", "") or "").lower()
            space_type = (getattr(space, "ObjectType", "") or "").lower()

            for keyword in circulation_keywords:
                if keyword in space_name or keyword in space_long_name or keyword in space_type:
                    is_circulation = True
                    break

            # Method 2: Check predefined type
            if not is_circulation and hasattr(space, "PredefinedType"):
                predefined = str(space.PredefinedType).lower()
                if any(keyword in predefined for keyword in circulation_keywords):
                    is_circulation = True

            if is_circulation:
                area = get_element_area(space)
                if area > 0:
                    total_circulation_area += area

        return round(total_circulation_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"
