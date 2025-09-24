from scripts.question_helpers import open_ifc


def count_elevators(ifc_file_path):
    """Count transport elements classified as elevators."""
    try:
        model = open_ifc(ifc_file_path)
        count = 0
        for element in model.by_type("IfcTransportElement"):
            predefined = getattr(element, "PredefinedType", None)
            if predefined and str(predefined).upper() == "ELEVATOR":
                count += 1
        return count
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
