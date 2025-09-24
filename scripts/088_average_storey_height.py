from scripts.question_helpers import get_ordered_storeys, open_ifc, storey_elevation


def average_storey_height(ifc_file_path):
    """Average vertical spacing between consecutive storeys."""
    try:
        model = open_ifc(ifc_file_path)
        storeys = get_ordered_storeys(model)
        if len(storeys) < 2:
            return 0.0

        diffs = []
        prev_elev = storey_elevation(storeys[0])
        for storey in storeys[1:]:
            curr_elev = storey_elevation(storey)
            diffs.append(curr_elev - prev_elev)
            prev_elev = curr_elev
        diffs = [diff for diff in diffs if diff > 0]
        if not diffs:
            return 0.0
        return sum(diffs) / len(diffs)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
