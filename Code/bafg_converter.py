import datetime
import json
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET

from gauge import Gauge


class BafgConverter:
    '''
    Conversion of hydrological data provided by bafg.de (https://www.bafg.de/) from their XML (WML) format into
    pandas Series and basic manipulations.
    '''

    #region Class Constants
    NAMESPACES = {'wml2': "http://www.opengis.net/waterml/2.0", "om": "http://www.opengis.net/om/2.0"}
    #endregion

    def __init__(self):
        self._data = []
        self._gauges = None


    @property
    def gauges(self):
        return self._gauges

    #region Public Features
    def create_gauge_dataframe(self, file_name: str) -> Optional[pd.DataFrame]:
        '''
        Creates a pandas series from a BFG WML file
        :param file_name: the name of the fle.
        :return: A pandas series, if successful, otherwise None.
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

        self._data = []

        for node_point in node_time_series.findall("wml2:point", BafgConverter.NAMESPACES):
            node_measurement = node_point.find("wml2:MeasurementTVP", BafgConverter.NAMESPACES)
            node_time = node_measurement.find("wml2:time", BafgConverter.NAMESPACES)
            node_value = node_measurement.find("wml2:value", BafgConverter.NAMESPACES)

            time = datetime.fromisoformat(node_time.text[:10])
            value = float(node_value.text) if node_value.text is not None else np.NaN

            self._data.append((time.year, time.month, value))

        return pd.DataFrame(self._data, columns=['Year', 'Month', 'Discharge'])

    def create_gauge_list(self, file_name: str):
        with open(file_name) as file:
            doc = json.load(file)

        gauges = []

        for feature in doc['features']:
            attributes = feature['attributes']
            gauge = Gauge(grid_number=int(attributes['grdc_no']), river=attributes['river'].title(), station=attributes['station'].title())
            gauges.append(gauge)

        self._gauges = pd.DataFrame(gauges, columns=['GridNo', 'River', 'Station'])

    #endregion

if __name__ == '__main__':
    converter = BafgConverter()
    # file_name = r"C:\Users\Stan\Desktop\-999_2316200_Q_Merge.Months.wml"
    #
    # discharges = converter.create_gauge_dataframe(file_name)
    #
    # print(discharges)

    gauges_file_name = r"C:\Users\Stan\Desktop\stationbasins.geojson"
    converter.create_gauge_list(gauges_file_name)

    print(converter.gauges)