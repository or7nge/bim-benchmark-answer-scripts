from scripts.question_helpers import open_ifc, safe_by_type


def count_furniture(ifc_file_path):
    """Count furniture elements (IfcFurniture)."""
    try:
        model = open_ifc(ifc_file_path)
        return len(safe_by_type(model, "IfcFurniture"))
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
