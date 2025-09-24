from scripts.question_helpers import open_ifc, safe_by_type


def top_furniture_types(ifc_file_path):
    """List the five most common furniture types by count."""
    try:
        model = open_ifc(ifc_file_path)
        furniture = safe_by_type(model, "IfcFurniture")
        if not furniture:
            return []

        counts = {}
        for item in furniture:
            for attr in ("ObjectType", "PredefinedType", "Name"):
                value = getattr(item, attr, None)
                if value:
                    key = str(value)
                    break
            else:
                key = "Unknown"
            counts[key] = counts.get(key, 0) + 1

        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return [{"type": key, "count": value} for key, value in ranked[:5]]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
