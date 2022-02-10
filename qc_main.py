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
from configobj import ConfigObj


#==========  DEFINE FUNCTION  =========

dict_corres = {
    'tmp_temperature':['TA',1,273.15], # Air temperature [K]
    'bme_tc':['TA',1,273.15],          # Air temperature [K]
    'bme_hum':['RH',0.01,0],            # Relative humidity [%]
    'mb_distance':['HS',0.01,0],       # Height of snow [cm]
    'vl_distance':['HS',0.01,0],       # Height of snow [cm]
    'bme_pres':['P',1,0],              # Air pressure [Pa]
    'wind_speed':['VW',1,0],           # Wind velocity [m.s-1]
    'wind_dir':['DW',1,0],             # Wind direction [degree from North]
    'mlx_object':['TSS',1,273.15],     # Temperature of the snow surface [K]
    '':['TSG',1,273.15],               # Temperature of the ground surface [K]
    '':['VW_MAX',1,0]
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
    

    for node in conf['node']:
        print('======================================')
        print('---> Preparing QC node {} - {}'.format(node['id'],node['name']))

        for version in node['version']:
            date_start=pd.to_datetime(version['date_start'])
            date_end=pd.to_datetime(version['date_end'])
            print('---> Version {} to {}'.format(format(date_start,"%Y-%m-%d"), format(date_end,"%Y-%m-%d")))
            
            if not version['QC_done']:
                try:
                    # Query database
                    df = query.query('postgresql', 
                    name=node['id'], 
                    fields=version['data_sios'],
                    time__gte=date_start, 
                    time__lte=date_end, 
                    limit=2000000000000)
                    print('---> Downloading {}',format(version['data_sios']))
                    
                    # handle MB. 1) median, 2) convert to SD
                    df['mb_median'] = df.mb_distance.apply(lambda x: np.median(np.array(x)))


                    # save to CSV
                    fname_csv = '{}_{}_{}.csv'.format(node['id'],
                                                      format(date_start,"%Y%m%d"),
                                                      format(date_end,"%Y%m%d"))
                    print('---> Filename: {}'.format(fname_csv))
                    
                except IOerror:
                    
                # save custom ini
                # [Input]
                config_ini['Input'][METEOPATH]='.'
                config_ini['Input']['CSV_UNITS_OFFSET']='0 {}'.format(' '.join([ str(dict_corres[d][2]) for d in version['data_sios'] ]))
                config_ini['Input']['CSV_UNITS_MULTIPLIER']='1 {}'.format(' '.join([str(dict_corres[d][1]) for d in version['data_sios'] ]))
                config_ini['Input']['CSV_FIELDS']='TIMESTAMP {}'.format(' '.join([dict_corres[d][0]  for d in version['data_sios'] ]))
                config_ini['Input']['CSV_NAME']=node['id']
                config_ini['Input']['CSV_ID']=node['id']
                config_ini['Input']['POSITION']='xy({},{},{})'.format(node['location']['easting'],node['location']['northing'],node['location']['elevation'])
                config_ini['Input']['STATION1']='{}.csv'.format(node['id'])
                # [Output]
            
                    
