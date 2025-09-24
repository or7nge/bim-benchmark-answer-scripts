from scripts.ifc_utils import get_element_bbox
from scripts.question_helpers import open_ifc


def total_railing_length(ifc_file_path):
    """Approximate total railing length using bounding boxes."""
    try:
        model = open_ifc(ifc_file_path)
        total = 0.0
        for railing in model.by_type("IfcRailing"):
            bbox = get_element_bbox(railing)
            if not bbox:
                continue
            min_x, min_y, _, max_x, max_y, _ = bbox
            spans = [max_x - min_x, max_y - min_y]
            length = max(spans)
            if length > 0:
                total += length
        return total
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
