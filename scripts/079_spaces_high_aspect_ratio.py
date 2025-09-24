from scripts.ifc_utils import get_element_bbox
from scripts.question_helpers import open_ifc


def spaces_high_aspect_ratio(ifc_file_path):
    """List spaces whose plan aspect ratio exceeds 2:1."""
    try:
        model = open_ifc(ifc_file_path)
        result = []
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
            ratio = long_side / short_side
            if ratio > 2.0:
                name = getattr(space, "Name", None) or getattr(space, "LongName", None) or getattr(space, "GlobalId", "Unknown")
                result.append({"name": str(name), "ratio": ratio})
        result.sort(key=lambda item: item["ratio"], reverse=True)
        return result
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
