#!/usr/bin/env python
"""
author: Marc Gavilán Gil
contributors: José Martinho, Julian Balletshofer
"""
import numpy as np
import csv
import re
from motion_capture.config_util import CONFIG_YAML
from scipy.spatial.transform import Rotation


class Joint:
    def __init__(self, name, global_pos=np.array([0., 0., 0.]), global_angle=np.array([0., 0., 0.])):
        self.name = name
        self.local_pos = np.array([])
        self.local_angle = np.array([])
        self.global_pos = global_pos
        self.global_angle = global_angle

    def __repr__(self):
        return "Global pos: {}, Global angles: {}, Local pos: {}, Local angles {}" \
            .format(self.global_pos, self.global_angle, self.local_pos, self.local_angle)

    def set_global_pos(self, pos):
        self.global_pos = pos

    def set_local_pos(self, pos):
        self.local_pos = pos

    def set_global_angle(self, angle):
        self.global_angle = angle

    def set_local_angle(self, angle):
        self.local_angle = angle


class Frame_information:
    def __init__(self, number, hierarchy):
        self.number = number
        self.JOINT_VALUES = {}
        for k, _ in hierarchy.items():
            self.JOINT_VALUES[k] = Joint(k)

    def __repr__(self):
        return "Frame number {}: {}".format(self.number, self.JOINT_VALUES)


def frames_joint_information(input_file, verbose=False):
    """
    Extract global and local, position and angle, from all the joints, from all the frames in the csv file
    """
    # calculate local frames data ??
    def assign_local_values(parent_name, frame: Frame_information):
        for child_ in CONFIG_YAML.JOINTS_HIERARCHY[parent_name]:
            local_a = frame.JOINT_VALUES[child_].global_angle - frame.JOINT_VALUES[parent_name].global_angle
            local_p = frame.JOINT_VALUES[child_].global_pos - frame.JOINT_VALUES[parent_name].global_pos
            frame.JOINT_VALUES[child_].set_local_angle(local_a)
            frame.JOINT_VALUES[child_].set_local_pos(local_p)
            assign_local_values(child_, frame)

    def even_chunks(list, n):
        for i in range(0, len(list), n):
            yield list[i:i + n]

    with open(input_file, newline='') as csvfile:
        viconreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(viconreader)
        next(viconreader)

        # First we want to check the order in which the joints appear
        # The first two columns of our CSV file are not important
        # Then, there is a joint every 6 positions
        # give row with all joints
        tmp = next(viconreader)[2:]
        joint_keys_and_indices = {}

        # file may contain irrelevant rows
        relevant_keys = []
        for k1, k2 in zip(CONFIG_YAML.BONE_BEGIN_AT_JOINT, CONFIG_YAML.BONE_END_AT_JOINT):
            relevant_keys.append(CONFIG_YAML.BONE_BEGIN_AT_JOINT[k1])
            relevant_keys.append(CONFIG_YAML.BONE_END_AT_JOINT[k2])

        for i in range(int(len(tmp) / 6)):
            joint = tmp[i * 6]
            joint = joint[10:]  # remove Subject01:
            if joint in relevant_keys:
                joint_keys_and_indices[joint] = i
        # Then we want to read the value for angles and positions.
        # use next to skip to row with data
        next(viconreader)
        next(viconreader)
        frames_info = {}
        row_counter = 0.
        valid_row_counter = 0.
        for frame_raw in viconreader:
            row_counter += 1.
            if (frame_raw) == []:
                continue
            frame_inf = Frame_information(frame_raw[0], CONFIG_YAML.JOINTS_HIERARCHY)
            frame_raw = frame_raw[2:]

            valid_row = True
            for joint_name, joint_index in joint_keys_and_indices.items():
                values = frame_raw[joint_index * 6:joint_index * 6 + 6]
                empty_b = [v == '' for v in values]
                if any(empty_b):
                    valid_row = False
                    break
                # rotation of data to preprepare for the next step
                # prepare data for bvh convention of y-up
                # coordinate system recording (looking at robot): z-up, x-right, y-away
                # coordinate system after the following: y-up, x-right, z-towards
                # in case of new vicon coord system, add here another rotation to align current again
                rot2 = Rotation.from_euler('z', 90, degrees=True)
                rot1 = Rotation.from_euler('y', 90, degrees=True) 
                rot0 = Rotation.from_euler('z', -90, degrees=True)
                compose = rot2*rot1*rot0

                global_pos = np.array([float(val) for val in values[3:]])

                # directly apply on position since no translation
                global_pos = compose.apply(global_pos)

                # first convert to rot vec
                global_angle = np.array([float(ang) for ang in values[:3]])
                if CONFIG_YAML.ROTATION_IN_DEGREE:
                    global_angle = np.deg2rad(global_angle)
                rot_vec = Rotation.from_rotvec(global_angle)
                # now apply rotation to rot vec and transform back into radians
                global_angle = Rotation.as_rotvec(compose*rot_vec, degrees=False)

                # set the values
                frame_inf.JOINT_VALUES[joint_name].set_global_pos(global_pos)
                frame_inf.JOINT_VALUES[joint_name].set_global_angle(global_angle)

            # Then it's time to build the dictionary, using HIERARCHY to calculate
            # the local positions and angles
            if valid_row:
                valid_row_counter += 1.

                assign_local_values("ROOT", frame_inf)
                frames_info[frame_inf.number] = frame_inf

        if verbose:
            print(f"The rate of valid row is: {round(valid_row_counter/row_counter, 2) * 100} %")
    return frames_info


