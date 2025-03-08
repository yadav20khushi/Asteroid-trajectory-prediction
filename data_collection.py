import numpy as np
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


class DataCollection:
    def __init__(self, spk_start: int, spk_limit: int):
        self.spk_range = range(spk_start, spk_limit + 1)

    def looping_spk_range(self):
        for spk in self.spk_range:
            self.fetch_asteroid_data(spk)

    @staticmethod
    def create_csv(spk: int, data: list):
        if not data:
            return
        # Converting asteroids dict to pd dataframe and then to csv
        expected_columns = ["orbit_class_name", "fullname", "spk_id", "pha", "e", "q", "tp", "om", "w", "i",
                            "H", "G", "diameter", "GM", "density", "rot_per", "albedo", "spec_T", "spec_B"
                            ]
        df = pd.DataFrame(data)
        df = df.reindex(columns=expected_columns)
        df = df.fillna(np.nan)
        file_exist = os.path.isfile('Asteroid_Data.csv')
        df.to_csv('Asteroid_Data.csv', index=False, encoding='utf-8', mode='a', header=not file_exist)
        print(f"Successfully added asteroid data for spk = {spk}")

    @staticmethod
    def create_csv_radar(spk: int, data: list):
        if not data:
            return
        # Converting asteroids dict to pd dataframe and then to csv
        expected_columns = ["orbit_class_name", "fullname", "spk_id", "pha", "e", "q", "tp", "om", "w", "i",
                            "H", "G", "diameter", "GM", "density", "rot_per", "albedo", "spec_T", "spec_B", "freq",
                            "sigma",
                            "value", "epoch", "units"
                            ]
        df = pd.DataFrame(data)
        df = df.reindex(columns=expected_columns)
        df = df.fillna(np.nan)
        file_exist = os.path.isfile('Asteroids_Data_radar_obs.csv')
        df.to_csv('Asteroids_Data_radar_obs.csv', index=False, encoding='utf-8', mode='a', header=not file_exist)
        print(f"Successfully added asteroid with radar_obs for spk = {spk}")

    def fetch_asteroid_data(self, spk: int):
        try:
            api_url = f"https://ssd-api.jpl.nasa.gov/sbdb.api?spk={spk}&full-prec=true&soln-epoch=true&cd-epoch=true&ca-body=Earth&radar-obs=true&phys-par=true"
            response = requests.get(api_url)
            response.raise_for_status()
            r = response.json()
            if r.get('message') == "specified NEO was not found":
                return
            else:
                asteroids_data = []
                #Data from the object key -- general data
                asteroids = {'orbit_class_name': r.get('object', {}).get('orbit_class', {}).get('name', 'N/A'),
                             'fullname': r.get('object', {}).get('fullname', 'N/A'),
                             'spk_id': r.get('object', {}).get('spkid', 'N/A'),
                             'pha': r.get('object', {}).get('pha', 'N/A')}
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
                        row = asteroids.copy()  #copies general data
                        row['freq'] = obs.get('freq', 'N/A')
                        row['sigma'] = obs.get('sigma', 'N/A')
                        row['value'] = obs.get('value', 'N/A')
                        row['epoch'] = obs.get('epoch', 'N/A')
                        row['units'] = obs.get('units', 'N/A')
                        asteroids_data.append(row)  #adds general data + multiple rows
                    self.create_csv_radar(spk, asteroids_data)
                    return
                else:
                    asteroids_data.append(asteroids)
                self.create_csv(spk, asteroids_data)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching API data: {e}")


if __name__ == "__main__":
    obj = DataCollection(spk_start=2000101, spk_limit=2000200)
    obj.looping_spk_range()
