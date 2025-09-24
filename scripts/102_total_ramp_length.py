from scripts.ifc_utils import get_element_bbox
from scripts.question_helpers import open_ifc


def total_ramp_length(ifc_file_path):
    """Approximate total ramp length using bounding boxes."""
    try:
        model = open_ifc(ifc_file_path)
        total = 0.0
        for ramp in list(model.by_type("IfcRamp")) + list(model.by_type("IfcRampFlight")):
            bbox = get_element_bbox(ramp)
            if not bbox:
                continue
            min_x, min_y, min_z, max_x, max_y, max_z = bbox
            spans = [max_x - min_x, max_y - min_y, max_z - min_z]
            length = max(spans)
            if length > 0:
                total += length
        return total
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
