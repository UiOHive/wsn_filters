# Workflow for Metadata and Quality Control
wsn_filters is a process workflow for automatic weather station data that focuses on gathering metadata in config files and meteoIO from SLF for producing a fast quality-control metadata-rich netcdf file.

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


## Command Line
### Wireless Sensor Network at Kongsvegen and Midtre Lovenbreen
The pipeline requires the config file as input parameter and can be ran as follow: 
```
python qc_main.py -nc config_wsn_KNG.yml
```
### AWS at Austfonna
```
python qc_austfonna.py -nc config_austfonna_ETON2.yml
```

## References
- insert paper references here
