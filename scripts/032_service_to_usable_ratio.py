import ifcopenshell
import ifcopenshell.util.element


def service_to_usable_ratio(ifc_file_path):
    """Calculate ratio of service spaces to usable spaces"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        service_area = 0.0
        usable_area = 0.0

        service_keywords = [
            "mechanical",
            "electrical",
            "janitor",
            "storage",
            "utility",
            "server",
            "equipment",
            "maintenance",
            "service",
            "technical",
            "hvac",
            "boiler",
            "elevator",
            "stair",
            "restroom",
            "bathroom",
        ]

        for space in spaces:
            area = _get_space_area(space)
            if area <= 0:
                continue

            is_service = False

            # Check space identifiers
            identifiers = [
                (space.Name or "").lower(),
                (getattr(space, "LongName", "") or "").lower(),
                (getattr(space, "ObjectType", "") or "").lower(),
            ]

            for identifier in identifiers:
                if any(keyword in identifier for keyword in service_keywords):
                    is_service = True
                    break

            if is_service:
                service_area += area
            else:
                usable_area += area

        if usable_area == 0:
            return 0.0

        ratio = service_area / usable_area
        return round(ratio, 3)

    except Exception as e:
        return f"Error: {str(e)}"


# Helper function stub
def _get_space_area(space):
    # ...existing code...
    pass
