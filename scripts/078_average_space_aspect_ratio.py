from scripts.ifc_utils import get_element_bbox
from scripts.question_helpers import open_ifc


def average_space_aspect_ratio(ifc_file_path):
    """Compute average plan aspect ratio (long side / short side) across spaces."""
    try:
        model = open_ifc(ifc_file_path)
        ratios = []
        for space in model.by_type("IfcSpace"):
            bbox = get_element_bbox(space)
            if not bbox:
                continue
            min_x, min_y, _, max_x, max_y, _ = bbox
            width = max_x - min_x
            depth = max_y - min_y
            short_side = min(width, depth)
            long_side = max(width, depth)
            if short_side <= 0 or long_side <= 0:
                continue
            ratios.append(long_side / short_side)
        if not ratios:
            return 0.0
        return sum(ratios) / len(ratios)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
