# Workflow for Metadata and Quality Control
wsn_filters is a process workflow for automatic weather station data that focuses on gathering metadata in config files and [meteoIO](https://gitlabext.wsl.ch/snow-models/meteoio) from SLF for producing a fast quality-control metadata-rich netcdf file. This project is part of [UiO Hive](https://uiohive.github.io/Hive/) that develops IoT technologies, AI/ML to solve data challenges, and shares knowledge across relevant interdisciplinary domains.

## Structure
- ```qc_*.py```: workflow specific to each network such as ```qc_main.py``` for the wsn network in Svalbard.
- ```config_*.yml```: YAML config file specific to each network such as ```config_wsn_KNG.yml``` for the Kongsvegen network
- ```ini/```: folder with templates and processed INI files containing parameters required by meteoIO. First, the parameter fields in an INI template are defined manually for each network. Running the ```qc_main.py``` pipeline, node-dependent parameters are added from the YAML config file to the template. The then new INI file is saved with the node name for backup and copied to the ```io.ini``` file required by the meteoIO processing command ```data_converter```.
- ```data/```: folder storing original data in csv file
- ```data_qc/```: folder for the quality-controlled metadata-rich netcdf output file
- ```log/```: log folder
- ```wsn_main.ipynb```: a jupyter notebooks containing earlier versions of the code and plots
- ```MeteoIO_test.ipynb```: a jupyter notebooks containing earlier versions of the meteoIO pipeline
- ```notebook_test_filter.ipynb```: a jupyter notebooks containing earlier versions of quality control codes

## Application 
The pipeline is designed for weather data from two networks of automatic weather stations installed in Svalbard as described in the [Hive documentation](https://hive-wireless-sensor-network.readthedocs.io/en/latest/). The code is developed to be transferrable to other locations and networks such as the one in Finse, Norway, also maintained by the University of Oslo.

### Command line usage
The pipeline requires the config file as input parameter and can be ran as followed: 
#### Wireless Sensor Network at Kongsvegen
```
python qc_main.py -nc config_wsn_KNG.yml
```
#### Wireless Sensor Network at Midtre Lovenbreen
```
python qc_main.py -nc config_wsn_MLB.yml
```
#### AWS at Austfonna
```
python qc_austfonna.py -nc config_austfonna_ETON2.yml
```

## Required installation
### meteIO compilation
A compilitation guide is available on [meteoIO's wiki](https://gitlabext.wsl.ch/snow-models/meteoio/-/wikis/Compiling-MeteoIO) and we provide a short summary here.
#### Dependencies:
- cmake or cmake-gui
- g++

#### Installation code
```
# master
git clone https://gitlabext.wsl.ch/snow-models/meteoio.git
cd meteoio

# turn ON netcdf option with sed -i.bak 's/SET(PLUGIN_NETCDFIO OFF/SET(PLUGIN_NETCDFIO ON/g' CMakeLists.txt or 
ccmake .      

# install meteoio
make 
sudo make install
  
# install examples including data_converter
cd doc/examples
cmake .
make
```
#### Installation test
```
# cd doc/examples, if you are not in this folder already

# run the test
./data_converter 2008-12-01T00:00:00 2008-12-31T23:00 60

# expected result
> Powered by MeteoIO 3.00 compiled on Dec  3 2021 12:49:20
> Reading data from 2008-12-01T00:00:00 to 2008-12-31T23:00:00
> Writing output data
> Done!! in 0.146223 s
```
You can then run the processing code described above in [Application](https://github.com/UiOHive/wsn_filters#application)

## References
Documentation about Hive is available:
- [Hive's project website](https://uiohive.github.io/Hive/)
- [Hive's wireless sensor network documentation](https://hive-wireless-sensor-network.readthedocs.io/en/latest/)
- [UiOHive's github](https://github.com/UiOHive)

You can find a complete description of MeteoIO in:
- [meteoIO's wiki](https://gitlabext.wsl.ch/snow-models/meteoio/-/wikis)
- [meteoIO's github](https://gitlabext.wsl.ch/snow-models/meteoio)
- Bavay, M. and Egger, T., "MeteoIO 2.4.2: a preprocessing library for meteorological data", Geosci. Model Dev., 7, 3135-3151, doi:10.5194/gmd-7-3135-2014, 2014 
and some example applications in: 
- Bavay, M., Fiddes, J., Fierz, C., Lehning, M., Monti, F. and Egger, T., "The METEOIO pre-processing library for operational applications", In International Snow Science Workshop ISSW, Innsbruck, Austria, 2018.

## YAML metadata field description
### Network
```YAML
network:
  name: "string" "Name of the network" "Midtre Lovenbreen"
  owner: "string" "Name of the owner of the nertwork" "NPI"
  country: "string" "Country where the network is installed" "Svalbard"  
  description: "string" "Description of the network" "Wireless Sensor Network on the Midtre Lovenbreen glacier in Svalbard"
  date_installation: "date" "Date of the original installation of the network" "2021-04-01"
  date_update: "date" "Date of the last maintenance of the network" "2022-05-10"
  year_hydro: "date array" "Date of the end of the hydrological year to set the reference surface  each year (set the zero)" "[ 2020-09-01, 2021-09-01, 2022-09-01 ]"
```
### List of nodes
```YAML
node:
  - id: "string" "unique id of the node" "sw-110"
    name: "string" "colloquial name of the node, often associated to known location" "MLB3"
    operational: "boolean" "True if station is still operational otherwise False" "True"
    date_installation: "date" "Date of the original installation of the node" "2021-04-18 15:32:09"
    meteoio_ini_template: "string" "Filename of the template containing meteoIO's preset input/filter parameters" "template_meteoio_wsn.ini"
    location: 
      epsg: "integer" "Coordinate reference system in epsg code" "32633"
      easting: "integer/float" "x coordinate in UTM (rounded to metre) or longitude (in decimal degrees)" "436655"
      northing: "integer/float" "y coordinate in UTM (rounded to metre) or latitude (in decimal degrees)" "8759315"
      elevation: "integer/float" "z coordinate (rounded to metre)" "143"
      date: "date" "Date of the measurement of the node location (in case, the node is moving, i.e. on a glacier)" "2021-04-26"
    snow:
      date: "date array" "Date of snow measurements" "[ 2021-04-26 ]"
      dist_to_sensor: "integer array" "Distance from the node's sensor to the snow surface in millimetre" "[ 1240 ]"
      depth: "integer array" "Distance from the snow surface to the ground/ice surface in millimetre" "[ 240 ]"
    version:
#---------- 2021 ----------
      - date_start: "date" "Start date of this node's version" "2021-04-26 14:52:17"
        date_end: "date" "End date of this node's version" "2022-05-01 00:00:00"
        version: "integer" "Hardware version of the node" "2"
        commit: "string" "Software version of the code uploaded to the node" "e3313958b542ed0e2dda5b943a53e0d197722355"
        QC_done: "boolean" "Set to False if quality controlled has not be completed" "False"
        data_sios: "string array" "Array of sensor's data name to be quality controlled and published" "[tmp_temperature, sht_hum, bme_pres, mb_distance, wind_dir, wind_speed, mlx_object]"
        sensor: "string array" "Array of sensors installed on the node" "[bme_int, mb, atmos, qtpy]"
        config:
          address: "integer" "Address of the node" "110"
          run_system: "string array" "Code to run the node's system" "bat=10 gps=12:00 acc=10 lan=30"
          run_sensor: "string array" "Code to run the node's sensors" "bme_int=10 mb=10 atmos=10 qtpy=10"
          destination: "integer" "Destination's address" "2"
          lora_mode: "integer" "Mode of LoRa communcation" "6"
        data: "string array" "Array of all data saved by the node -  extracted from the database" "[time, bat, frame, received, type, acc_x, ...]"
        note: "string" "Description of the node's maintenance or observations" "Stake has been redrilled and station reinstalled ..."
#---------------------------------------------------------
```

```
network:
  name:
  owner:
  country:  
  description:
  date_installation:
  date_update:
  year_hydro:
  
node:
#---------------------------------------------------------
  - id: sw-template
    name: 
    operational: 
    date_installation: 
    meteoio_ini_template: 
    location:
      epsg:
      easting: 
      northing: 
      elevation: 
      date: 
    snow:
      date: [  ]
      dist_to_sensor: [  ] 
      depth: [  ]
    version:
#---------- 2021 ----------
      - date_start: 
        date_end: 
        version: 
        commit:
        QC_done: 
        data_sios: 
        sensor: 
        config:
          adress: 
          run_system: 
          run_sensor: 
          destination: 
          lora_mode: 
        data: 
        note:
#---------------------------------------------------------

ACDD:
  WRITE:
  CREATOR:
  CREATOR_EMAIL:
  CREATOR_INSTITUTION:
  CREATOR_URL:
  CREATOR_TYPE:
  PUBLISHER:
  PUBLISHER_EMAIL:
  PUBLISHER_URL:
  PUBLISHER_TYPE:
  INSTITUTION:
  KEYWORDS:
  KEYWORDS_VOCABULARY:
  TITLE: 
  PROJECT:
  SOURCE:
  ID:
  NAMING_AUTHORITY:
  PROCESSING_LEVEL:
  SUMMARY:
  ACKNOWLEDGEMENT:
  REFERENCES:
  LICENSE:
  PRODUCT_VERSION:
  ACTIVITY_TYPE:
  OPERATIONAL_STATUS:
```