from scripts.question_helpers import open_ifc


def count_stairs(ifc_file_path):
    """Count stair assemblies and stair flights."""
    try:
        model = open_ifc(ifc_file_path)
        stairs = len(list(model.by_type("IfcStair")))
        flights = len(list(model.by_type("IfcStairFlight")))
        return {"IfcStair": stairs, "IfcStairFlight": flights, "total": stairs + flights}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
