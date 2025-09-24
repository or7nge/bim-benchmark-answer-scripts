from scripts.ifc_utils import get_space_height
from scripts.question_helpers import open_ifc


def space_height_statistics(ifc_file_path):
    """Return count, min, max and average ceiling height across all spaces."""
    try:
        model = open_ifc(ifc_file_path)
        heights = [h for h in (get_space_height(space) for space in model.by_type("IfcSpace")) if h is not None]
        if not heights:
            return {"count": 0, "min": 0.0, "max": 0.0, "average": 0.0}
        total = sum(heights)
        return {
            "count": len(heights),
            "min": min(heights),
            "max": max(heights),
            "average": total / len(heights),
        }
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
