#!/bin/python
'''
 P. Lefeuvre and S. Filhol, Feb 2022

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


#import xarray as xr
import numpy as np
import pandas as pd
import os, sys, datetime, shutil
from sys import platform
import subprocess
from wsn_client import query
import yaml
import argparse
from configobj import ConfigObj
import logging
import time
from datetime import timedelta


#==========  DEFINE FUNCTION  =========

def calibration_snow(df,node_snow,year_hydro):
    ##########################
    # Snow depth calibration #
    ##########################
    
    # Time span
    date_start = df.index.min().date()
    date_end = df.index.max().date()
    logging.info('     Data range: {} - {}'.format(date_start,date_end))

    # Compute median value and assign to new column for output
    df = df.apply(lambda x: np.median(np.array(x)))

    # Extract hydrological station 
    year_hydro = []
    for node_last_melt in node['date_last_melt']:
        year_hydro.append(node_last_melt['date'])
        
    # loop through hydrological year to calibrate snow depth
    for d in range(1,len(year_hydro)):

        # Constrain loop to calibrate only period with data
        str_hydro_year = '     Period {} - {}:'.format(year_hydro[d-1],year_hydro[d])
        if any(( year_hydro[d] < date_start, year_hydro[d-1] > date_end )):
            logging.info('{} No data for hydrological year'.format(str_hydro_year))
            continue

        # Find calibration parameters matching the hydrological year
        date_snow = []
        dist_surf_sensor= []
        snow_depth = []
        offset = []
        for node_snow in node['snow']: 
            if node_snow['usage'] == 'calibration':
                date = node_snow['date']
                if date >= year_hydro[d-1] and date < year_hydro[d]:
                    date_snow = date
                    dist_surf_sensor = node_snow['dist_surf_sensor']
                    snow_depth = node_snow['snow_depth']
                    offset = node_snow['offset']
                    if node_snow['dist_surf_sensor'] is None or node_snow['snow_depth'] is None:
                        logging.info("{} No calibration data for hydrological year".format(str_hydro_year))
                        continue

        # Compute distance between sensor and reference surface i.e. ice or last summer surface
        height_sensor_to_ice = dist_surf_sensor + offset + snow_depth
        logging.info('{} Apply snow calibration ... {} + {} + {} = {} mm on {}'.format(str_hydro_year, dist_surf_sensor, snow_depth, offset, height_sensor_to_ice, date_snow))

        # Calibration of snow depth - Remove negative value i.e. ice melt
        snow_depth = height_sensor_to_ice - df[year_hydro[d-1]:year_hydro[d]]
        snow_depth[snow_depth<0] = 0

        # Assign in dataframe
        df[year_hydro[d-1]:year_hydro[d]] = snow_depth
        #df.plot()
                                              
    return df
    ##########################

# Dictionary for variables to meteoIO input format    
dict_corres = {
    'tmp_temperature':['TA',1,273.15], # Air temperature [deg. C -> K]
    'wind_temp':['TA',1,273.15],       # Air temperature [deg. C -> K]
    'ds2_temp':['TA',1,273.15],        # Air temperature [deg. C -> K]
    'bme_tc':['TA',1,273.15],          # Air temperature [deg. C -> K]
    'bme_hum':['RH',0.01,0],           # Relative humidity [% -> 1-0]
    'sht_hum':['RH',0.01,0],           # Relative humidity [% -> 1-0]
    'mb_distance':['HS',0.001,0],          # Height of snow [mm -> m]
    'vl_distance':['HS',0.001,0],          # Height of snow [mm -> m]
    'bme_pres':['P',100,0],            # Air pressure [hPa -> Pa]
    'wind_speed':['VW',1,0],           # Wind velocity [m.s-1]
    'wind_dir':['DW',1,0],             # Wind direction [degree from North]
    'ds2_speed':['VW',1,0],            # Wind velocity [m.s-1]
    'ds2_dir':['DW',1,0],              # Wind direction [degree from North]
    'mlx_object':['TSS',1,273.15],     # Temperature of the snow surface [deg. C -> K]
    '':['TSG',1,273.15],               # Temperature of the ground surface [deg. C -> K]
    '':['VW_MAX',1,0]
}

#========== Script ============
if __name__ == "__main__":
        
    # Log info/debug/error
    logfile = 'log/qc_main_{}.log'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
                        # datefmt='%m-%d %H:%M',
                        filename=logfile,
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(console)
    
    # Parse script input
    logging.info('Parse arguments')
    parser = argparse.ArgumentParser()
    parser.add_argument('--network_config', '-nc', help='Path to config file of the network', default='network.yml')
    parser.add_argument('--meteoio_template', '-ini', help='Path to Meteoio .ini file template', default='/home/meteoio.ini')
    args = parser.parse_args()
    logging.info(args)
    
    # Open network 
    with open(args.network_config, 'r') as file:
        conf = yaml.safe_load(file)
    
    # Create directory tree
    folder_input = conf['path']['folder_input']
    folder_output = conf['path']['folder_output']
    if not os.path.exists('log'): os.makedirs('log')
    if not os.path.exists('ini'): os.makedirs('log')
    if not os.path.exists(folder_input): os.makedirs(folder_input)
    if not os.path.exists(folder_output): os.makedirs(folder_output)

    for node in conf['node']:
        logging.info('=============================================')
        logging.info('=============================================')
        logging.info('---> Preparing QC node {} - {}'.format(node['id'],node['name']))

        # Open the meteoIO configuration template (ini file)  
        config_ini = ConfigObj('ini/'+node['meteoio_ini_template'])
        
        # Loop through several version i.e. sensor types
        for version in node['version']:
            date_start = version['date_start'].replace(microsecond=0, second=0, minute=0)
            date_end = version['date_end'].replace(microsecond=0, second=0, minute=0)+ timedelta(hours=1)
            logging.info('---> Version {} to {}: {}'.format(format(date_start,"%Y-%m-%d"),
                                                            format(date_end,"%Y-%m-%d"),
                                                            version['QC_todo']))
            
            # Check if data_sios is empty
            if type(version['data_sios']) is float:
                if pd.isnull(version['data_sios']):
                    logging.info('---> No data_sios')
                    logging.info('===')
                    continue
            
            if not version['QC_todo']:
                logging.info('---> Do not run QC')
                logging.info('===')
                continue
            else:
                try:
                    # Query database
                    df = query.query('postgresql',
                                     name=node['id'],
                                     fields=version['data_sios'],
                                     time__gte=date_start,
                                     time__lte=date_end,
                                     limit=2000000000000)
                    logging.info('---> Downloading {}'.format(version['data_sios']))

                    ## Formatting
                    # Replace Nones in empty lists by NaNs 
                    df = df.fillna(value=np.nan)
                    # Assign NaNs to -9999 values
                    df = df.replace('-9999',np.nan)
                    # Remove column with time as number
                    del df['time']

                    ## Snow depth calibration
                    if "mb_distance" in version['data_sios']:
                        logging.info('---> Snow depth calibration')
                        df['mb_distance'] = calibration_snow(df['mb_distance'],node['snow'],node['date_last_melt'])
                    else:
                        logging.info('---> No snow depth data: skip calibration')
                    
                    ## Handling filenames
                    fname = 'aws-{}-{}-{}'.format(node['id'],
                                              format(date_start,"%Y%m%d"),
                                              format(date_end,"%Y%m%d"))
                    fname_csv = '{}/{}.csv'.format(folder_input, fname)
                    fname_out ='{}.nc'.format(fname)
                    
                    ## Delete existing files
                    path_out = '{}/{}'.format(folder_output, fname_out)
                    if os.path.exists(path_out):
                        os.remove(path_out)
                        logging.info('---> Deleted existing file: {}'.format(path_out))
                    
                    ## Save to CSV
                    logging.info('---> Save data output in: {}'.format(fname_csv))
                    df.to_csv(fname_csv)

                    ## Save custom ini
                    # filename ini
                    fname_ini = 'ini/{}.ini'.format(fname)
                    if os.path.exists(fname_ini):
                        os.remove(fname_ini)
                        logging.info('---> Deleted existing file: {}'.format(fname_ini))
                    logging.info('---> Copy and fill meteoIO configurations: {}'.format(fname_ini))

                    # Copy and load configuration file template for meteoIO
                    shutil.copyfile('ini/'+node['meteoio_ini_template'],fname_ini)
                    config_ini = ConfigObj(fname_ini)

                    # [Input]
                    config_ini['Input']['METEOPATH']=folder_input
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
                    config_ini['Output']['METEOPATH']=folder_output
                    config_ini['Output']['METEOFILE']='{}.nc'.format(fname)
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
                    if platform == "linux" or platform == "linux2":
                        subprocess.run(['sed -i \'s/"//g\' {}'.format(fname_ini)], shell=True)
                    elif platform == "darwin":
                        subprocess.run(['sed -i \'\' \'s/"//g\' {}'.format(fname_ini)], shell=True)
                    shutil.copyfile(fname_ini,'io.ini')
                    logging.info('---> Save meteoIO configurations and make io.ini file')

                    # run MeteoIO (need to alias data_converter)
                    sampling_rate = 10 # in minutes
                    command = 'data_converter {} {} {}'.format(format(date_start,"%Y-%m-%dT%H:%M:%S"),format(date_end,"%Y-%m-%dT%H:%M:%S"),sampling_rate)
                    logging.info('---> command: {}'.format(command))
                    time.sleep(4)
                    subprocess.run([command], shell=True)
                    logging.info('---> Netcdf output: {}'.format(path_out))
                    logging.info('===')
                    
                except IOerror:
                    logging.info(e)
                    logging.info(sys.exc_type)
