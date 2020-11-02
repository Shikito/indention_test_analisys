import argparse
from itertools import product
import pickle
from pathlib import Path
from typing import Text
import numpy as np
from matplotlib import pyplot as plt

# TODO:描画したいものは以下
# 横軸が空気圧
# 縦軸が曲げセンサの値
# indention_depthごとにグラフを書く。

def get_latest_db_path(db_dir_path : Text) -> Text:
    d_path = Path(db_dir_path)
    f_path_list = d_path.glob('**/db_dict.pickle')
    f_path_list = sorted(f_path_list)
    latest_db_path = f_path_list[-1]
    return latest_db_path

def main():
    parser = argparse.ArgumentParser(description='database_visualizer')
    parser.add_argument('-p', '--db_dir_path', type=str,
                        default='/home/toshi/python_projects/indention_test_analisys/database')
    parser.add_argument('-r', '--result_dir_path', type=str,
                        default='/home/toshi/python_projects/analysis_result')
    args = parser.parse_args()

    latest_db_path = get_latest_db_path(args.db_dir_path)
    # print(latest_db_path)
    with open(latest_db_path, 'rb') as f:
        db_dict = pickle.load(f)

    # print(type(db_dict.keys()))
    # print(db_dict)
    db_dict_keys = list(db_dict.keys())
    depth_list = {str(key).split('_')[-1] for key in db_dict_keys}
    depth_list = sorted(depth_list)
    width_list = {str(key).split('_')[1] for key in db_dict_keys}
    width_list = sorted(width_list)
    radious_list = {str(key).split('_')[3] for key in db_dict_keys}
    radious_list = sorted(radious_list)
    print(width_list)
    print(radious_list)

    # display
    for depth, width in product(depth_list, width_list):
    # for depth, radious in product(depth_list, radious_list):
        # create display_dict
        display_dict = {} # {width_x_radious_y : {100 : 584, 125 : 540, 150 : 560, ..., 200 : 570}}的な
        for key, value in db_dict.items():
            depth_ = key.split('_')[-1]
            if depth_ != depth:
                continue
            display_dict_key = key.split('_target_pressure')[0]
            if display_dict_key not in display_dict.keys():
                display_dict[display_dict_key] = []
            target_pressure = key.split('_')[6]
            if target_pressure == '0':
                continue
            bend_sensor_mean = value[0]['bend_sensor_mean']
            display_dict[display_dict_key].append([int(target_pressure), float(bend_sensor_mean)])

        plt.figure()
        # width ver !!! #############################
        for key, plot_data in display_dict.items():
            if f'width_{width}' not in key:
                continue
            plot_data = sorted(plot_data) # 0番目、目標圧力値でソート
            plot_data = np.array(plot_data)
            print(key)
            if 'minus' in key:
                color = 'red'
            elif key.split('_')[-1] == '0':
                color = 'blue'
            else:
                color = 'green'
            fig_title = f'depth_{depth}_width_{width}'
            plt.title(fig_title)
            plt.ylim([520, 590])
            plt.plot(
                plot_data[:, 0],
                plot_data[:, 1],
                label=key,
                color=color)
            plt.legend()

        # ### radious ver !!!! ######################
        # for key, plot_data in display_dict.items():
        #     if f'radious_{radious}' not in key:
        #         continue
        #     plot_data = sorted(plot_data) # 0番目、目標圧力値でソート
        #     plot_data = np.array(plot_data)
        #     print(key)
        #     if f'width_{width_list[0]}' in key:
        #         color = 'red'
        #     if f'width_{width_list[1]}' in key:
        #         color = 'darkorchid'
        #     if f'width_{width_list[2]}' in key:
        #         color = 'pink'
        #     fig_title = f'depth_{depth}_radious_{radious}'
        #     plt.title(fig_title)
        #     plt.ylim([520, 590])
        #     plt.plot(
        #         plot_data[:, 0],
        #         plot_data[:, 1],
        #         label=key,
        #         color=color)
        #     plt.legend()

        plt.savefig(args.result_dir_path + f'/{fig_title}')
        # plt.show()
        plt.close()



if __name__=='__main__':
    main()
