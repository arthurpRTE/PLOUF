import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import pandas as pd


class river :
    "creation d'une riviere à partir d'un netCDF de runoff"
    def __init__(self, runoff, debit):
        self.runoffFile = runoff
        self.debitFile = debit
        self.sources = []
        self.initialPoint = []
        self.anthropized_river = []
        self.low_sources = []

    def reduce_domain(self, lonmin, lonmax, latmin, latmax) :
        "reduit le domaine d'etude, attention à ne pas couper les amonts hydrauliques"
        self.runoffFile = self.runoffFile.where((self.runoffFile.lat > latmin) & (self.runoffFile.lat < latmax) & (self.runoffFile.lon > lonmin) & (self.runoffFile.lon < lonmax), drop = True)
        self.debitFile = self.debitFile.where((self.debitFile.latitude > latmin) & (self.debitFile.latitude < latmax) & (self.debitFile.longitude > lonmin) & (self.debitFile.longitude < lonmax), drop = True)
        print("new domain :")
        print("longitude : " + str(lonmin) + " to " + str(lonmax))
        print("latitude : " + str(latmin) + " to " + str(latmax))
        print("runoff File : ")
        print(self.runoffFile.coords.sizes)
        print("debit File :")
        print(self.debitFile.coords.sizes)

    def define_minimal_flow(self, f = 0.1) :
        "construit la riviere pour les ecoulements superieur à l'ecoulement minimal"
        self.minimalFlow = f
        mask = (self.debitFile.dis06.mean(dim="valid_time") > self.minimalFlow)
        self.indices = np.where(mask)
        self.flow = []
        for la, lo in zip(self.indices[0], self.indices[1]) :
            self.flow.append(self.runoffFile.sel(lat = self.debitFile.latitude.values[la], 
                                            lon = self.debitFile.longitude.values[lo], method = "nearest").ldd.values)

    def reverse_flow(self) :
        "reconstruit le flux d'ecoulement (necessaire pour retrouver les sources)"
        self.reversed_flow = {}
        x_step = np.mean(self.runoffFile.lon.values[1:] - self.runoffFile.lon.values[:-1])
        y_step = np.mean(self.runoffFile.lat.values[1:] - self.runoffFile.lat.values[:-1])
        lon_list = self.runoffFile.lon.values
        lat_list = self.runoffFile.lat.values

        for x, y in zip(np.array(lon_list[self.indices[1]])[np.array(self.flow) == 1.], np.array(lat_list[self.indices[0]])[np.array(self.flow) == 1.]) :
            rev_lat = float(self.runoffFile.sel(lat = y - 0.01, lon = x - 0.01, method="nearest").lat.values)
            rev_lon = float(self.runoffFile.sel(lat = y - 0.01, lon = x - 0.01, method="nearest").lon.values)
            self.reversed_flow[(x, y)] = (rev_lon, rev_lat)

        for x, y in zip(np.array(lon_list[self.indices[1]])[np.array(self.flow) == 2.], np.array(lat_list[self.indices[0]])[np.array(self.flow) == 2.]) :
            rev_lat = float(self.runoffFile.sel(lat = y - 0.01, lon = x , method="nearest").lat.values)
            rev_lon = float(self.runoffFile.sel(lat = y - 0.01, lon = x , method="nearest").lon.values)
            self.reversed_flow[(x, y)] = (rev_lon, rev_lat)

        for x, y in zip(np.array(lon_list[self.indices[1]])[np.array(self.flow) == 3.], np.array(lat_list[self.indices[0]])[np.array(self.flow) == 3.]) :
            rev_lat = float(self.runoffFile.sel(lat = y - 0.01, lon = x + 0.01, method="nearest").lat.values)
            rev_lon = float(self.runoffFile.sel(lat = y - 0.01, lon = x + 0.01, method="nearest").lon.values)
            self.reversed_flow[(x, y)] = (rev_lon, rev_lat)

        for x, y in zip(np.array(lon_list[self.indices[1]])[np.array(self.flow) == 4.], np.array(lat_list[self.indices[0]])[np.array(self.flow) == 4.]) :
            rev_lat = float(self.runoffFile.sel(lat = y, lon = x - 0.01, method="nearest").lat.values)
            rev_lon = float(self.runoffFile.sel(lat = y, lon = x - 0.01, method="nearest").lon.values)
            self.reversed_flow[(x, y)] = (rev_lon, rev_lat)

        for x, y in zip(np.array(lon_list[self.indices[1]])[np.array(self.flow) == 6.], np.array(lat_list[self.indices[0]])[np.array(self.flow) == 6.]) :
            rev_lat = float(self.runoffFile.sel(lat = y, lon = x + 0.01, method="nearest").lat.values)
            rev_lon = float(self.runoffFile.sel(lat = y, lon = x + 0.01, method="nearest").lon.values)
            self.reversed_flow[(x, y)] = (rev_lon, rev_lat)

        for x, y in zip(np.array(lon_list[self.indices[1]])[np.array(self.flow) == 7.], np.array(lat_list[self.indices[0]])[np.array(self.flow) == 7.]) :
            rev_lat = float(self.runoffFile.sel(lat = y + 0.01, lon = x - 0.01, method="nearest").lat.values)
            rev_lon = float(self.runoffFile.sel(lat = y + 0.01, lon = x - 0.01, method="nearest").lon.values)
            self.reversed_flow[(x, y)] = (rev_lon, rev_lat)

        for x, y in zip(np.array(lon_list[self.indices[1]])[np.array(self.flow) == 8.], np.array(lat_list[self.indices[0]])[np.array(self.flow) == 8.]) :
            rev_lat = float(self.runoffFile.sel(lat = y + 0.01, lon = x, method="nearest").lat.values)
            rev_lon = float(self.runoffFile.sel(lat = y + 0.01, lon = x, method="nearest").lon.values)
            self.reversed_flow[(x, y)] = (rev_lon, rev_lat)

        for x, y in zip(np.array(lon_list[self.indices[1]])[np.array(self.flow) == 9.], np.array(lat_list[self.indices[0]])[np.array(self.flow) == 9.]) :
            rev_lat = float(self.runoffFile.sel(lat = y + 0.01, lon = x + 0.01, method="nearest").lat.values)
            rev_lon = float(self.runoffFile.sel(lat = y + 0.01, lon = x + 0.01, method="nearest").lon.values)
            self.reversed_flow[(x, y)] = (rev_lon, rev_lat)


    def source(self, initialPoint) :
        "permet de retrouver les sources de l'écoulement"
        initialPoint = (self.runoffFile.sel(lon = initialPoint[0], lat = initialPoint[1], method = "nearest").lon.values,
               self.runoffFile.sel(lon = initialPoint[0], lat = initialPoint[1], method = "nearest").lat.values)
        self.initialPoint.append(initialPoint)
        upperPoint = [up for up, val in self.reversed_flow.items() if val == initialPoint]
        if upperPoint == [] :
            self.sources.append(initialPoint)
        else :
            for p in upperPoint :
                self.source(p)
    

    def lowest_natural_flow(self, aval_limit, stationList, anthropizerList) :
        aval_limit = (self.runoffFile.sel(lon = aval_limit[0], lat = aval_limit[1], method = "nearest").lon.values,
               self.runoffFile.sel(lon = aval_limit[0], lat = aval_limit[1], method = "nearest").lat.values)
        lo_s = abs(self.runoffFile.lon.values[1] - self.runoffFile.lon.values[0])
        la_s = abs(self.runoffFile.lat.values[1] - self.runoffFile.lat.values[0])
        lon_step_dict = {1 : -lo_s, 2 : 0, 3 : lo_s, 4 : -lo_s, 6 : lo_s, 7 : -lo_s, 8 : 0, 9 : lo_s}
        lat_step_dict = {1 : -la_s, 2 : -la_s, 3 : -la_s, 4 : 0, 6 : 0, 7 : la_s, 8 : la_s, 9 : la_s}
        for s in stationList :
            self.anthropized_river.append((float(self.runoffFile.sel(lon = s.longitude, lat = s.latitude, method = "nearest").lon.values),
               float(self.runoffFile.sel(lon = s.longitude, lat = s.latitude, method = "nearest").lat.values)))
            while self.anthropized_river[-1] != aval_limit :
                flow_dir = self.runoffFile.sel(lat = self.anthropized_river[-1][1], 
                                            lon = self.anthropized_river[-1][0], method = "nearest").ldd.values
                
                lon_step = lon_step_dict[int(flow_dir)]
                lat_step = lat_step_dict[int(flow_dir)]
                self.anthropized_river.append((float(self.runoffFile.sel(lon = self.anthropized_river[-1][0] + lon_step, lat = self.anthropized_river[-1][1] + lat_step, method = "nearest").lon.values),
                float(self.runoffFile.sel(lon = self.anthropized_river[-1][0] + lon_step, lat = self.anthropized_river[-1][1] + lat_step, method = "nearest").lat.values)))

        for a in anthropizerList :
            self.anthropized_river.append((float(self.runoffFile.sel(lon = a.up_lon, lat = a.up_lat, method = "nearest").lon.values),
               float(self.runoffFile.sel(lon = a.up_lon, lat = a.up_lat, method = "nearest").lat.values)))
            while self.anthropized_river[-1] != aval_limit :
                flow_dir = self.runoffFile.sel(lat = self.anthropized_river[-1][1], 
                                            lon = self.anthropized_river[-1][0], method = "nearest").ldd.values
                
                lon_step = lon_step_dict[int(flow_dir)]
                lat_step = lat_step_dict[int(flow_dir)]
                self.anthropized_river.append((float(self.runoffFile.sel(lon = self.anthropized_river[-1][0] + lon_step, lat = self.anthropized_river[-1][1] + lat_step, method = "nearest").lon.values),
                float(self.runoffFile.sel(lon = self.anthropized_river[-1][0] + lon_step, lat = self.anthropized_river[-1][1] + lat_step, method = "nearest").lat.values)))

        for p in self.anthropized_river :
            upperPoint = [up for up, val in self.reversed_flow.items() if val == (float(p[0]), float(p[1]))]
            for up in upperPoint :
                if up not in self.anthropized_river :
                    self.low_sources.append(up)


    def display_river(self) :
        for k in self.reversed_flow.keys() :
            plt.arrow(k[0], k[1], (self.reversed_flow[k][0] - k[0])*0.8, (self.reversed_flow[k][1] - k[1])*0.8, ec = "red")

        for s in self.sources :
            plt.plot(s[0], s[1], 'c.', markersize = 15)
        
        for a in self.anthropized_river :
            plt.plot(a[0], a[1], 'b+', markersize = 15)

        for ls in self.low_sources : 
            plt.plot(ls[0], ls[1], 'b*', markersize = 15)
        
        data = self.debitFile.mean(dim = "valid_time")["dis06"].values
        data = np.array(data, dtype=np.float64)
        lat_efas = self.debitFile['latitude'].values
        lat_step = abs(lat_efas[1] - lat_efas[0])
        lon_efas = self.debitFile['longitude'].values
        lon_step = abs(lon_efas[1] - lon_efas[0]) 
        im = plt.imshow(data, extent=[lon_efas.min() - 0.5*lon_step, lon_efas.max() + 0.5*lon_step, lat_efas.min() - 0.5*lat_step, lat_efas.max() + 0.5*lat_step], origin='upper', cmap='jet', alpha=0.3)
        plt.colorbar(im, label = "Q_mean efas (m3/s)")


    def get_coords(self, lon, lat) :
        return (self.runoffFile.sel(lon = lon, lat = lat, method = "nearest").lon.values,
               self.runoffFile.sel(lon = lon, lat = lat, method = "nearest").lat.values)
    

    def simulate(self, stationList, anthropizerList, end_river, show_error = False) :
        self.sim_flow = {}
        stop_point = [(float(self.runoffFile.sel(lon = end_river[0], lat = end_river[1], method = "nearest").lon.values), 
                       float(self.runoffFile.sel(lon = end_river[0], lat = end_river[1], method = "nearest").lat.values))]
        for s in stationList :
            stop_point.append((s.longitude, s.latitude))
        
        for a in anthropizerList :
            stop_point.append((a.up_lon, a.up_lat))
        for river_step in self.anthropized_river :
            self.sim_flow[river_step] = []
        
        for s in self.low_sources :
            self.sim_flow[s] = []
            self.sim_flow[s].append(self.debitFile.sel(longitude = s[0], latitude = s[1], method = "nearest").dis06.values)
            next_step = self.reversed_flow[s]
            while next_step not in stop_point :
                self.sim_flow[next_step].append(self.debitFile.sel(longitude = s[0], latitude = s[1], method = "nearest").dis06.values)
                next_step = self.reversed_flow[next_step]
        
        for s in stationList :
            self.sim_flow[(s.longitude, s.latitude)] = [s.flow]
            if (s.longitude, s.latitude) != end_river :
                next_step = self.reversed_flow[(s.longitude, s.latitude)]
                while next_step not in stop_point :
                    self.sim_flow[next_step].append(s.flow)
                    next_step = self.reversed_flow[next_step]

        for a in anthropizerList : 
            upperPoint = [up for up, val in self.reversed_flow.items() if val == ((a.up_lon, a.up_lat))]
            up_flow = sum([sum(self.sim_flow[upperPoint[i]]) for i in range(len(upperPoint))])
            self.sim_flow[(a.up_lon, a.up_lat)] = [((up_flow + a.up_command - a.up_ecoflow) > 0) * (up_flow + a.up_command - a.up_ecoflow) + a.up_ecoflow]
            if (a.up_lon, a.up_lat) != end_river :
                next_step = self.reversed_flow[(a.up_lon, a.up_lat)]
                while next_step not in stop_point :
                    self.sim_flow[next_step].append(((up_flow + a.up_command - a.up_ecoflow) > 0) * (up_flow + a.up_command - a.up_ecoflow) + a.up_ecoflow)
                    next_step = self.reversed_flow[next_step]

            upperPoint = [up for up, val in self.reversed_flow.items() if val == ((a.do_lon, a.do_lat))]
            up_flow = sum([sum(self.sim_flow[upperPoint[i]]) for i in range(len(upperPoint))])
            self.sim_flow[(a.do_lon, a.do_lat)].append(np.maximum(((up_flow - a.do_ecoflow) > 0) * (up_flow - a.do_ecoflow) + a.do_ecoflow, a.do_command + up_flow))
            if (a.do_lon, a.do_lat) != end_river :
                next_step = self.reversed_flow[(a.do_lon, a.do_lat)]
                while next_step not in stop_point :
                    self.sim_flow[next_step].append(np.maximum(((up_flow - a.do_ecoflow) > 0) * (up_flow - a.do_ecoflow) + a.do_ecoflow, a.do_command + up_flow))
                    next_step = self.reversed_flow[next_step]

        
        if show_error :
            for s in stationList :
                upperPoint = [up for up, val in self.reversed_flow.items() if val == (s.longitude, s.latitude)]
                amt = sum([sum(np.array(self.sim_flow[up])) for up in upperPoint])
                print("_" * 20)
                print("station " + s.name + " :")
                print("mean error : " + str(np.mean(s.flow - amt)))
                print("mean error (EFAS) : " + str(np.mean(s.flow - self.debitFile.sel(longitude = s.longitude, latitude = s.latitude, method = "nearest").dis06.values))) 
                print("RMSE : " + str(sum(((s.flow - amt)**2/len(self.debitFile.valid_time.values))**0.5)))
                print("RMSE (EFAS) : " + str(sum(((s.flow - self.debitFile.sel(longitude = s.longitude, latitude = s.latitude, method = "nearest").dis06.values)**2/len(self.debitFile.valid_time.values))**0.5)))
                plt.figure(figsize=(15, 5))
                plt.plot(self.debitFile.valid_time.values, s.flow - amt)
                plt.title(s.name)
                plt.ylabel("anomalie debit")


        stationResults = []
        anthropizerResults = []
        for s in stationList :
            upperPoint = [up for up, val in self.reversed_flow.items() if val == (s.longitude, s.latitude)]
            amt = sum([sum(np.array(self.sim_flow[up])) for up in upperPoint])
            stationResults.append(pd.Series(amt, index = self.debitFile.valid_time.values, name = s.name))

        for a in anthropizerList :
            upperPoint = [up for up, val in self.reversed_flow.items() if val == (a.up_lon, a.up_lat)]
            amt = sum([sum(np.array(self.sim_flow[up])) for up in upperPoint])
            
            anthropizerResults.append(pd.Series(amt, index = self.debitFile.valid_time.values, name = a.name))
        return (stationResults, anthropizerResults)
    


