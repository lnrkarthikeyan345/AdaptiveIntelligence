import time
import requests

class RouteGraph:
    def __init__(self):
        pass

    def geocode(self, place):
        """
        Convert place name to lat/lon using Nominatim (OpenStreetMap)
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": place,
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "Raven-Route-Optimizer"
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()

        if not data:
            raise ValueError(f"Location not found: {place}")

        return float(data[0]["lat"]), float(data[0]["lon"])

    def get_route(self, start, end):
        """
        Get real route from OSRM
        """
        url = (
            f"https://router.project-osrm.org/route/v1/driving/"
            f"{start[1]},{start[0]};{end[1]},{end[0]}"
            f"?overview=full&geometries=geojson"
        )

        response = requests.get(url)
        data = response.json()

        if data.get("code") != "Ok":
            raise ValueError("OSRM routing failed")

        return data["routes"][0]["geometry"]["coordinates"]

    def dynamic_route_optimization(
        self,
        source,
        destination,
        update_interval,
        preferences,
        route_data,
        marker_close_event
    ):
        print("🌍 Using OpenStreetMap + OSRM routing")

        # Convert place names to coordinates
        start_coords = self.geocode(source)
        end_coords = self.geocode(destination)

        # Get real route
        route_coords = self.get_route(start_coords, end_coords)

        # Convert coordinates to "lat,lon" strings for frontend
        route_nodes = [
            f"{lat},{lon}" for lon, lat in route_coords
        ]

        route_data["final_route"] = []
        route_data["alternative_routes"] = []

        for node in route_nodes:
            route_data["final_route"].append(node)
            time.sleep(0.5)

            # Wait for frontend marker signal (non-blocking)
            marker_close_event.wait(timeout=0.5)
            marker_close_event.clear()

        print("✅ OSRM route optimization completed")
