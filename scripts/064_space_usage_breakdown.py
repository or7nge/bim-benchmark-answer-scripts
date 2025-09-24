from collections import defaultdict

from scripts.question_helpers import classify_space_usage, open_ifc


def space_usage_breakdown(ifc_file_path):
    """Group spaces into high-level usage categories using keyword heuristics."""
    try:
        model = open_ifc(ifc_file_path)
        spaces = list(model.by_type("IfcSpace"))
        if not spaces:
            return {}

        counts = defaultdict(int)
        for space in spaces:
            category = classify_space_usage(space)
            counts[category] += 1
        return dict(counts)
    except Exception as exc:  # pragma: no cover
        return f"Error: {exc}"
