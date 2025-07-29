import ifcopenshell
import ifcopenshell.util.element


def wall_materials(ifc_file_path):
    """Extract unique materials used in walls"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        walls = ifc_file.by_type("IfcWall")
        materials = set()

        for wall in walls:
            # Get materials through relationships
            if hasattr(wall, "HasAssociations"):
                for association in wall.HasAssociations:
                    if association.is_a("IfcRelAssociatesMaterial"):
                        material = association.RelatingMaterial
                        if material.is_a("IfcMaterial"):
                            materials.add(material.Name)
                        elif material.is_a("IfcMaterialLayerSetUsage"):
                            layer_set = material.ForLayerSet
                            for layer in layer_set.MaterialLayers:
                                if layer.Material:
                                    materials.add(layer.Material.Name)

        return sorted(list(materials)) if materials else ["No materials found"]
    except Exception as e:
        return f"Error: {str(e)}"