def get_first_frame(frames_info):
    """
    Selects and return first frame from the dictionary containing all frames
    Args:
        frames_info (dict): dictionary with Frame_information (parsed values of recording).
        The key in the dictionary corresponds to the timestep of the frame.

    Returns:
        first_frame: the frame information of the first timestep
    """
    frames_indices = [int(s) for s in frames_info.keys()]
    frames_indices.sort()
    first_frame = frames_info[str(frames_indices[0])]
    return first_frame


def estimate_t_pose_info(hierarchy, frame_info, root_node):
    """
    Estimate directions vectors and offsets between parent and child elements in the hierarchy.
    Additionally, it estimates the orientation of the root bone at the t_pose.
    Args:
        hierarchy (dict): dictionary describing the hierarchical relation of the elements. The key is the parent
        element and the value is a list. The list contains all the child elements of the parent
        frame_info (Frame_information): object containing information of a line of the parsed CSV.
        root_node: the root/first element of the hierarchy

    Returns:
        dir_vectors (dict): direction vectors between (parent_joint, child_joint) pairs of the hierarchy.
        Measured from the t-pose.
        distance_dict (dict): distance between (parent_joint, child_joint) pairs of the hierarchy.
        Measured from the t-pose. Distances measured in x, y ans z axis separately.
        base_t_pose_angle: the angle (orientation) of the root bone from the t_pose recording.
        Angle in axis-angle representation
    """
    base_t_pose_angle = frame_info.JOINT_VALUES[root_node].global_angle
    distance_dict = {}
    dir_vectors = {}

    # estimate the direction vectors between each joints in resting
    def _rec_est(parent_label, parent_pos):
        for child_l in hierarchy[parent_label]:
            child_pos = frame_info.JOINT_VALUES[child_l].global_pos
            dir = child_pos - parent_pos
            l = np.linalg.norm(dir)
            assert l > 0
            key = (parent_label, child_l)
            distance_dict[key] = l
            dir_vectors[key] = dir / l
            _rec_est(child_l, child_pos)

    root_pos = frame_info.JOINT_VALUES[root_node].global_pos
    _rec_est(root_node, root_pos)

    return distance_dict, dir_vectors, base_t_pose_angle


def estimate_t_pose_dirs_and_dists(hierarchy, root_label, global_pos_dict):
    """
    Estimate directions vectors and offsets between parent and child elements in the hierarchy
    Args:
        hierarchy (dict): dictionary describing the hierarchical relation of the elements. The key is the parent
        element and the value is a list. The list contains all the child elements of the parent
        root_label: the root/first element (key) of the hierarchy
        global_pos_dict (dict): a dictionary containing the global position of all elements od the hierarchy

    Returns:
        dir_vectors (dict): direction vectors between (parent_joint, child_joint) pairs of the hierarchy.
        Measured from the t-pose.
        distance_dict (dict): distance between (parent_joint, child_joint) pairs of the hierarchy.
        Measured from the t-pose. Distances measured in x, y ans z axis separately.
    """
    dir_vectors = {}
    distance_dict = {}

    def _rec_est(current_label, current_pos):
        for child_l in hierarchy[current_label]:
            child_pos = global_pos_dict[child_l]
            vec = child_pos - current_pos
            l = np.linalg.norm(vec)
            dir = vec / l
            dir_vectors[(current_label, child_l)] = dir
            distance_dict[(current_label, child_l)] = l
            _rec_est(child_l, child_pos)

    _rec_est(root_label, global_pos_dict[root_label])

    return dir_vectors, distance_dict
