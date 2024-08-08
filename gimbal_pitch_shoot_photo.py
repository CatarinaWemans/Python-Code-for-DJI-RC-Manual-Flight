import xml.etree.ElementTree as ET
import math
import re

def extract_coordinates_from_kml(kml_file):
    coordinates = []
    tree = ET.parse(kml_file)
    root = tree.getroot()
    document_element = root.find(".//Document")
    if document_element is not None:
        folder_element = document_element.find(".//Folder")
        if folder_element is not None:
            placemarks = folder_element.findall(".//Placemark")
            for placemark in placemarks:
                point = placemark.find(".//Point/coordinates")
                if point is not None:
                    name = placemark.findtext('name')
                    coords = [float(coord) for coord in point.text.split(',')]
                    coordinates.append((name, coords))
    return coordinates

def calculate_distance(waypoint_coord, poi_coord):
    """
    Calculate the great circle distance between two points
    on the earth specified in decimal degrees.
    """
    # Convert latitude and longitude from degrees to radians
    waypoint_lat_rad = math.radians(waypoint_coord[1])
    waypoint_lon_rad = math.radians(waypoint_coord[0])
    poi_lat_rad = math.radians(poi_coord[1])
    poi_lon_rad = math.radians(poi_coord[0])

    # Haversine formula
    dlon = poi_lon_rad - waypoint_lon_rad
    dlat = poi_lat_rad - waypoint_lat_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(waypoint_lat_rad) * math.cos(poi_lat_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    radius_of_earth = 6371  # Radius of the Earth in kilometers. You can change it to 3958.8 for miles
    distance = radius_of_earth * c * 1000  # Convert distance to meters

    return distance

print(calculate_distance)

def calculate_angle_to_poi(waypoint_coord, poi_coord, distance):
    # Get the altitude of the waypoint
    y = waypoint_coord[2]-poi_coord[2]
    # Calculate the angle between the waypoint and POI using trigonometry
    angle_rad = -math.atan2(y, distance)
    # Convert the angle from radians to degrees
    angle_deg = math.degrees(angle_rad)
    return angle_deg

def substitute_gimbal_pitch(kml_file, gimbal_pitch_data):
    with open(kml_file, 'r') as file:
        kml_data = file.read()
    for waypoint_name, pitch_angle in gimbal_pitch_data.items():
        kml_data = re.sub(fr'(<name>{waypoint_name}</name>.*?<mis:gimbalPitch>\s*)[-+]?\d*\.?\d+(?:\.\d+)?(?:\s*</mis:gimbalPitch>)',
                          fr'\g<1>{pitch_angle:.1f}</mis:gimbalPitch>',
                          kml_data, flags=re.DOTALL)
    with open(kml_file, 'w') as file:
        file.write(kml_data)

def add_photograph_action_to_all_waypoints(kml_file):
    with open(kml_file, 'r') as f:
        kml_content = f.readlines()

    new_line = '          <mis:actions param="0" accuracy="0" cameraIndex="0" payloadType="0" payloadIndex="0">ShootPhoto</mis:actions>\n'

    for i in range(len(kml_content)):
        if '<Folder>' in kml_content[i] and '<name>Waypoints</name>' in kml_content[i+1]:
            for j in range(i+2, len(kml_content)):
                if '</Folder>' in kml_content[j]:
                    break
                if '<Placemark>' in kml_content[j]:
                    action_present = False
                    while '</Placemark>' not in kml_content[j]:
                        if new_line.strip() in kml_content[j]:
                            action_present = True
                            break
                        j += 1
                    if not action_present:
                        for k in range(j-1, i, -1):
                            if '</ExtendedData>' in kml_content[k]:
                                kml_content.insert(k, new_line)  # Insert just before </ExtendedData>
                                break

    with open(kml_file, 'w') as f:
        f.writelines(kml_content)


import re

def substitute_poi(kml_file, poi_coords):
    with open(kml_file, 'r') as file:
        kml_data = file.read()

    # Search for the Placemark with name "Poi" and replace its coordinates
    try:
        replacement = f'<Placemark>\n' \
                      f'      <name>Poi</name>\n' \
                      f'      <description>Poi</description>\n' \
                      f'      <visibility>1</visibility>\n' \
                      f'      <Point>\n' \
                      f'        <coordinates>{poi_coords[0]},{poi_coords[1]},{poi_coords[2]}</coordinates>\n' \
                      f'      </Point>\n' \
                      f'    </Placemark>'

        kml_data = re.sub(r'<Placemark>\s*<name>Poi<\/name>\s*<description>Poi<\/description>\s*<visibility>1<\/visibility>\s*<Point>\s*<coordinates>.*?<\/coordinates>\s*<\/Point>\s*<\/Placemark>',
                          replacement,
                          kml_data, flags=re.DOTALL)
    except Exception as e:
        print("Error during substitution:", e)

    with open(kml_file, 'w') as file:
        file.write(kml_data)

# Example usage:
# substitute_poi("your_kml_file.kml", [-9.336533942863042, 38.836043669491374, 50.0])


def main():
    kml_file = input("Enter the name of the KML file with waypoints: ") 
    choice = input("Do you want to insert gimbal pitch manually (M) or calculate to the Point of Interest (P)? ")

    if choice.upper() == 'M':
        gimbal_pitch_input = float(input("Enter the gimbal pitch angle: "))
        gimbal_pitch_data = {waypoint_name: gimbal_pitch_input for waypoint_name, _ in extract_coordinates_from_kml(kml_file)}
        # Substitute gimbal pitch data in KML
        substitute_gimbal_pitch(kml_file, gimbal_pitch_data)
        print("Gimbal pitch angles substituted successfully.")

        # Add photograph action to all waypoints
        add_photograph_action_to_all_waypoints(kml_file)
        print("ShootPhoto action added to all waypoints.")
    elif choice.upper() == 'P':
        poi_coords_input = input("Enter the coordinates of the Point Of Interest (format: long,lat,alt): ")
        poi_coords = tuple(map(float, poi_coords_input.split(',')))
        substitute_poi(kml_file, poi_coords)

        waypoint_coords = extract_coordinates_from_kml(kml_file)

        # Calculate distance and angle for each waypoint
        gimbal_pitch_data = {}
        for waypoint_name, waypoint_coord in waypoint_coords:
            # Calculate distance between Waypoint and POI
            distance = calculate_distance(waypoint_coord, poi_coords)
            # Calculate angle between horizontal plane to the Waypoint-POI vector
            angle = calculate_angle_to_poi(waypoint_coord, poi_coords, distance)
            # Store the angle for the waypoint
            gimbal_pitch_data[waypoint_name] = angle

        # Substitute gimbal pitch data in KML
        substitute_gimbal_pitch(kml_file, gimbal_pitch_data)
        print("Gimbal pitch angles substituted successfully.")

        # Add photograph action to all waypoints
        add_photograph_action_to_all_waypoints(kml_file)
        print("ShootPhoto action added to all waypoints.")

        print("Point of Interest substituted successfully.")
    else:
        print("Invalid choice. Please choose 'M' for manual or 'P' for point of interest calculation.")
        return

if __name__ == "__main__":
    main()
