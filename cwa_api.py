"""
CWA (Central Weather Administration) Open Data API Client & Data Parser.
Corresponds to Steps 3, 4, 5, 6, 7, 20 in the curriculum:
- CWA API integration (Requests, Authorization Header / Query Param)
- JSON response parsing for locations, weather elements (MinT, MaxT)
- Pandas DataFrame structuring (regionName, dataDate, minT, maxT)
- Fallback realistic data generator for instant offline demonstration
"""

import datetime
import random
import requests
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple

# Standard Taiwan regions shown in curriculum poster
REGIONS = [
    "北部地區",
    "中部地區",
    "南部地區",
    "東北部地區",
    "東部地區",
    "東南部地區",
]

# Region center coordinates for Folium Map visualization (Step 17)
REGION_COORDINATES = {
    "北部地區": {"lat": 25.04, "lon": 121.53, "desc": "包含基隆、雙北、桃園、新竹等地"},
    "東北部地區": {"lat": 24.75, "lon": 121.75, "desc": "包含宜蘭地區"},
    "中部地區": {"lat": 24.15, "lon": 120.67, "desc": "包含苗栗、台中、彰化、南投、雲林"},
    "東部地區": {"lat": 23.99, "lon": 121.61, "desc": "包含花蓮地區"},
    "南部地區": {"lat": 22.99, "lon": 120.21, "desc": "包含嘉義、台南、高雄、屏東"},
    "東南部地區": {"lat": 22.75, "lon": 121.15, "desc": "包含台東地區"},
}

# Base temperature offsets for realistic mock simulation
REGION_BASE_TEMPS = {
    "北部地區": {"min": 19.0, "max": 26.5},
    "東北部地區": {"min": 18.5, "max": 25.0},
    "中部地區": {"min": 20.5, "max": 29.5},
    "東部地區": {"min": 20.0, "max": 27.0},
    "南部地區": {"min": 22.0, "max": 32.0},
    "東南部地區": {"min": 21.5, "max": 29.0},
}


def fetch_cwa_live_data(api_key: str, dataset_id: str = "F-C0032-001") -> Optional[Dict[str, Any]]:
    """
    Step 4: Fetch live JSON data from Central Weather Administration Open Data platform.
    Uses requests with Authorization parameter.
    """
    if not api_key:
        return None

    # CWA Open Data API endpoint
    endpoint = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{dataset_id}"
    params = {
        "Authorization": api_key.strip(),
        "format": "JSON"
    }

    try:
        response = requests.get(endpoint, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"CWA API returned status {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"Error fetching from CWA API: {e}")
        return None


def parse_cwa_json_to_df(json_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Steps 5, 6, 7: Parse CWA JSON structure, extract MinT and MaxT,
    and convert to a structured Pandas DataFrame.
    """
    records: List[Dict[str, Any]] = []

    try:
        dataset_records = json_data.get("records", {})
        
        # Check standard location list format
        location_list = []
        if "location" in dataset_records:
            location_list = dataset_records["location"]
        elif "locations" in dataset_records:
            locs_parent = dataset_records["locations"]
            if isinstance(locs_parent, list) and len(locs_parent) > 0:
                location_list = locs_parent[0].get("location", [])
            elif isinstance(locs_parent, dict):
                location_list = locs_parent.get("location", [])

        # Map CWA location names to our 6 key regions if needed
        for loc in location_list:
            raw_name = loc.get("locationName", "")
            region_name = match_region_name(raw_name)
            
            # Find MinT and MaxT weatherElements
            weather_elements = loc.get("weatherElement", [])
            min_t_dict = {}
            max_t_dict = {}

            for element in weather_elements:
                elem_name = element.get("elementName", "")
                times = element.get("time", [])

                if elem_name == "MinT":
                    for t in times:
                        # Extract date string YYYY-MM-DD
                        date_str = extract_date_str(t.get("startTime", ""))
                        val = parse_temperature_val(t.get("parameter", {}).get("parameterName"))
                        if date_str and val is not None:
                            min_t_dict[date_str] = val
                elif elem_name == "MaxT":
                    for t in times:
                        date_str = extract_date_str(t.get("startTime", ""))
                        val = parse_temperature_val(t.get("parameter", {}).get("parameterName"))
                        if date_str and val is not None:
                            max_t_dict[date_str] = val

            # Align MinT and MaxT dates
            all_dates = sorted(set(min_t_dict.keys()) & set(max_t_dict.keys()))
            for d in all_dates:
                records.append({
                    "regionName": region_name,
                    "dataDate": d,
                    "minT": float(min_t_dict[d]),
                    "maxT": float(max_t_dict[d]),
                })
    except Exception as e:
        print(f"Error parsing CWA JSON: {e}")

    if records:
        df = pd.DataFrame(records)
        # Deduplicate regionName and dataDate by averaging if multiple time segments
        df = df.groupby(["regionName", "dataDate"], as_index=False).agg({
            "minT": "min",
            "maxT": "max"
        })
        return df

    return pd.DataFrame(columns=["regionName", "dataDate", "minT", "maxT"])


def match_region_name(name: str) -> str:
    """Helper to standardize county/location names into the 6 major regions."""
    if "北" in name and "東" not in name:
        return "北部地區"
    elif "宜蘭" in name or "東北" in name:
        return "東北部地區"
    elif "中" in name or "苗栗" in name or "台中" in name or "彰化" in name or "雲林" in name or "南投" in name:
        return "中部地區"
    elif "南" in name or "嘉義" in name or "台南" in name or "高雄" in name or "屏東" in name:
        return "南部地區"
    elif "花蓮" in name or "東部" in name:
        return "東部地區"
    elif "台東" in name or "東南" in name:
        return "東南部地區"
    return name if name in REGIONS else "北部地區"


def extract_date_str(datetime_str: str) -> Optional[str]:
    """Parse '2026-04-14 06:00:00' or ISO format into '2026-04-14'."""
    if not datetime_str:
        return None
    return datetime_str.split(" ")[0].split("T")[0]


def parse_temperature_val(val: Any) -> Optional[float]:
    """Safe float parser."""
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def generate_mock_forecast_data(days: int = 7, start_date: Optional[datetime.date] = None) -> pd.DataFrame:
    """
    Generate realistic 7-day weather forecast dataset matching the curriculum schema.
    Guarantees seamless out-of-the-box demonstration without requiring immediate API keys.
    """
    if start_date is None:
        start_date = datetime.date.today()

    rows = []
    # Seed based on date to maintain consistency across reloads within the same day
    base_seed = int(start_date.strftime("%Y%m%d"))
    rng = random.Random(base_seed)

    for i in range(days):
        current_date = start_date + datetime.timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")

        # Weather trend variation across the week (e.g. passing cold front or warm ridge)
        weekly_wave = 2.5 * math_sin(i * 0.8)

        for region in REGIONS:
            base_spec = REGION_BASE_TEMPS.get(region, {"min": 20.0, "max": 28.0})
            jitter = rng.uniform(-1.0, 1.0)

            min_temp = round(base_spec["min"] + weekly_wave + jitter, 1)
            max_temp = round(base_spec["max"] + weekly_wave + rng.uniform(0.2, 1.5), 1)

            # Ensure minT is always less than maxT
            if min_temp >= max_temp:
                min_temp = max_temp - 4.0

            rows.append({
                "regionName": region,
                "dataDate": date_str,
                "minT": min_temp,
                "maxT": max_temp
            })

    return pd.DataFrame(rows)


def math_sin(val: float) -> float:
    """Math sine helper without importing heavy libs."""
    import math
    return math.sin(val)
