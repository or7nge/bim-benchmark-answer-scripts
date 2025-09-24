from scripts.question_helpers import open_ifc, safe_by_type


def count_light_fixtures(ifc_file_path):
    """Count lighting fixtures in the model."""
    try:
        model = open_ifc(ifc_file_path)
        return len(safe_by_type(model, "IfcLightFixture"))
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
