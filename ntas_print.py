from ntas_math import Nmath
import csv
import matplotlib.pyplot as plt
from ntas_parse import ParseNtasLogs


class ExportLogs(ParseNtasLogs):

    exportFolder = "DAY" + "-Station_figures" + "\\" + day+ "-graph-data-4.csv"
    def __init__(self, dirlist = None):
        if dirlist is None:
            self.dirlist = ["F:\\NTAS_Log-Tues-1107-1.zip", "F:\\NTAS_Log-Tues-1114-1.zip","F:\\NTAS_Log-Tues-1114-2.zip"]
        super().__init__()

    def process_data(self, outputfile=exportFolder ):
        for dir1 in self.dirlist:
            self.read_zipfolder(dir1)
        self.create_csv_graphs(outputfile, self.__test_print, header=True)

    def create_csv_graphs(self, outputfile, write_to_file, header=True):
        myfile = open(outputfile, 'w', newline="")
        wr = csv.writer(myfile)
        if header:
            wr.writerow(["Station", "Prediction(minutes)", "Avg Error(Actual - Prediction)", "Standard Deviation",
                         "List of Error values"])
        write_to_file(wr)
        myfile.close()

    def __test_print(self, wr):
        self.predict["All"] = self.__set_all_stations()
        for key in self.predict.keys():
            print(key)
            errors = self.predict[key]
            nmath = Nmath()
            nmath.set_mean__sdeviation(errors)
            for all_keys in nmath.avg.keys():
                li_err = nmath.field_list(errors[all_keys], "prediction")
                wr.writerow([key, all_keys, nmath.avg[all_keys], nmath.sd[all_keys], li_err])
                if self.test_station in key:
                    print(all_keys,nmath.sd[all_keys], nmath.avg[all_keys], li_err)
            self.create_graph(nmath.avg, nmath.sd, key)

    def __set_all_stations(self):
        all_predictions = dict()
        predictions_dict = self.predict
        for station in predictions_dict.keys():
            for arriving_in in predictions_dict[station]:
                for obj in predictions_dict[station][arriving_in]:
                    try:
                        all_predictions[arriving_in].append(obj)
                    except KeyError:
                        all_predictions[arriving_in] = [obj]
        return all_predictions

    def create_graph(self, avg, standard_deviation, key):
        if len(avg) > 0:
            x, y = zip(*avg.items())
            fig = plt.figure()
            for int1 in avg.keys():
                plt.errorbar(int1, avg[int1], yerr=standard_deviation[int1], fmt='none', ecolor='r')
            plt.scatter(x, y)
            plt.ylim([-3, 5])

            if max(x) < 5:
                plt.xlim([0.5, 6])
            else:
                plt.xlim([0.5,max(x) + 1])

            plt.xlabel("Arrival Time Prediction(rounded to nearest Minute)")
            plt.ylabel("Prediction Error (Actual - Expected)")
            plt.title(key)
            fig.canvas.set_window_title(self.day + "Arrival Predictions")

            fig.savefig(self.day+"-Station_figures//" + "Station__" + key)
            fig.clear()
            plt.close()

if __name__ == "__main__":
    Ntas = ExportLogs()
    Ntas.process_data()