#import sqlite3
#from DataBaseReader import MyDatabase


def update_predictions():
    pass
    #initalize Current predictions
    #Initalize db with information we could use
    #create a dictionary mapping current station to next stations
    #Bind endpoints to a predciction array element
    #listen for updates
    #filter out everything except train arrivals
    #Use boolean variables to poll ie. if an incoming message contains "Arrived" set store_train to true
    #store train number, arrival station and time stamp in station ID in 2D ORDERED dictionary {trainNum: {station : datetime} }
    #if dict_stationOrder[station_now] == station_next: //station_now can be found in the request dictionary
    # append station to train list
    #if station_now == get_prevstation(odict_station_request): // DO NOTHING
    #
    #update Current predictions
    #


#def get_prevstation(odict_train)   #odict_station_request['trainNum']
    #last_station = next(reversed(odict_train))
    #return last_station
