# Workflow for Metadata and Quality Control
wsn_filters is a process workflow for automatic weather station data that focuses on gathering metadata in config files and [meteoIO](https://gitlabext.wsl.ch/snow-models/meteoio) from SLF for producing a fast quality-control metadata-rich netcdf file. This project is part of [UiO Hive](https://uiohive.github.io/Hive/) that develops IoT technologies, AI/ML to solve data challenges, and shares knowledge across relevant interdisciplinary domains.

## Structure
- ```qc_*.py```: workflow specific to each network such as ```qc_main.py``` for the wsn network in Svalbard.
- ```config_*.yml```: YAML config file specific to each network such as ```config_wsn_KNG.yml``` for the Kongsvegen network
- ini/: folder with templates and processed INI files containing parameters required by meteoIO. First, the parameter fields in an INI template are defined manually for each network. Running the ```qc_main.py``` pipeline, node-dependent parameters are added from the YAML config file to the template. The then new INI file is saved with the node name for backup and copied to the ```io.ini``` file required by the meteoIO processing command ```data_converter```.
- data/: folder storing original data in csv file
- data_qc/: folder for the quality-controlled metadata-rich netcdf output file
- log/: log folder
- ```wsn_main.ipynb```: a jupyter notebooks containing earlier versions of the code and plots
- ```MeteoIO_test.ipynb```: a jupyter notebooks containing earlier versions of the meteoIO pipeline
- ```notebook_test_filter.ipynb```: a jupyter notebooks containing earlier versions of quality control codes

## Application 
The pipeline is designed for weather data from two networks of automatic weather stations installed in Svalbard as described in the [Hive documentation](https://hive-wireless-sensor-network.readthedocs.io/en/latest/). The code is developed to be transferrable to other locations and networks such as the one in Finse, Norway, also maintained by the University of Oslo.

## Command line usage
### Wireless Sensor Network at Kongsvegen and Midtre Lovenbreen
The pipeline requires the config file as input parameter and can be ran as follow: 
```
python qc_main.py -nc config_wsn_KNG.yml
```
### AWS at Austfonna
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
- [UiOHive github](https://github.com/UiOHive)
- [Hive documentation](https://hive-wireless-sensor-network.readthedocs.io/en/latest/)

You can find a complete description of MeteoIO in:
- [meteoIO's wiki](https://gitlabext.wsl.ch/snow-models/meteoio/-/wikis)
- Bavay, M. and Egger, T., "MeteoIO 2.4.2: a preprocessing library for meteorological data", Geosci. Model Dev., 7, 3135-3151, doi:10.5194/gmd-7-3135-2014, 2014 
and some example applications in: 
- Bavay, M., Fiddes, J., Fierz, C., Lehning, M., Monti, F. and Egger, T., "The METEOIO pre-processing library for operational applications", In International Snow Science Workshop ISSW, Innsbruck, Austria, 2018.
