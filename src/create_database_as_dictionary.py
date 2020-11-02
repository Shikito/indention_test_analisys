###################################################
# 生データを意味のあるデータにまとめます          #
# 具体的には、曲げセンサや空気圧センサの          # 
# 平均・分散を計算します。そして                  #
# dictionary型のデータベースとして                # 
# pickle形式で保存します。                        # 
# ############################################### #
   
import os
import sys
import argparse
import pathlib
import pickle
from itertools import product
from datetime import datetime as dt
from typing import Text
from typing import List
from typing import Dict

import yaml
import pandas as pd
from matplotlib import pyplot as plt

def csv_file_paths(dir_path : Text) -> List[Text]:
    d_path = pathlib.Path(dir_path)
    csv_paths_posix = list(d_path.glob('**/*.csv'))
    csv_paths_str = map(str, csv_paths_posix) 
    return csv_paths_str

def parse_csv_file_path(csv_file_path : Text) -> Dict[Text, int]:
    file_name = csv_file_path.split('/')[-1]
    width = file_name.split('_')[1]
    radious = file_name.split('_')[3]
    return {
        'width':width,
        'radious':radious,
    }

def main(argv=sys.argv):

    # initial settings
    home_path = os.environ['HOME']
    dt_now = dt.now().strftime('%Y%m%d%H%M%S')
    
    parser = argparse.ArgumentParser(description='indention_test_plotter')
    parser.add_argument('-r', '--rawdata_dir_path', type=str, default=home_path+'/python_projects/indention_test_analisys/rawdata') 
    parser.add_argument('-s', '--save_dir_path', type=str, default=home_path+f'/python_projects/indention_test_analisys/database/{dt_now}') 
    args = parser.parse_args()
    
    csv_paths = csv_file_paths(args.rawdata_dir_path)

    # process rawdata and create db_dict(which is Dictionary)
    db_dict = {}
    for path in csv_paths:

        # get csv file info from it's path name
        csv_file_info = parse_csv_file_path(str(path))
        width   = csv_file_info['width']
        radious = csv_file_info['radious']
        
        df = pd.read_csv(path)
        
        home_indention_pos   = df['ttac3_state_z'].unique()[0]
        indention_depth_list = df['ttac3_state_z'].unique()[1:]  # unique()[0] is home_position that is meaningless
        target_pressure_list = df['target_pressure_value'].unique()
        
        for tp, depth in product(target_pressure_list, indention_depth_list):
            db_key = f'width_{width}_radious_{radious}_target_pressure_{int(tp)}_indention_depth_{depth - home_indention_pos}'
            
            if db_key not in db_dict.keys():
                db_dict[db_key] = []

            indecies = (df['target_pressure_value'] == tp) & (df['ttac3_state_z'] == depth)
            processed_data = {
                'bend_sensor_mean' :float(df['bend_sensor_value'][indecies].mean()),
                'bend_sensor_std'  :float(df['bend_sensor_value'][indecies].std()),
                'air_pressure_mean':float(df['current_pressure_value'][indecies].mean()),
                'air_pressure_std' :float(df['current_pressure_value'][indecies].std()),
            }
            db_dict[db_key].append(processed_data)

    # create meta_data of db_list
    meta_data = {'width_radious_target_depth : data_num ' : {key : len(value) for key, value in db_dict.items()} }

    # display db_dict
    for key, data_list in db_dict.items():
        for data in data_list:
            print(key, data)

    # save db_dict
    pathlib.Path(args.save_dir_path).mkdir(exist_ok=True, parents=True)
    with open(args.save_dir_path + f'/db_dict.pickle', 'wb') as f:
        pickle.dump(db_dict, f)

    # save metadata of db_dict
    with open(args.save_dir_path + f'/db_metadata.yaml', 'w') as f:
        yaml.dump(meta_data, f, default_flow_style=False)

if __name__=='__main__':
    main()