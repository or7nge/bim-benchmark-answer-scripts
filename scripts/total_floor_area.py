# scripts/total_floor_area.py - Q004 (Medium) - Fixed version
import ifcopenshell
import ifcopenshell.util.element


def total_floor_area(ifc_file_path):
    """Calculate total floor area of all spaces - improved version"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")
        total_area = 0.0

        # Expanded list of possible area property names
        area_keys = [
            "Area",
            "FloorArea",
            "NetFloorArea",
            "GrossFloorArea",
            "NetArea",
            "GrossArea",
            "UsableArea",
            "RoomArea",
            "FinishFloorArea",
            "SpaceArea",
            "InternalArea",
        ]

        for space in spaces:
            space_area = 0.0

            # Method 1: Property sets
            psets = ifcopenshell.util.element.get_psets(space)
            for pset_data in psets.values():
                for key in area_keys:
                    if key in pset_data and pset_data[key] is not None:
                        try:
                            space_area = float(pset_data[key])
                            if space_area > 0:
                                break
                        except (ValueError, TypeError):
                            continue
                if space_area > 0:
                    break

            # Method 2: Quantity sets
            if space_area == 0:
                try:
                    quantities = ifcopenshell.util.element.get_quantities(space)
                    for qty_data in quantities.values():
                        for key in area_keys:
                            if key in qty_data and qty_data[key] is not None:
                                try:
                                    space_area = float(qty_data[key])
                                    if space_area > 0:
                                        break
                                except (ValueError, TypeError):
                                    continue
                        if space_area > 0:
                            break
                except:
                    pass

            total_area += space_area

        return round(total_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"
