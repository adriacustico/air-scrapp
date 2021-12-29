import json
import pandas as pd
import matplotlib.pyplot as plt
import utm
from mpl_toolkits.mplot3d import Axes3D

class TrackAnalysis:
    def __init__(self, file_in):
        self.file_in = file_in
    # function to convert lat/lon to UTM
    def uuttmm(self, fila):
        [Easting, Northing, zone_number, zone_letter] = utm.from_latlon(fila['lat'], fila['lng'])
        return (Easting, Northing, zone_number, zone_letter)
    # Function to create a plotting area in xN meters from center point (Easting, Northing)
    def plottingArea(self, Easting, Northing, xN):
        east_left = Easting - xN
        east_right = Easting + xN
        north_up = Northing + xN
        north_down = Northing - xN
        return (east_left, east_right, north_up, north_down)

    def read_file(self):
        # Creating a main dataframe from the json file
        df = pd.read_json(self.file_in, orient='index')
        index=list(df.index.values) # list of flight ids

        ax = plt.figure().add_subplot(projection='3d')
    
        for i in index:
            a=df.loc[i] # a is a row of the main dataframe
            try:
                trail_df=pd.DataFrame(a['trail'])   
            except ValueError:
                print('No trail data for flight ' + i)
                continue
            if trail_df.empty:
                print("Empty trail: "+ i)
                continue
            else:
                [sc, east_left, east_right, north_up, north_down] = self.plot_trail(trail_df, ax)

        plt.xlim(east_left, east_right)
        plt.ylim(north_down, north_up)
        plt.show()


    def plot_trail(self, trail_df, ax):
        # Append columns with the UTM coordinates
        coord_list = trail_df.apply(self.uuttmm, axis=1).to_list()
        c=pd.DataFrame(coord_list, columns=['Easting', 'Northing', 'Zone_N', 'Zone_L'])
        e=pd.concat([trail_df, c], axis=1)
        # Example of airport data
        airport_place = {
            'Code':{
                'SCL':{
                    'City': 'Santiago de Chile',
                    'Latitude': -33.4379,
                    'Longitude': -70.6503
                },
                'IQQ':{
                    'City': 'Iquique',
                    'Latitude': -20.23,
                    'Longitude': -70.13
                }
            }
        }
        # Add data to plot
        (Easting, Northing, zone_number, zone_letter) = utm.from_latlon(airport_place['Code']['SCL']['Latitude'], airport_place['Code']['SCL']['Longitude'])
        (east_left, east_right, north_up, north_down)=self.plottingArea(Easting, Northing, 40000)
        result_df=e[(e['Easting']>east_left) & (e['Easting']<east_right) & (e['Northing']>north_down) & (e['Northing']<north_up)]
        sc= ax.plot(result_df.Easting, result_df.Northing, result_df.alt*0.3048)
        return [sc, east_left, east_right, north_up, north_down]
        
    


def main():
    file_in = '2021-12-15_data.json' #  <= Filename
    track = TrackAnalysis(file_in)
    track.read_file()

if __name__ == '__main__':
    main()