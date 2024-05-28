import requests


def tilequery(longitude, latitude, radius, limit, access_token, tileset_id):
    # Construct the URL
    url = (
        f"https://api.mapbox.com/v4/{tileset_id}/tilequery/{longitude},{latitude}.json"
    )

    # Define the parameters
    params = {
        "dedupe": True,
        "access_token": access_token,
    }

    # Send the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        return data
    else:
        # Handle errors
        print(f"Error: {response.status_code}")
        return None


# Example usage
if __name__ == "__main__":
    # Replace with your own Mapbox access token
    ACCESS_TOKEN = "sk.eyJ1IjoicGFjaWZpcXVlMzY2IiwiYSI6ImNsd2tyYW81ODA2MWwyam54d3FzNHZhNWQifQ.qW9WugoBf8se4W-5md7Wmg"

    # Tileset ID for Mapbox Streets v8
    TILESET_ID = "pacifique366.cletpg9a30a2y2kogsx8ymh2y-0hy2c"

    # Coordinates to query
    longitude = 30.0061616666667
    latitude = -1.94404833333333

    # Query parameters
    radius = 25
    limit = 5

    # Make the tilequery request
    result = tilequery(longitude, latitude, radius, limit, ACCESS_TOKEN, TILESET_ID)

    if result:
        import json

        # Pretty print the JSON response
        print(json.dumps(result, indent=2))
