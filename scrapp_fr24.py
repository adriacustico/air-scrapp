import json
import random, time, utm
from datetime import datetime
lat_long_airp = {
    'SCL':{
        'City': 'Santiago de Chile',
        'Latitude': -33.4379,
        'Longitude': -70.6503
    },
    'IQQ':{
        'City': 'Iquique',
        'Latitude': -20.5352,
        'Longitude': -70.1813
    },
    'VLC':{
        'City': 'Valencia',
        'Latitude': 39.486998052 ,
        'Longitude': -0.475664764
    },
    'ANF':{
        'City': 'Antofagasta',
        'Latitude': -41.4388,
        'Longitude':-73.0939
    },
    'ZCO':{
        'City': 'Temuco',
        'Latitude': -38.7669,
        'Longitude':-72.6372
    },
    'CCP':{
        'City': 'Concepcion',
        'Latitude': -36.7728,
        'Longitude':-73.0631
    },
    'PMC':{
        'City': 'Puerto Montt',
        'Latitude': -41.4388,
        'Longitude':-73.0939
    }
}

class ScrapAirpGenerator:
    def __init__(self, year, month, day, airportcode='SCL', zoom=10):
        """Arguments:
        year, month, day, IATA airport code (default: SCL), zoom level (default: zoom=10, square of 2x km^2)
        """
        self.histTime = datetime(year, month, day)
        self.airportcode = airportcode
        self.zoom = zoom
    

    def curl_scrapping(self, url): # curl method to get the json data
        import shlex, subprocess
        cmd = '''curl ''' + url
        args = shlex.split(cmd)
        process = subprocess.Popen( args, 
                                    shell=False, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        json_out = json.loads(stdout)
        return json_out # curl response to json

    def plottingArea(self, latitude, longitude, zoom):
        [Easting, Northing, zone_number, zone_letter] = utm.from_latlon(latitude, longitude)
        [east_left,east_right] = [Easting - 1000*zoom, Easting + 1000*zoom]
        [north_up, north_down] = [Northing + 1000*zoom, Northing - 1000*zoom]
        [lat1, lon1] = utm.to_latlon(east_left, north_up, zone_number, zone_letter)
        [lat2, lon2] = utm.to_latlon(east_right, north_down, zone_number, zone_letter)
        return lat1, lat2, lon1, lon2
    
    def file_generator(self): 
        epoch_time = int(time.mktime(self.histTime.timetuple()))
        id_flights = list()
        flight_json={}
        latlon_area=self.plottingArea(lat_long_airp[self.airportcode]['Latitude'], lat_long_airp[self.airportcode]['Longitude'], self.zoom)
        latlon_area=[round(latlon_area,3) for latlon_area in latlon_area]
        for t in range(600,86400,600):
            post_time = epoch_time +t
            pre_time = post_time - 600
            url_list = 'https://data-live.flightradar24.com/zones/fcgi/feed.js?faa=1&bounds='+ str(latlon_area[0])+'%2C'+ str(latlon_area[1]) +'%2C'+ str(latlon_area[2]) +'%2C'+ str(latlon_area[3]) +'&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1%26maxage%3D14400&gliders=1&stats=1&prefetch='+ str(pre_time)+'&history='+str(post_time)
            json_out = self.curl_scrapping(url_list)
            id_flight = list(json_out.keys())
            # if 'full_count' or 'stats' in id_flight, remove it
            id_flight = [id_flight for id_flight in id_flight if id_flight != 'full_count' and id_flight != 'stats' and id_flight != 'version']
            id_flights = list(set(id_flights +id_flight)) # appending id_flight's lists groups to a main id_flights list
        #print(id_flights)
        #false__id = ['full_count', 'version', 'stats']
        #id_flights = [false__id for false__id in id_flights if false__id not in id_flights]
        for flight in id_flights:
            try:
                time.sleep(random.uniform(0.5, 1.5))
                url_flight ='https://data-live.flightradar24.com/clickhandler/?version=1.5&flight=' + flight
                flight_out_json = self.curl_scrapping(url_flight) # flight data as a dictionary

                flight_json.update({flight:flight_out_json}) # appending the flight data to a main dictionary

                print(flight+ " Cargado Correctamente " +  str(id_flights.index(flight)+1) + "/"+ str(len(id_flights))+"\r")
            except:
                print("No se puede completar para " + str(flight)+"\r")
        date=str(self.histTime)
        filename_out = self.airportcode+'_' + date[0:10]+ '_data.json'
        with open(filename_out, 'w') as outfile:
            json.dump(flight_json, outfile)
        print(filename_out + ' guardado con exito')

def main():
    file=ScrapAirpGenerator(2022, 1,4, airportcode='SCL', zoom=10)
    file.file_generator()

if __name__ == '__main__':
    main()

