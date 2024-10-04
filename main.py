import requests
from geopy.geocoders import Nominatim


def get_bus_data():
    base_url = "https://huntsville.routematch.io/routeshout/api/v2.0/rs.vehicle.getListByRoutes"

    params = {
        "key": "RouteShoutAPIAdapterv2.0",
        "agency": "1",
        "routes": "Meridian/A&M",
        "templates[]": ["title", "body"],
        "title": "{@masterRouteShortName} - Vehicle {@internalVehicleId}",
        "body": "Heading {@tripDirection} on {@masterRouteLongName} at {@speed}mph",
        "timeHorizon": "1",
        "timeSensitive": "false",
    }

    headers = {
        "Host": "huntsville.routematch.io",
        "Sec-Ch-Ua-Platform": '"Android"',
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; sdk_gphone64_arm64 Build/SE1A.220203.002.A1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/129.0.6668.81 Mobile Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Sec-Ch-Ua": '"Android WebView";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://huntsville.routematch.io/routeshout/stop/Alabama+A+%26+M+College?mRouteId=Meridian/A&M",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Priority": "u=1, i",
    }

    response = requests.get(url=base_url, headers=headers, params=params)
    return response.json()


bus_data = get_bus_data()
response = bus_data.get("response", [])


def is_bus_in_gas_station(latitude, longitude):
    # Define the boundaries of the gas station area
    min_latitude = 34.792966
    max_latitude = 34.792972
    min_longitude = -86.598465
    max_longitude = -86.595881

    return (
        min_latitude <= latitude <= max_latitude
        and min_longitude <= longitude <= max_longitude
    )


def get_nearby_landmark(latitude, longitude):
    geolocator = Nominatim(user_agent="bus_location_bot")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    if location:
        return ",".join(location.address.split(",")[:2])
    return "No nearby landmark found."


bus_info_list = []

if not response:
    print("No bus data available.")
else:
    for bus in response:
        hN = bus.get("hN")
        uT = bus.get("uT")
        la = bus.get("la")
        lo = bus.get("lo")
        body = bus.get("templates", {}).get("body", "")
        speed = int(
            body[-5:-3]
        )  # assumed that body text is always abmph so used slicing to get the speed

        bus_info = {
            "hN": hN,
            "uT": uT,
            "latitude": la,
            "longitude": lo,
            "speed_mph": speed,
        }

        if is_bus_in_gas_station(la, lo):
            print(f"Bus {hN} is in the gas station area!")

        landmark = get_nearby_landmark(la, lo)
        print(f"Bus is in {hN} direction and is near: {landmark}")

        bus_info_list.append(bus_info)

    for info in bus_info_list:
        print(info)
