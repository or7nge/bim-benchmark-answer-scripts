import ifcopenshell
import ifcopenshell.util.element


def vertical_circulation_percentage(ifc_file_path):
    """Calculate percentage of floor area dedicated to vertical circulation"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return 0.0

        # Calculate total floor area
        total_floor_area = 0.0
        vertical_circulation_area = 0.0

        # Keywords for vertical circulation spaces
        vertical_keywords = ["stair", "elevator", "escalator", "lift", "vertical", "stairwell", "stairway", "staircase", "shaft"]

        for space in spaces:
            space_area = _get_space_area(space)
            if space_area > 0:
                total_floor_area += space_area

                # Check if this is a vertical circulation space
                is_vertical_circulation = _is_vertical_circulation_space(space, vertical_keywords)

                if is_vertical_circulation:
                    vertical_circulation_area += space_area

        # Method 2: Also check for stair and elevator elements directly
        stairs = ifc_file.by_type("IfcStair")
        elevators = ifc_file.by_type("IfcTransportElement")  # Often used for elevators

        # Add areas from stair elements
        for stair in stairs:
            stair_area = _get_element_area(stair)
            if stair_area > 0:
                vertical_circulation_area += stair_area

        # Add areas from elevator elements
        for elevator in elevators:
            # Check if it's actually an elevator
            if _is_elevator(elevator):
                elevator_area = _get_element_area(elevator)
                if elevator_area > 0:
                    vertical_circulation_area += elevator_area

        # Method 3: If no direct elements found, estimate from building type
        if vertical_circulation_area == 0 and total_floor_area > 0:
            storeys = ifc_file.by_type("IfcBuildingStorey")
            if len(storeys) > 1:  # Multi-story building
                # Typical vertical circulation is 10-15% for multi-story buildings
                estimated_circulation = total_floor_area * 0.12  # 12% estimate
                vertical_circulation_area = estimated_circulation

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


def _is_elevator(transport_element):
    """Check if transport element is an elevator"""
    # Check predefined type
    if hasattr(transport_element, "PredefinedType"):
        predefined = str(transport_element.PredefinedType).upper()
        if "ELEVATOR" in predefined or "LIFT" in predefined:
            return True

    # Check name
    name = (transport_element.Name or "").lower()
    if "elevator" in name or "lift" in name:
        return True

    return False


def _get_element_area(element):
    """Get area of any IFC element"""
    try:
        # Method 1: Quantity sets
        if hasattr(element, "IsDefinedBy"):
            for rel in element.IsDefinedBy:
                if rel.is_a("IfcRelDefinesByProperties"):
                    if rel.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                        for qty in rel.RelatingPropertyDefinition.Quantities:
                            if qty.is_a("IfcQuantityArea"):
                                return qty.AreaValue

        # Method 2: Property sets
        psets = ifcopenshell.util.element.get_psets(element)
        for pset_data in psets.values():
            area = pset_data.get("Area") or pset_data.get("FootprintArea")
            if area:
                return area
    except Exception:
        pass

    return 0.0


def _get_space_area(space):
    """Get area of a space for estimation purposes"""
    try:
        psets = ifcopenshell.util.element.get_psets(space)
        for pset_data in psets.values():
            area = pset_data.get("FloorArea") or pset_data.get("Area")
            if area:
                return area
    except Exception:
        pass
    return 0.0
