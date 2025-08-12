import ifcopenshell
import ifcopenshell.util.element


def count_hvac_zones(ifc_file_path):
    """Count thermal zones or HVAC zones in the building"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)

        zone_count = 0

        # Method 1: Count IfcZone entities
        zones = ifc_file.by_type("IfcZone")
        thermal_zones = []

        for zone in zones:
            zone_name = (zone.Name or "").lower()
            zone_type = (getattr(zone, "ObjectType", "") or "").lower()

            # Check if it's a thermal/HVAC zone
            hvac_keywords = ["thermal", "hvac", "heating", "cooling", "air", "climate", "temperature"]
            if any(keyword in zone_name or keyword in zone_type for keyword in hvac_keywords):
                thermal_zones.append(zone)

        zone_count += len(thermal_zones)

        # Method 2: Count IfcSystem entities related to HVAC
        systems = ifc_file.by_type("IfcSystem")
        hvac_systems = []

        for system in systems:
            # Check predefined type
            if hasattr(system, "PredefinedType"):
                predefined = str(system.PredefinedType).upper()
                if any(keyword in predefined for keyword in ["HVAC", "HEATING", "COOLING", "VENTILATION"]):
                    hvac_systems.append(system)
                    continue

            # Check name and object type
            system_name = (system.Name or "").lower()
            system_type = (getattr(system, "ObjectType", "") or "").lower()

            hvac_keywords = ["hvac", "heating", "cooling", "ventilation", "air conditioning", "thermal"]
            if any(keyword in system_name or keyword in system_type for keyword in hvac_keywords):
                hvac_systems.append(system)

        zone_count += len(hvac_systems)

        # Method 3: Count spaces with HVAC-related properties
        spaces = ifc_file.by_type("IfcSpace")
        hvac_controlled_spaces = set()

        for space in spaces:
            has_hvac_properties = False

            try:
                psets = ifcopenshell.util.element.get_psets(space)
                for pset_name, pset_data in psets.items():
                    # Look for HVAC-related properties
                    hvac_props = [
                        "ThermalZone",
                        "HvacZone",
                        "HeatingSetpoint",
                        "CoolingSetpoint",
                        "AirChangeRate",
                        "SupplyAir",
                        "ReturnAir",
                        "DesignTemperature",
                    ]

                    for prop in hvac_props:
                        if prop in pset_data and pset_data[prop]:
                            has_hvac_properties = True
                            break

                    if has_hvac_properties:
                        break
            except Exception:
                continue

            if has_hvac_properties:
                hvac_controlled_spaces.add(space.id())

        # If we found HVAC-controlled spaces but no explicit zones,
        # estimate zone count (typically 1 zone per 5-10 spaces)
        if len(hvac_controlled_spaces) > 0 and zone_count == 0:
            estimated_zones = max(1, len(hvac_controlled_spaces) // 8)  # Rough estimate
            zone_count = estimated_zones

        # Method 4: Look for HVAC distribution elements as zone indicators
        if zone_count == 0:
            hvac_elements = []
            hvac_elements.extend(ifc_file.by_type("IfcFlowTerminal"))  # VAV boxes, diffusers
            hvac_elements.extend(ifc_file.by_type("IfcFlowController"))  # Dampers, valves
            hvac_elements.extend(ifc_file.by_type("IfcAirTerminal"))  # Air terminals

            # Group by floor/location to estimate zones
            if hvac_elements:
                # Simplified: assume each floor has at least one zone
                storeys = ifc_file.by_type("IfcBuildingStorey")
                zone_count = max(1, len(storeys))

        # Default minimum
        if zone_count == 0:
            zone_count = 1  # Assume at least one thermal zone

        return zone_count

    except Exception as e:
        return f"Error: {str(e)}"
