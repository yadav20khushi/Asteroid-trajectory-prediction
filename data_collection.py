import requests
import pandas as pd
import os
from dotenv import load_dotenv

try:
    load_dotenv()
    api_url = os.getenv('api_url')
    response = requests.get(api_url)
    response.raise_for_status()
    r = response.json()
    asteroids_data = []
    #Data from the object key -- general data
    asteroids = {'orbit_class_name': r.get('object', {}).get('orbit_class', {}).get('name', 'N/A'),
                 'fullname': r.get('object', {}).get('fullname', 'N/A'), 'pha': r.get('object', {}).get('pha', 'N/A')}
    #Data from orbit key -- general data
    orbit = r.get('orbit', {}).get('elements', [])
    for ele in orbit:
        asteroids[ele.get('name', 'N/A')] = ele.get('value', 'N/A')
    #Data from phy_par key -- general data
    phys_par_list = r.get('phys_par', [])
    valid_par = os.getenv('valid_par')
    if phys_par_list:
        for par in phys_par_list:
            if par.get('name') in valid_par:
                asteroids[par.get('name', 'N/A')] = par.get('value', 'N/A')
    # Data from Radar_obs key -- multiple rows
    radar_obs = r.get('radar_obs', [])
    if radar_obs:
        for obs in radar_obs:
            row = asteroids.copy() #copies general data
            row['freq'] = obs.get('freq', 'N/A')
            row['sigma'] = obs.get('sigma', 'N/A')
            row['value'] = obs.get('value', 'N/A')
            row['epoch'] = obs.get('epoch', 'N/A')
            row['units'] = obs.get('units', 'N/A')
            asteroids_data.append(row) #adds general data + multiple rows
    else:
        asteroids_data.append(asteroids) #adds general data if no radar data found
    #Converting asteroids dict to pd dataframe
    df = pd.DataFrame(asteroids_data)
    df.to_csv('NEA_433.csv', index='False', encoding='utf-8')
    print("Successfully generated CSV")
except requests.exceptions.RequestException as e:
    print(f"Error fetching API data: {e}")