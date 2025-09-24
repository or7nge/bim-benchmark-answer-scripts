from scripts.question_helpers import count_elements_by_storey, get_ordered_storeys, open_ifc


def storey_fewest_doors(ifc_file_path):
    """Identify the storey with the lowest door count."""
    try:
        model = open_ifc(ifc_file_path)
        doors = list(model.by_type("IfcDoor"))
        if not doors:
            return "No doors found"

        storeys = get_ordered_storeys(model)
        counts = count_elements_by_storey(storeys, doors)
        if not counts:
            return "All doors unassigned"

        target_storey = min(counts.items(), key=lambda item: (item[1], item[0]))
        return target_storey[0]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
