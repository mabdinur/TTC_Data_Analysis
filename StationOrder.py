from readcsv import Readcsv

class StationOrder(Readcsv):
    nstation_dict = dict()
    pstation_dict = dict()

    @classmethod
    def get_next(cls, station):
        if cls.nstation_dict.__len__() == 0:
            cls.__create_dict()
        return cls.nstation_dict[station]

    @classmethod
    def get_previous(cls, station):
        if cls.pstation_dict.__len__() == 0:
            cls.__create_dict()
        return cls.pstation_dict[station]

    @classmethod
    def __create_dict(cls):
        stationSpecs = cls.read_station_table("NTAS CSS\\StationMap.csv")
        for line in stationSpecs:
            station = line[0].strip()
            stationNext = line[3].strip()
            cls.nstation_dict[station] = stationNext
            cls.pstation_dict[stationNext] = station


if __name__ == "__main__" :
    print(Readcsv.create_dest())
