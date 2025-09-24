from scripts.question_helpers import open_ifc


def count_curtain_walls(ifc_file_path):
    """Count the number of curtain wall assemblies."""
    try:
        model = open_ifc(ifc_file_path)
        return len(list(model.by_type("IfcCurtainWall")))
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
