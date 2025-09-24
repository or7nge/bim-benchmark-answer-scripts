from scripts.question_helpers import open_ifc


def count_ramps(ifc_file_path):
    """Count ramp elements (IfcRamp and IfcRampFlight)."""
    try:
        model = open_ifc(ifc_file_path)
        return len(list(model.by_type("IfcRamp"))) + len(list(model.by_type("IfcRampFlight")))
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
