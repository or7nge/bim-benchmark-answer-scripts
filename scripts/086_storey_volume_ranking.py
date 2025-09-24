from scripts.ifc_utils import find_storey_for_element, get_space_volume
from scripts.question_helpers import get_ordered_storeys, open_ifc, storey_label


def storey_volume_ranking(ifc_file_path):
    """Rank storeys by total enclosed space volume."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        if not spaces:
            return []

        storeys = get_ordered_storeys(model)
        totals = {}
        for storey in storeys:
            totals[storey_label(storey)] = 0.0
        totals.setdefault("Unassigned", 0.0)

        for space in spaces:
            volume = get_space_volume(space)
            if volume <= 0:
                continue
            storey = find_storey_for_element(space, storeys)
            key = storey_label(storey) if storey else "Unassigned"
            totals[key] = totals.get(key, 0.0) + volume

        items = [{"storey": name, "volume": volume} for name, volume in totals.items() if volume > 0]
        items.sort(key=lambda item: item["volume"], reverse=True)
        return items
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
