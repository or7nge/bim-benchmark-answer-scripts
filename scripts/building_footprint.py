import ifcopenshell
import ifcopenshell.util.element


def building_footprint(ifc_file_path):
    """Calculate building's footprint area"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Try to find ground floor slabs first
        slabs = ifc_file.by_type("IfcSlab")
        ground_floor_area = 0.0

        for slab in slabs:
            # Check if this is a floor slab (not roof, etc.)
            predefined_type = getattr(slab, "PredefinedType", None)
            if predefined_type and "FLOOR" in str(predefined_type).upper():
                psets = ifcopenshell.util.element.get_psets(slab)
                for pset_name, pset_data in psets.items():
                    area = pset_data.get("NetArea") or pset_data.get("GrossArea") or pset_data.get("Area")
                    if area:
                        ground_floor_area += float(area)
                        break

        if ground_floor_area > 0:
            return round(ground_floor_area, 2)

        # Fallback: sum all space areas on the lowest floor
        storeys = ifc_file.by_type("IfcBuildingStorey")
        if not storeys:
            return 0.0

        # Find lowest storey by elevation
        lowest_storey = min(storeys, key=lambda s: s.Elevation if s.Elevation else float("inf"))

        spaces = ifc_file.by_type("IfcSpace")
        footprint_area = 0.0

        for space in spaces:
            # Check if space is in the lowest storey
            if hasattr(space, "ContainedInStructure"):
                for rel in space.ContainedInStructure:
                    if rel.RelatingStructure == lowest_storey:
                        psets = ifcopenshell.util.element.get_psets(space)
                        for pset_name, pset_data in psets.items():
                            area = pset_data.get("FloorArea") or pset_data.get("Area")
                            if area:
                                footprint_area += float(area)
                                break
                        break

        return round(footprint_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"
