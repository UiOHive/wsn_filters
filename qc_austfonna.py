#!/bin/python
'''
 P. Lefeuvre and S. Filhol, Feb 2022

Script to control QC routine 


Scipt input (parse with argparse):
   - austfonna_ETON2.yml
   - meteoio_austfonna.ini
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
#import xarray as xr
import numpy as np
import pandas as pd
import os, sys, datetime, shutil
import subprocess
from wsn_client import query
import yaml
import argparse
from configobj import ConfigObj
import logging
import time

#==========  DEFINE FUNCTION  =========

# Dictionary for variables to meteoIO input format    
dict_corres = {
    'TA':['TA', 1, 273.15], # Air temperature [deg. K]
    'RH':['RH',0.01,0],            # Relative humidity [% -> 1-0]
    'HS':['HS',1,0],       # Height of snow [cm -> m]
    'P':['P',100, 0],              # Air pressure [Pa]
    'VW':['VW',1,0],           # Wind velocity [m.s-1]
    'DW':['DW',1,0],             # Wind direction [degree from North]
    'TSS':['TSS',1,0],     # Temperature of the snow surface [deg. C -> K]
    'ISWR':['ISWR',1,0],               # Incoming SW [W/m2]
    'RSWR':['RSWR',1,0],               # Reflected SW []
    'ILWR':['ILWR',1,0],               # Incoming LW []
    
}

#========== Script ============
if __name__ == "__main__":
    
    # Log info/debug/error
    logfile = 'log/qc_austfonna_{}.log'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
                        # datefmt='%m-%d %H:%M',
                        filename=logfile,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(console)
    
    logging.info('Parse arguments')
    # Parse script input
    parser = argparse.ArgumentParser()
    parser.add_argument('--network_config', '-nc', help='Path to config file of the network', default='network.yml')
    parser.add_argument('--meteoio_template', '-ini', help='Path to Meteoio .ini file template', default='/home/meteoio.ini')
    args = parser.parse_args()
    
    # csv filename convention:  node_startdate_enddate.csv    ex: sw-001_20210419_20220412.csv
    # meteoio ini file per version per node                   ex: sw-001_20210419_20220412.ini
    
    print(args)
    # Open network 
    with open(args.network_config, 'r') as file:
        conf = yaml.safe_load(file)    

    for node in conf['node']:
        logging.info('======================================')
        logging.info('---> Preparing QC node {} - {}'.format(node['id'],node['name']))

        # Open the meteoIO configuration template (ini file)  
        config_ini = ConfigObj('ini/'+node['meteoio_ini_template'])
        
        # Loop through several version i.e. sensor types
        for version in node['version']:
            date_start = version['date_start']
            date_end = version['date_end']
            logging.info('---> Version {} to {}'.format(format(date_start,"%Y-%m-%d"), format(date_end,"%Y-%m-%d")))
            
            if not version['QC_done']:
                try:
                    # Filename of the data without extension
                    fname = 'aws-eton-2'
                    fname_out ='{}-{}-{}.nc'.format(fname, format(date_start,"%Y%m%d"), format(date_end,"%Y%m%d"))
                    
                    ## Save custom ini
                    # filename ini
                    fname_ini = 'ini/{}.ini'.format(fname)
                    logging.info('---> Copy and fill meteoIO configurations: {}'.format(fname_ini))

                    # Copy and load configuration file template for meteoIO
                    shutil.copyfile('ini/'+node['meteoio_ini_template'],fname_ini)
                    config_ini = ConfigObj(fname_ini)

                    # [Input]
                    config_ini['Input']['STATION1']='{}.csv'.format(fname) 
                    config_ini['Input']['CSV_UNITS_OFFSET']='0 {}'.format(' '.join([ str(dict_corres[d][2]) for d in version['data_sios'] ]))
                    config_ini['Input']['CSV_UNITS_MULTIPLIER']='1 {}'.format(' '.join([str(dict_corres[d][1]) for d in version['data_sios'] ]))
                    config_ini['Input']['CSV_FIELDS']='TIMESTAMP {}'.format(' '.join([dict_corres[d][0]  for d in version['data_sios'] ]))
                    config_ini['Input']['CSV_NAME']=node['id']
                    config_ini['Input']['CSV_ID']=node['id']
                    config_ini['Input']['POSITION']='xy({},{},{})'.format(node['location']['easting'],
                                                                          node['location']['northing'],
                                                                          node['location']['elevation'])
                    # [Output]
                    config_ini['Output']['METEOFILE']=fname_out
                    config_ini['Output']['NC_CREATOR']=conf['ACDD']['CREATOR']
                    config_ini['Output']['NC_SUMMARY']='Station {} from {}'.format(node['id'],conf['network']['description'])
                    config_ini['Output']['NC_ID']=node['id']
                    config_ini['Output']['ACDD_CREATOR']=conf['ACDD']['CREATOR']
                    
                    # Add ACDD values
                    for ACDD,value in conf['ACDD'].items():
                        if not ACDD=='WRITE':
                            config_ini['Output']['ACDD_'+ACDD]=value

                    # write and copy ini - and remove double quotes
                    config_ini.write()
                    subprocess.run(['sed -i \'\' \'s/"//g\' {}'.format(fname_ini)], shell=True)
                    shutil.copyfile(fname_ini,'io.ini')
                    logging.info('---> Save meteoIO configurations and make io.ini file')

                    # run MeteoIO (need to alias data_converter)
                    sampling_rate = 10 # in minutes
                    command = 'data_converter {} {} {}'.format(format(date_start,"%Y-%m-%dT%H:%M:%S"),format(date_end,"%Y-%m-%dT%H:%M:%S"),sampling_rate)
                    logging.info('---> command: {}'.format(command))
                    time.sleep(4)
                    subprocess.run([command], shell=True)
                    logging.info('---> Netcdf output: {}'.format(fname_out))
                    
                except IOerror:
                    logging.info(e)
                    logging.info(sys.exc_type)