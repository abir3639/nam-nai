import requests
import json

def fetch_nasa_donki_data():
    url = "https://api.nasa.gov/DONKI/SEP?startDate=2017-09-01&endDate=2017-09-30&api_key=DEMO_KEY"
    print("Attempting to fetch LIVE data from NASA API...\n")
    
    try:
        # We added a 5-second timeout so it doesn't freeze your terminal waiting for a dead server
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        print("✅ Successfully retrieved LIVE data from NASA!")
        
    except requests.exceptions.RequestException as e:
        # If the API fails, we catch the error and use our fallback data
        print(f"⚠️ NASA API is currently unavailable (Timeout/Error).")
        print("🔄 Switching to Fallback Mode (Using safely stored historical NASA data)...\n")
        
        data = [
            {
                "sepID": "2017-09-05T00:00:00-SEP-001",
                "eventTime": "2017-09-05T08:20Z",
                "link": "https://iswa.gsfc.nasa.gov/IswaSystemWebApp...",
                "instruments": [
                    {
                        "id": 13,
                        "displayName": "GOES15: SEM/EPEAD"
                    }
                ],
                "linkedEvents": [
                    {
                        "activityID": "2017-09-04T18:55:00-CME-001"
                    }
                ]
            }
        ]
        print("✅ Successfully loaded FALLBACK data!")

    # Print the final data structure, regardless of whether it came from the live API or the fallback
    if len(data) > 0:
        print(f"Found {len(data)} SEP event(s).")
        print("First Event Data:")
        print(json.dumps(data[0], indent=2))

if __name__ == "__main__":
    fetch_nasa_donki_data()