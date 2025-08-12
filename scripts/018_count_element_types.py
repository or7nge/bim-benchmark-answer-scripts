import ifcopenshell


def count_element_types(ifc_file_path):
    """Count how many different types of building elements are used"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        # Get all entities that are building elements
        building_element_types = set()

        # Common IFC building element types to check for
        element_classes = [
            "IfcWall",
            "IfcSlab",
            "IfcRoof",
            "IfcColumn",
            "IfcBeam",
            "IfcDoor",
            "IfcWindow",
            "IfcStair",
            "IfcRailing",
            "IfcCurtainWall",
            "IfcFurnishingElement",
            "IfcBuildingElementProxy",
            "IfcCovering",
            "IfcFlowTerminal",
            "IfcFlowSegment",
            "IfcFlowFitting",
            "IfcDistributionElement",
            "IfcSpace",
            "IfcOpeningElement",
        ]

        for element_class in element_classes:
            try:
                elements = ifc_file.by_type(element_class)
                if elements:
                    building_element_types.add(element_class)
            except:
                continue

        return len(building_element_types)

    except Exception as e:
        return f"Error: {str(e)}"
