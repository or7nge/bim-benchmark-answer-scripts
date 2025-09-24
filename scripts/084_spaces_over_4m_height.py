from scripts.ifc_utils import get_space_height
from scripts.question_helpers import open_ifc


def spaces_over_4m_height(ifc_file_path):
    """List spaces whose ceiling height exceeds 4 m."""
    try:
        model = open_ifc(ifc_file_path)
        result = []
        for space in model.by_type("IfcSpace"):
            height = get_space_height(space)
            if height is None or height <= 4.0:
                continue
            name = getattr(space, "Name", None) or getattr(space, "LongName", None) or getattr(space, "GlobalId", "Unknown")
            result.append({"name": str(name), "height": height})
        result.sort(key=lambda item: item["height"], reverse=True)
        return result
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
