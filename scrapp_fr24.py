import json
import random, time, os
from datetime import datetime, date

class ScrapAirpGenerator:
    def __init__(self, dtime):
        self.histTime = dtime

    def curl_scrapping(self, url):
        import shlex, subprocess
        cmd = '''curl ''' + url
        args = shlex.split(cmd)
        process = subprocess.Popen( args, 
                                    shell=False, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        json_out = json.loads(stdout)
        return json_out
   
    def file_generator(self):
        epoch_time = int(time.mktime(self.histTime.timetuple()))
        id_flights = list()
        flight_json={}
        for t in range(600,86400,600):
            post_time = epoch_time +t
            pre_time = post_time - 600
            url_list = 'https://data-live.flightradar24.com/zones/fcgi/feed.js?faa=1&bounds=-30.441%2C-42.709%2C-78.132%2C-64.708&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1%26maxage%3D14400&gliders=1&stats=1&prefetch='+ str(pre_time)+'&history='+str(post_time)
            json_out = self.curl_scrapping(url_list)
            id_flight = list(json_out.keys())
            id_flights = list(set(id_flights +id_flight))
        #print(id_flights)

        for flight in id_flights:
            if flight == 'full_count' or flight == 'version':
                pass
            else:
                try:
                    time.sleep(random.uniform(0.5, 1.5))
                    url_flight ='https://data-live.flightradar24.com/clickhandler/?version=1.5&flight=' + flight
                    flight_out_json = self.curl_scrapping(url_flight) # diccionario con datos de vuelo

                    flight_json.update({flight:flight_out_json})

                    print(flight+ ' Cargado Correctamente ' +  str(id_flights.index(flight)+1) + '/'+ str(len(id_flights))+'\r')
                except:
                    print("No se puede completar para " + str(flight))
        date=str(self.histTime)
        filename_out = date[0:10]+ '_data.json'
        with open(filename_out, 'w') as outfile:
            json.dump(flight_json, outfile)
        print(filename_out + ' guardado con exito')

def main():
    dtime = datetime(2021, 12, 16)
    file=ScrapAirpGenerator(dtime)
    file.file_generator()

if __name__ == '__main__':
    main()
