from destionations import Destination


class Readcsv():

    @classmethod
    def create_dest(cls):
        stationSpecs = cls.read_station_table("NTAS CSS\\StationMap.csv")
        dest_dict = dict()
        for line in stationSpecs:
            dest1 = line[9].strip()
            if dest1 != '':
                di = {dest1: Destination()}
            dest2 = line[10].strip()
            if dest2 != '':
                di[dest2] = Destination()
            dest3 = line[11].strip()
            if dest3 != '':
                di[dest3] = Destination()
            dest_dict[line[0]] = di
        return dest_dict

    @classmethod
    def read_station_table(cls, path):
        stationSpecs = [dataline.strip().split(',') for dataline in open(path, 'r')]
        stationSpecs.pop(0)
        return stationSpecs

if __name__ == "__main__":
    print(Readcsv.create_dest())
