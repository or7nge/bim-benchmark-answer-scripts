from scripts.question_helpers import get_ordered_storeys, open_ifc, storey_elevation, storey_label


def storey_height_differences(ifc_file_path):
    """Return elevation differences between successive storeys."""
    try:
        model = open_ifc(ifc_file_path)
        storeys = get_ordered_storeys(model)
        if len(storeys) < 2:
            return []

        differences = []
        previous = storeys[0]
        prev_elev = storey_elevation(previous)
        for current in storeys[1:]:
            curr_elev = storey_elevation(current)
            diff = curr_elev - prev_elev
            differences.append(
                {
                    "from": storey_label(previous),
                    "to": storey_label(current),
                    "height": diff,
                }
            )
            previous = current
            prev_elev = curr_elev
        return differences
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
