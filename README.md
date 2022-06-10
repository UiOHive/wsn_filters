# Workflow for Metadata and Quality Control
wsn_filters is a process workflow for automatic weather station data that is used for quality control and deliver a metadata-rich netcdf using meteoIO.

## Structure
- qc_*.py: workflow specific to each network such as qc_main.py for the wsn network in Svalbard.
- config_*.yml: YAML config file specific to each network such as config_wsn_KNG.yml
- ini/: templates and processed INI files containing meteoIO's parameters. The parameter fields are first populated manually in a template for each network. Running the ```qc_main.py``` pipeline, node-dependent parameters are added from the YAML config file inside the template and copied to a new file saved with the node name.
- data/: folder storing original data in csv file
- data_qc/: folder for the quality-controlled metadata-rich netcdf output file
- log/: folder for saving logs

## Command Line
### Wireless Sensor Network at Kongsvegen and Midtre Lovenbreen
```
python qc_main.py -nc config_wsn_KNG.yml
```
### AWS at Austfonna
```
python qc_austfonna.py -nc config_austfonna_ETON2.yml
```

## References
- insert paper references here
