from scripts.question_helpers import elements_area_by_storey, get_ordered_storeys, open_ifc, unique_elements


def slab_area_by_storey(ifc_file_path):
    """Total slab area per storey."""
    try:
        model = open_ifc(ifc_file_path)
        slabs = unique_elements(model.by_type("IfcSlab"))
        if not slabs:
            return {"No slabs": 0.0}
        storeys = get_ordered_storeys(model)
        areas = elements_area_by_storey(storeys, slabs)
        return areas if areas else {"Unassigned": 0.0}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
