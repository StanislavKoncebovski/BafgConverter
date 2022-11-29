# BAFG Converter
## Motivation 
The goal of this toy project was to convert monthly discharge data of certain hydrological stations from a format in which they were downloaded from the website of BAFG = Bundesanstalt für Gewässerkunde (Koblenz, Germany), to pandas dataframes (to be able to extract information and manipulate the data in a civilized way).

## Scope
The 28 hydrological stations under consideration are geographically within the basin of the Syr Darya river in Central Asia (selected not randomly, but because of an earlier acqaintance).

## Links
* https://www.bafg.de/GRDC/EN/01_GRDC/13_dtbse/database_node.html (Global Runoff Data Base by BAFG) 
* https://www.bafg.de/GRDC/EN/02_srvcs/21_tmsrs/210_prtl/prtl_node.html (Discharge download page by BAFG)
* https://www.compositerunoff.sr.unh.edu/ (Another hydrological source, less informative than BAFG)

## Contents
* `Code/bafg_converter.py`: contains class BafgConverter
* `Data/ferghana.pkl`: the gauge list and the collection of discharge dataframes in a single pickle file.

## How To:
### Load an instance of ``BafgConverter`` from pickle
```
ferghana = BafgConverter.unpickle("ferghana.pkl")
# provided that ferghana.pkl is in the working directory, otherwise replace with correct data path
```
### Extract discharge data for a station
```
grdc_number = '2416202'
discharges = ferghana.get_time_series(grdc_number)

print(discharges) # prints the table of discharges of the Syr Darya river at station Kal.
```
### Create similar objects for other basins:
1. Download zip file with discharges and gauge description from https://www.bafg.de/GRDC/EN/02_srvcs/21_tmsrs/210_prtl/prtl_node.html
2. Unpack the zip file into a directory. The files are "not pretty", so that Python's ElementTree can have problems with reading them. In this case, you will need to prettify the XML manually (I did it in Visual Studio 2019).
3. If the path to the directory with the files is ``path``:
   1. Create the gauge list using
      ````
      converter = BafgConverter()
      converter.create_gauge_list(f"{path}/stationbasins.geojson")
      ````
      
   2. Create the discharge dataframes using 
      ```
      converter.create_gauge_dataframes_from_folder(path)
      ```
      
   3. Ready (hopefully) -- play with your data
