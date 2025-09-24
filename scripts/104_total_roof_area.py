from scripts.ifc_utils import get_element_area
from scripts.question_helpers import open_ifc


def total_roof_area(ifc_file_path):
    """Sum area of roof elements and slabs tagged as roofs."""
    try:
        model = open_ifc(ifc_file_path)
        total = 0.0
        for roof in model.by_type("IfcRoof"):
            area = get_element_area(roof)
            if area > 0:
                total += area
        for slab in model.by_type("IfcSlab"):
            predefined = getattr(slab, "PredefinedType", None)
            if predefined and str(predefined).upper() != "ROOF":
                continue
            area = get_element_area(slab)
            if area > 0:
                total += area
        return total
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
