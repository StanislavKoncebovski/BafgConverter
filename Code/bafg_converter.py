import datetime
import json
import pickle
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
import glob

class BafgConverter:
    pass

class BafgConverter:
    '''
    Conversion of hydrological data provided by bafg.de (https://www.bafg.de/) from their XML (WML) format into
    pandas Series and basic manipulations.
    '''
    #region Class Constants
    NAMESPACES = {'wml2': "http://www.opengis.net/waterml/2.0", "om": "http://www.opengis.net/om/2.0"}
    #endregion

    #region Initialization
    def __init__(self):
        # Dictionary of dataframes over single gauges, the key being the gauge's grid number,
        # the value a dataframe with columns "Year", "Month", "Discharge" (m3/s).
        self._data = {}

        # pandas dataframe with columns: 'GridNo', 'River', 'Station'
        self._gauges = None
    #endregion

    #region Properties
    @property
    def gauges(self):
        '''
        Gets the gauges list
        :return:
        '''
        return self._gauges

    @property
    def data(self):
        '''
        Gets
        :return:
        '''
        return self._data

    def get_time_series(self, grid_number: str) -> Optional[pd.DataFrame]:
        '''
        Returns the discharge dataframe for a gauge.
        :param grid_number: The grid number of the gauge.
        :return: The gauge's discharge dataframe, if found, otherwise None.
        '''
        if grid_number not in self._data:
            return None

        df = self._data[grid_number]
        return df
    # endregion

    #region Public Features
    def create_gauge_list(self, file_name: str):
        '''
        Creates the gauges dataframe from a file (geojson).
        :param file_name: The file name to create gauges from.
        :return: None.
        '''
        with open(file_name) as file:
            doc = json.load(file)

        gauges = []

        for feature in doc['features']:
            attributes = feature['attributes']
            grid_number = int(attributes['grdc_no'])
            river = attributes['river'].title()
            station = attributes['station'].title()
            gauges.append((grid_number, river, station))

        self._gauges = pd.DataFrame(gauges, columns=['GridNo', 'River', 'Station'])

    def create_gauge_dataframe(self, file_name: str) -> Optional[pd.DataFrame]:
        '''
        Creates a pandas dataframe from a WML file, and adds it to the dataframe dictionary with its grid number as the key.
        :param file_name: the name of the fle.
        :return: A pandas dataframe, if successful, otherwise None.
        '''
        root = ET.parse(file_name).getroot()

        node_member = root.find("wml2:observationMember", BafgConverter.NAMESPACES)
        node_observation = node_member.find("om:OM_Observation", BafgConverter.NAMESPACES)
        node_feature = node_observation.find("om:featureOfInterest", BafgConverter.NAMESPACES)

        gauge_id = node_feature.attrib['{http://www.w3.org/1999/xlink}href']
        gauge_name = node_feature.attrib['{http://www.w3.org/1999/xlink}title']

        print(gauge_id, gauge_name.title())

        node_result = node_observation.find("om:result", BafgConverter.NAMESPACES)
        node_time_series = node_result.find("wml2:MeasurementTimeseries", BafgConverter.NAMESPACES)

        data = []

        for node_point in node_time_series.findall("wml2:point", BafgConverter.NAMESPACES):
            node_measurement = node_point.find("wml2:MeasurementTVP", BafgConverter.NAMESPACES)
            node_time = node_measurement.find("wml2:time", BafgConverter.NAMESPACES)
            node_value = node_measurement.find("wml2:value", BafgConverter.NAMESPACES)

            time = datetime.fromisoformat(node_time.text[:10])
            value = float(node_value.text) if node_value.text is not None else np.NaN

            data.append((time.year, time.month, value))

        df = pd.DataFrame(data, columns=['Year', 'Month', 'Discharge'])
        self._data[gauge_id] = df
        return df

    def create_gauge_dataframes(self, flie_names: list[str]):
        '''
        Creates the collection of gauge dataframes from a list of files (WML), and adds them to the dataframe dictionary
        with their grid numbers as the keys.
        :param flie_names: The list of file names to create from.
        :return: None.
        '''
        for file_name in flie_names:
            print(file_name)
            self.create_gauge_dataframe(file_name)

    def create_gauge_dataframes_from_folder(self, folder: str):
        '''
        Creates the collection of gauge dataframes from a directory, and adds the dataframes to the dataframe dictionary.
        :param folder: The name of the folder.
        :return: None.
        '''
        files = glob.glob(f"{folder}\\*.wml")
        self.create_gauge_dataframes(files)

    def gauges_to_csv(self, csv_file_name: str, sep: str = ','):
        '''
        Writes the gauges as a cvs file.
        :param csv_file_name: The file name to save under.
        :param sep: CSV Separator, default = ','.
        :return: None.
        '''
        self._gauges.to_csv(csv_file_name, sep=sep)

    def gauge_discharges_to_csv(self, grid_number: str, csv_file_name: str, sep: str = ','):
        '''
        Writes the discharges of a gauge to CSV.
        :param grid_number: The grid number of the gauge.
        :param csv_file_name: The file to write to.
        :param sep: CSV Separator, default = ','.
        :return: None.
        '''
        if grid_number not in self._data:
            return

        df = self._data[grid_number]
        df.to_csv(csv_file_name, sep)

    def pickle(self, pickle_file_name: str):
        '''
        Pickles the whole instance.
        :param pickle_file_name: The name of the file to pickle to.
        :return: None.
        '''
        with open(pickle_file_name, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def unpickle(cls, pickle_file_name: str) -> Optional[BafgConverter]:
        '''
        Creates an instance of BafgConverter from a pickle file.
        :param pickle_file_name: The name of the file to unpickle from.
        :return: An instance of BafgConverter, if successful, otherwise None.
        '''
        try:
            with open(pickle_file_name, "rb") as file:
                return pickle.load(file)
        except:
            return None
    #endregion

if __name__ == '__main__':
    converter = BafgConverter()

    # # create gauge list
    # gauges_file_name = r"../Data/stationbasins.geojson"
    # converter.create_gauge_list(gauges_file_name)
    # print(converter.gauges)
    #
    # # create station dataframes
    # folder = "../Data/"
    # converter.create_gauge_dataframes_from_folder(folder)
    #
    # df = converter.get_time_series('2316200')
    #
    # print(df)
    #
    # converter.gauges_to_csv("gauges.csv")
    # converter.gauge_discharges_to_csv('2316200', 'discharges_2316200.csv')
    #
    # converter.pickle("ferghana.pkl")

    ferghana = BafgConverter.unpickle("ferghana.pkl")

    print(ferghana.gauges)
    print(ferghana.get_time_series('2416810'))