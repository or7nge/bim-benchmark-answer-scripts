from scripts.question_helpers import element_area, open_ifc

CORRIDOR_KEYWORDS = ["corridor", "hallway", "hall", "passage", "lobby"]


def corridor_area_total(ifc_file_path):
    """Total area of circulation spaces identified as corridors or halls."""
    try:
        model = open_ifc(ifc_file_path)
        total = 0.0
        for space in model.by_type("IfcSpace"):
            labels = " ".join(
                str(value)
                for value in (
                    getattr(space, "LongName", ""),
                    getattr(space, "Name", ""),
                    getattr(space, "ObjectType", ""),
                    getattr(space, "Description", ""),
                )
                if value
            ).lower()
            if not any(keyword in labels for keyword in CORRIDOR_KEYWORDS):
                continue
            area = element_area(space)
            if area is not None:
                total += area
        return total
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
