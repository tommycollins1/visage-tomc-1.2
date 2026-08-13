"""
-------------------------------------------------------------------------------
Title: ""
Description: ""
Created: 12/01/2024
Author: tommycollins1 (trc207)
-------------------------------------------------------------------------------
"""
import logging
import pandas as pd


# --------------------------------------------------------------- data params -
def set_pandas_options():
    print('... pandas options')
    pd.set_option('display.max_columns', 500)


# ------------------------------------------------------------ logging params -
def set_logging_params():
    print('... logging config')
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%d-%b-%y %H:%M:%S')


# ---------------------------------------------------------------- vis params -
# def set_cell_type_params():
#     if cfg.objects.spatial_aggregation_first:
#         print('Using IRIS parameters.')
#         return cfg.iris_path
#     else:
#         print('Using NETMOB parameters.')
#         return cfg.netmob_path

print('Setting parameters...')

set_pandas_options()
set_logging_params()
