from scripts.ifc_utils import get_element_bbox
from scripts.question_helpers import open_ifc


def total_beam_length(ifc_file_path):
    """Approximate total beam centerline length using bounding boxes."""
    try:
        model = open_ifc(ifc_file_path)
        total = 0.0
        for beam in model.by_type("IfcBeam"):
            bbox = get_element_bbox(beam)
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
