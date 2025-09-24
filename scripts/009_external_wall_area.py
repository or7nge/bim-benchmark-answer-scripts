import ifcopenshell
from scripts.ifc_utils import is_external_wall, get_element_area


def external_wall_area(ifc_file_path):
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = [w for w in ifc_file.by_type("IfcWall") if hasattr(w, "is_a")]
        total_external_area = 0.0

        for wall in walls:
            try:
                if not is_external_wall(wall):
                    continue

                wall_area = get_element_area(wall)
                total_external_area += wall_area

            except Exception as e:
                continue

        return round(total_external_area, 2)

    except Exception as e:
        return f"Error: {str(e)}"
