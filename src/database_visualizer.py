import argparse
from itertools import product
import pickle
from pathlib import Path
from typing import Text
from typing import List
from typing import Dict
from typing import Any
from typing import NewType
import numpy as np
from matplotlib import pyplot as plt

# result_dictとは、次のような形式の辞書型のこと
# {width_x_radious_y_depth_z : {100 : 584, 125 : 540, 150 : 560, ..., 200 : 570}}
def create_result_dict(db_dict):
    db_dict_keys = list(db_dict.keys())
    depth_list = {str(key).split('_')[-1] for key in db_dict_keys}
    depth_list = sorted(depth_list)

    for depth in depth_list:
        result_dict = {} 
        for key, value in db_dict.items():
            depth = key.split('_')[-1]
            result_dict_key = key.split('_target_pressure')[0] + f'_depth_{depth}'
            if result_dict_key not in result_dict.keys():
                result_dict[result_dict_key] = []
            target_pressure = key.split('_')[6]
            if target_pressure == '0':
                continue
            bend_sensor_mean = value[0]['bend_sensor_mean']
            result_dict[result_dict_key].append([int(target_pressure), float(bend_sensor_mean)])

    return result_dict

def create_display_dict_list(result_dict, fixed_param='width', ylim=None) -> List:
    result_dict_keys = result_dict.keys()
    fixed_param_index = list(result_dict_keys)[0].split('_').index(fixed_param)
    f_param_list = {str(key).split('_')[fixed_param_index + 1] for key in result_dict_keys}
    f_param_list = sorted(f_param_list)
    depth_list = {str(key).split('_')[-1] for key in result_dict_keys}
    depth_list = sorted(depth_list)
    
    display_dict_list = []
    for depth, param_value in product(depth_list, f_param_list):
        display_dict = {}

        display_dict['ylim'] = ylim
        display_dict['title'] = f'depth_{depth}_{fixed_param}_{param_value}'
        display_dict['elements'] = []

        for key, plot_data in result_dict.items():
            display_dict_element = {}
            if f'depth_{depth}' not in key:
                continue
            if f'{fixed_param}_{param_value}' not in key:
                continue
            plot_data = sorted(plot_data) # 0番目、目標圧力値でソート
            plot_data = np.array(plot_data)
            display_dict_element['x'] = plot_data[:, 0]
            display_dict_element['y'] = plot_data[:, 1]
            display_dict_element['label'] = key
            display_dict['elements'].append(display_dict_element)
        
        display_dict_list.append(display_dict)

    return display_dict_list

def plot_display_dict_list(display_dict_list, show_flug=True, savefig_flug=True, save_dir=None):
    for display_dict in display_dict_list:
        plt.figure()
        plt.title(display_dict['title'])
        if display_dict['ylim'] is not None:
            plt.ylim(display_dict['ylim'])

        for el in display_dict['elements']:
            plt.plot(
                el['x'],
                el['y'],
                label=el['label'],
            )
        plt.legend()
        
        if show_flug:
            plt.show()
        
        if savefig_flug:
            if save_dir is None:
                raise ValueError('Please set the save_dir when savefig_flug is True')
            plt.savefig(save_dir + f'/{display_dict["title"]}')

        plt.close()

        

def get_latest_db_path(db_dir_path : Text) -> Text:
    d_path = Path(db_dir_path)
    f_path_list = d_path.glob('**/db_dict.pickle')
    f_path_list = sorted(f_path_list)
    latest_db_path = f_path_list[-1]
    return latest_db_path

def main():
    parser = argparse.ArgumentParser(description='database_visualizer')
    parser.add_argument('-p', '--db_dir_path', type=str, default='/home/toshi/python_projects/indention_test_analisys/database')
    parser.add_argument('-r', '--result_dir_path', type=str, default='/home/toshi/python_projects/analysis_result')
    args = parser.parse_args()

    latest_db_path = get_latest_db_path(args.db_dir_path)
    with open(latest_db_path, 'rb') as f:
        db_dict = pickle.load(f)

    result_dict = create_result_dict(db_dict)

    display_dict_fixed_width   = create_display_dict_list(result_dict, fixed_param='width'  , ylim=[520, 630])
    display_dict_fixed_radious = create_display_dict_list(result_dict, fixed_param='radious', ylim=[520, 630])

    plot_display_dict_list(display_dict_fixed_width,   show_flug=False, savefig_flug=True, save_dir=args.result_dir_path)
    plot_display_dict_list(display_dict_fixed_radious, show_flug=False, savefig_flug=True, save_dir=args.result_dir_path)


if __name__=='__main__':
    main()
