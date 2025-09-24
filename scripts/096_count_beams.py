from scripts.question_helpers import open_ifc


def count_beams(ifc_file_path):
    """Count structural beams in the model."""
    try:
        model = open_ifc(ifc_file_path)
        return len(list(model.by_type("IfcBeam")))
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
