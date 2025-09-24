from scripts.question_helpers import (
    count_elements_by_storey,
    elements_area_by_storey,
    get_ordered_storeys,
    open_ifc,
)


def storey_highest_door_density(ifc_file_path):
    """Find the storey with the highest number of doors per square metre."""
    try:
        model = open_ifc(ifc_file_path)
        doors = list(model.by_type("IfcDoor"))
        spaces = list(model.by_type("IfcSpace"))
        if not doors or not spaces:
            return "Insufficient data"

        storeys = get_ordered_storeys(model)
        door_counts = count_elements_by_storey(storeys, doors)
        area_totals = elements_area_by_storey(storeys, spaces)

        ratios = {}
        for storey_name, door_count in door_counts.items():
            area = area_totals.get(storey_name)
            if area is None or area <= 0:
                continue
            ratios[storey_name] = door_count / area

        if not ratios:
            return "No ratios computed"

        target = max(ratios.items(), key=lambda item: (item[1], item[0]))
        return target[0]
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
