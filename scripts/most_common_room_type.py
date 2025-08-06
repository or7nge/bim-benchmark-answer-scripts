import ifcopenshell


def most_common_room_type(ifc_file_path):
    """Find which room type appears most frequently"""
    try:
        ifc_file = ifcopenshell.open(ifc_file_path)
        spaces = ifc_file.by_type("IfcSpace")

        if not spaces:
            return "No rooms found"

        room_types = {}

        for space in spaces:
            # Try to get room type from various attributes
            room_type = None

            # Check ObjectType first
            if hasattr(space, "ObjectType") and space.ObjectType:
                room_type = space.ObjectType
            # Check PredefinedType
            elif hasattr(space, "PredefinedType") and space.PredefinedType:
                room_type = str(space.PredefinedType)
            # Check LongName
            elif hasattr(space, "LongName") and space.LongName:
                room_type = space.LongName
            # Fallback to Name
            elif hasattr(space, "Name") and space.Name:
                room_type = space.Name
            else:
                room_type = "Unclassified"

            # Clean up the room type name
            room_type = room_type.strip() if room_type else "Unclassified"

            # Count the room type
            room_types[room_type] = room_types.get(room_type, 0) + 1

        if not room_types:
            return "No room types identified"

        # Return most common room type
        most_common = max(room_types, key=room_types.get)
        return most_common

    except Exception as e:
        return f"Error: {str(e)}"
