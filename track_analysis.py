import pandas as pd
import matplotlib.pyplot as plt
import utm
from mpl_toolkits.mplot3d import Axes3D
import airport_coord

# function to convert lat/lon to UTM
lat_long_airp = airport_coord.lat_long_airp
code ='SCL'

def uuttmm(fila):
    [Easting, Northing, zone_number, zone_letter] = utm.from_latlon(fila['lat'], fila['lng'])
    return (Easting, Northing, zone_number, zone_letter)
# Function to create a plotting area in xN meters from center point (Easting, Northing)
def plotting_area(Easting, Northing, xN):
    east_left = Easting - xN
    east_right = Easting + xN
    north_up = Northing + xN
    north_down = Northing - xN
    return (east_left, east_right, north_up, north_down)

def iter_df(func):
    def wrapper(df, index, key='trail'): #Parameters from the function plot_trail()
        for i in index:
            a=df.loc[i] # a is a row of the main dataframe
            try:
                partial_df=pd.DataFrame(a[key])   
            except ValueError:
                print('No data for flight ' + i)
                continue

            if partial_df.empty:
                print("Empty trail: "+ i)
                continue
            else:
                params = func(partial_df, ax)      
        return params
    return wrapper



ax = plt.figure().add_subplot(projection='3d')  
@iter_df
def plot_trail(partial_df, ax):
    # Append columns with the UTM coordinates
    coord_list = partial_df.apply(uuttmm, axis=1).to_list()
    utm_coord=pd.DataFrame(coord_list, columns=['Easting', 'Northing', 'Zone_N', 'Zone_L'])
    utm_trail_coord=pd.concat([partial_df, utm_coord], axis=1)
    # Add data to plot
    (Easting, Northing, zone_number, zone_letter) = utm.from_latlon(lat_long_airp[code]['Latitude'], 
                                                                    lat_long_airp[code]['Longitude'])
    (east_left, east_right, north_up, north_down)=plotting_area(Easting, Northing, 40000)
    result_df=utm_trail_coord[(utm_trail_coord['Easting']>east_left) & (utm_trail_coord['Easting']<east_right) 
            & (utm_trail_coord['Northing']>north_down) & (utm_trail_coord['Northing']<north_up)]
    sc= ax.plot(result_df.Easting, result_df.Northing, result_df.alt*0.3048)
    plot_params = {'sc':sc, 'east_left':east_left, 'east_right':east_right, 'north_up':north_up, 'north_down':north_down}
    return plot_params

def partialize_df(df, index, key = 'aircraft'):
    ind = pd.DataFrame(index, columns=['Flight_ID'])
    partial_df = pd.json_normalize(df.loc[:,key])
    return pd.concat([ind,partial_df], axis=1)

def flight_operation(df, index):
    airport_list = partialize_df(df, index, key = 'airport').dropna(axis =1, how='all')
    arrival = airport_list[airport_list['destination.code.icao'].isin(['SCEL'])]
    from_north = arrival[arrival['origin.position.latitude'] > arrival['destination.position.latitude']]
    from_south = arrival[arrival['origin.position.latitude'] < arrival['destination.position.latitude']]
    departure = airport_list[airport_list['origin.code.icao'].isin(['SCEL'])]
    to_north = departure[departure['origin.position.latitude'] < departure['destination.position.latitude']]
    to_south = departure[departure['origin.position.latitude'] > departure['destination.position.latitude']]
    overflight = airport_list[~airport_list['destination.code.icao'].isin(['SCEL']) & ~airport_list['origin.code.icao'].isin(['SCEL'])]
    return [from_north['Flight_ID'], from_south['Flight_ID'], to_north['Flight_ID'], to_south['Flight_ID'], overflight['Flight_ID']]

def aircraft_model(df, index):
    aircraft_list = partialize_df(df, index, key = 'aircraft')
    return aircraft_list

class TrackAnalysis:
    def __init__(self, file_in):
        self.file_in = file_in

    def read_file(self):
        # Creating a main dataframe from the json file
        df = pd.read_json(self.file_in, orient='index')
        index=list(df.index.values) # list of flight ids
        return df, index

def main():
    filename = 'SCL_2022-01-04_data.json' #  <= Filename
    track = TrackAnalysis(filename)
    df, index = track.read_file()
    #plot_params = plot_trail(df, index)
    #plt.xlim(plot_params['east_left'], plot_params['east_right'])
    #plt.ylim(plot_params['north_down'], plot_params['north_up'])
    #plt.show()
    index_mat = flight_operation(df, index)
    inx1 = index_mat[0] # 0=from_north, 1=from_south, 2=to_north, 3=to_south, 4=overflight
    # count values in index_mat
    
    plot_params = plot_trail(df, inx1)
    plt.xlim(plot_params['east_left'], plot_params['east_right'])
    plt.ylim(plot_params['north_down'], plot_params['north_up'])
    plt.show()
    



if __name__ == '__main__':
    main()