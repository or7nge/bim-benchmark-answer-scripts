from scripts.ifc_utils import get_element_bbox
from scripts.question_helpers import open_ifc


def total_column_height(ifc_file_path):
    """Sum vertical extents of structural columns."""
    try:
        model = open_ifc(ifc_file_path)
        total = 0.0
        for column in model.by_type("IfcColumn"):
            bbox = get_element_bbox(column)
            if not bbox:
                continue
            min_z = bbox[2]
            max_z = bbox[5]
            height = max_z - min_z
            if height > 0:
                total += height
        return total
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
