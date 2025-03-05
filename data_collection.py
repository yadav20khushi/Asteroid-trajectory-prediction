import requests
import csv
api_url = "https://ssd-api.jpl.nasa.gov/sbdb.api?neo=1&spk=2000433&full-prec=true&soln-epoch=true&cd-epoch=true&ca-body=Earth&radar-obs=true&phys-par=true"

r = requests.get(api_url).json()
c = csv.writer(open('433_data.csv','w'),lineterminator='\n')
#Data from the object key
c.writerow([r['object']['orbit_class']['name'],r['object']['fullname'],r['object']['pha']])
#Data from Radar_obs key
for i in range(len(r['radar_obs'])):
    c.writerow([r['radar_obs'][i]['freq'],r['radar_obs'][i]['sigma'],r['radar_obs'][i]['value'],r['radar_obs'][i]['epoch'],r['radar_obs'][i]['units']])
#Data from orbit key
for i in range(len(r['orbit']['elements'])):
    c.writerow([r['orbit']['elements'][i]['name'],r['orbit']['elements'][i]['value']])
c.writerow([r['orbit']['data_arc'],r['orbit']['epoch'],r['orbit']['first_obs'],r['orbit']['last_obs'],r['orbit']['moid'],r['orbit']['moid_jup'],r['orbit']['t_jup'],r['orbit']['n_obs_used']])
#Data from phy_par key
name = ['H','G','diameter','GM','density','rot_per','albedo','spec_T','spec_B']
for i in range(len(r['phys_par'])):
    if r['phys_par'][i]['name'] in name:
        c.writerow([r['phys_par'][i]['name'],r['phys_par'][i]['value']])

