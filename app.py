from flask import Flask, request, jsonify, send_from_directory
import requests
from itertools import permutations
from urllib.parse import quote_plus

app = Flask(__name__)

API_KEY = ''

# HTML CSS JS INTEGRATION
# Serve the static HTML
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# Serve CSS and JS
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)



def get_lat_lng(location):
    """Get latitude and longitude for a location using Google Maps Geocoding API."""
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': location,
        'key': API_KEY
    }
    response = requests.get(base_url, params=params)
    result = response.json()
    if result['status'] == 'OK':
        location = result['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    else:
        raise Exception(f"Error fetching coordinates: {result['status']}")

def get_distance_matrix(locations):
    """Get distance matrix using Google Maps Distance Matrix API."""
    origins = "|".join(locations)
    destinations = "|".join(locations)
    
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        'origins': origins,
        'destinations': destinations,
        'key': API_KEY
    }
    response = requests.get(base_url, params=params)
    result = response.json()
    
    if result['status'] == 'OK':
        matrix = []
        for row in result['rows']:
            distances = [element['distance']['value'] for element in row['elements']]
            matrix.append(distances)
        return matrix
    else:
        raise Exception(f"Error fetching distance matrix: {result['status']}")

def calculate_total_distance(graph, path, start_location, end_location):
    total_distance = graph[start_location][path[0]]  # From start to first city in path
    for i in range(len(path) - 1):
        total_distance += graph[path[i]][path[i+1]]
    total_distance += graph[path[-1]][end_location]  # From last city in path to end location
    return total_distance

def traveling_salesman(graph, start_location, end_location):
    # We will permute over the cities that are neither the start nor the end
    intermediate_cities = list(range(len(graph)))
    intermediate_cities.remove(start_location)
    intermediate_cities.remove(end_location)

    min_distance = float('inf')
    best_path = []

    for path in permutations(intermediate_cities):
        current_distance = calculate_total_distance(graph, path, start_location, end_location)
        if current_distance < min_distance:
            min_distance = current_distance
            best_path = path
    
    return best_path, min_distance

def generate_google_maps_url(start_location, end_location, best_path, locations):
    """Generate a Google Maps URL for the given path."""
    start = quote_plus(locations[start_location])
    end = quote_plus(locations[end_location])
    waypoints = "|".join(quote_plus(locations[i]) for i in best_path)
    
    # Construct the Google Maps URL
    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={start}&destination={end}&waypoints={waypoints}"
    
    return maps_url

@app.route('/tsp', methods=['POST'])
def solve_tsp():
    data = request.json
    locations = data.get('locations')

    if not locations or len(locations) < 2:
        return jsonify({"error": "Please provide at least two locations."}), 400

    try:
        lat_lngs = [f"{get_lat_lng(loc)[0]},{get_lat_lng(loc)[1]}" for loc in locations]
        distance_matrix = get_distance_matrix(lat_lngs)

        start_location = 0  # First location
        end_location = len(locations) - 1  # Last location
        
        best_path, min_distance = traveling_salesman(distance_matrix, start_location, end_location)
        
        ordered_locations = [locations[start_location]] + [locations[i] for i in best_path] + [locations[end_location]]
        google_maps_url = generate_google_maps_url(start_location, end_location, best_path, locations)
        
        return jsonify({
            "best_path": ordered_locations,
            "minimum_distance_km": min_distance / 1000,
            "google_maps_url": google_maps_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
