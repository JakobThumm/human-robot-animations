#!/usr/bin/env python
"""
author: Erick Álvarez
contributors: Julian Balletshofer
"""
import os
import pickle
import argparse
import numpy as np
from motion_capture.help_scripts.angle_estimation import estimate_rotation_between_joints, \
    rotation_dict_to_angle_dict
from motion_capture.readers.readViconCSV import get_first_frame, frames_joint_information, estimate_t_pose_info
from motion_capture.config_util import CONFIG_YAML

# Measurements are given in cm. We want to convert them to meters.
UNIT_TRANSFORMATION = 0.01


def main(input_file, output_folder, verbose=False):
    """
    Transforms the animations recordings into bvh file format.
    Additionally, it creates a json file containing the parameters that will be needed for editing the motion
    in blender.
    Args:
        input_file: a csv file with the animation recording
        output_folder: the folder where the bvh file will be saved
        verbose: if true, it prints information to the console
    """
    file_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_folder, file_name + ".pkl")
    info = frames_joint_information(input_file, verbose)
    first_entry = list(info.keys())[0]
    # info[first_entry].JOINT_VALUES['hip']
    joint_names = []
    for joint_name in info[first_entry].JOINT_VALUES.keys():
        if joint_name != 'ROOT':
            joint_names.append(joint_name)
    with open(output_folder + "/joint_names.yml", 'w', newline='') as file_handle:
        for joint in info[first_entry].JOINT_VALUES.keys():
            if joint == 'ROOT':
                continue
            file_handle.write("{}: {}\n".format(joint_names.index(joint), joint))
        file_handle.close()
    n_joints = len(joint_names)
    joint_motions = np.zeros((len(info), n_joints, 3), dtype=np.float32)
    count = 0
    for key in info.keys():
        for joint in info[key].JOINT_VALUES.keys():
            if joint == 'ROOT':
                continue
            joint_motions[count, joint_names.index(joint), :] = UNIT_TRANSFORMATION * info[key].JOINT_VALUES[joint].global_pos
        count += 1
    output = open(output_file, "wb")
    pickle.dump(joint_motions, output)
    output.close()
    stop = 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Vicon CSV file to BVH file')
    parser.add_argument('--csv_file', required=True, help='Vicon CSV file')
    parser.add_argument('--verbose', action='store_true', help='Use this argument to print to the console.')
    args = parser.parse_args()

    input_file = args.csv_file
    main(input_file, args.verbose)