class station :
    "creation d'une station de mesure sur la riviere"
    def __init__(self, river, lon, lat, measurements, name = " "):
        self.river = river
        self.longitude = float(self.river.get_coords(lon, lat)[0])
        self.latitude = float(self.river.get_coords(lon, lat)[1])
        self.flow = measurements
        self.name = name

    def display_station(self) : 
        plt.plot(self.longitude, self.latitude, 'g.', markersize = 45)

class anthropizer :
    "creation d'une infrasturcture humaine influençant l'écoulement hydraulique naturel de la riviere"
    def __init__(self, river, do_lon, do_lat, do_ecoflow, up_ecoflow, up_command = None, do_command = None, up_lon = None, up_lat = None, name = " "):
        self.river = river
        self.do_lon = float(self.river.get_coords(do_lon, do_lat)[0])
        self.do_lat = float(self.river.get_coords(do_lon, do_lat)[1])
        self.do_ecoflow = do_ecoflow
        self.up_ecoflow = up_ecoflow
        self.name = name
        if up_lon is None :
            self.up_lon = self.do_lon
            self.up_lat = self.do_lat
        else :
            self.up_lon = float(self.river.get_coords(up_lon, up_lat)[0])
            self.up_lat = float(self.river.get_coords(up_lon, up_lat)[1])
        if (up_command is None) & (do_command is not None) :
            self.up_command = -do_command
            self.do_command = do_command
        elif (up_command is not None) & (do_command is None) :
            self.up_command = up_command
            self.do_command = -do_command
        else :
            self.do_command = do_command
            self.up_command = up_command

    def display_anthropizer(self) :
        plt.plot([self.do_lon, self.up_lon], [self.do_lat, self.up_lat], "o:k", markersize = 10)


