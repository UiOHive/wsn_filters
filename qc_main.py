'''
S. Filhol and P. Lefeuvre, Feb 2022

Script to control QC routine 


Scipt input (parse with argparse):
   - network.yml
   - WSN_meteoio_template.ini
   - path

Logic:
    1. parse network.yml file
    2. query PostgreSQL DB based on .yml
        - one query by version of each node. 
        - save one csv file per version per nodes
        - Convert unit if needed
    3. parse WSN_meteoio_template.ini
    4. modify .ini file. One per version per nodes


'''


import xarray as xr
import pandas as pd
import os, sys, datetime
from wsn_client import query
import yaml
import argparse
import configobj

#==========  DEFINE FUNCTION  =========

dict_corres = {
    'TA':['tmp_temperature','bme_tc'],      # Air temperature
    'RH':'bme_hum',                         # Relative humidity
    'HS':['mb_distance','vl_distance'],     # Height of snow
    'P':'bme_pres',                         # Air pressure
    'VW':'wind_speed',                      # Wind velocity
    'DW':'wind_dir',                        # Wind direction
    'TSS': 'mlx_object',    # Temperature of the snow surface
    'TSG': '',              # Temperature of the ground surface
    'VW_MAX':''
}

#========== Script ============

if __name__ == "__main__":
    
    # Parse script input
    parser = argparse.ArgumentParser()
    parser.add_argument('--network_config', '-nc', help='Path to config file of the network', default='/home/config.yml')
    parser.add_argument('--meteoio_template', '-ini', help='Path to Meteoio .ini file template', default='/home/meteoio.ini')
    args = parser.parse_args()
    
    # csv filename convention:  node_startdate_enddate.csv    ex: sw-001_20210419_20220412.csv
    # meteoio ini file per version per node                   ex: sw-001_20210419_20220412.ini
    

    # Open network 
    with open(args.net, 'r') as file:
        conf = yaml.safe_load(file)
    
    # Open Meteoio ini template
    

    for node in conf['network_nodes']:
        print('======================================')
        print('---> Preparing for QC node {}'.format(node['common_name']))
        
        for version in node['version']:
            print('---> Version {} to {}'.format(version['start_date'], version['end_date']))
            
            if not version['QC_done']:
                try:
                    # Query database
                    start_date = version['start_date']
                    end_date = version['end_date']
                    
                    df = query.query('postgresql', 
                                     name=node['node_name'], 
                                     fields=version['sensors_sios'],
                                     time__gte=start_date, 
                                     time__lte=end_date, 
                                     limit=2000000000000)
                    
                    # handle MB. 1) median, 2) convert to SD
                    df['mb_median'] = df.mb_distance.apply(lambda x: np.median(np.array(x)))


                    # save to CSV
                    fname_csv = '{}_{}_{}'.format(node['node_name'],
                                                 version['start_date'],
                                                 version['end_date'])
                    df.to_csv(fname_csv)
                    
                except IOerror:
                    
                # save custom ini
                
                    
