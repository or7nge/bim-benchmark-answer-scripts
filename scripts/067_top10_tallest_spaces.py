from scripts.ifc_utils import get_space_height
from scripts.question_helpers import open_ifc


def top10_tallest_spaces(ifc_file_path):
    """Return the ten spaces with the highest ceiling."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        items = []
        for space in spaces:
            height = get_space_height(space)
            if height is None:
                continue
            name = getattr(space, "Name", None) or getattr(space, "LongName", None) or getattr(space, "GlobalId", "Unknown")
            items.append({"name": str(name), "height": height})
        items.sort(key=lambda item: item["height"], reverse=True)
        return items[:10]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
