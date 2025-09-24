from scripts.question_helpers import open_ifc


def vertical_circulation_counts(ifc_file_path):
    """Count major vertical circulation elements (stairs, ramps, elevators)."""
    try:
        model = open_ifc(ifc_file_path)
        stair_count = len(list(model.by_type("IfcStair"))) + len(list(model.by_type("IfcStairFlight")))
        ramp_count = len(list(model.by_type("IfcRamp"))) + len(list(model.by_type("IfcRampFlight")))
        elevators = 0
        for element in model.by_type("IfcTransportElement"):
            predefined = getattr(element, "PredefinedType", None)
            if predefined and str(predefined).upper() == "ELEVATOR":
                elevators += 1
        return {"stairs": stair_count, "ramps": ramp_count, "elevators": elevators}
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
