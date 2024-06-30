#!/usr/bin/env python
"""
author: Erick Álvarez
contributors: Julian Balletshofer
"""
import argparse
import numpy as np
from motion_capture.help_scripts.angle_estimation import estimate_rotation_between_joints, \
    rotation_dict_to_angle_dict
from motion_capture.config_util import CONFIG_YAML

if CONFIG_YAML.READER == "Vicon":
    from motion_capture.readers.readViconCSV import get_first_frame, frames_joint_information, estimate_t_pose_info
elif CONFIG_YAML.READER == "Lara":
    from motion_capture.readers.readLaraCSV import get_first_frame, frames_joint_information, estimate_t_pose_info
else:
    raise RuntimeError("No valid reader defined in the yaml config")


def create_bvh_hierarchy_str(t_pose_dirs, inter_joints_dists):
    """
    Estimates the hierarchy lines for the bvh file
    Args:
        t_pose_dirs (dict): direction vectors between (parent_joint, child_joint) pairs of the hierarchy.
        Measured from the t-pose.
        inter_joints_dists (dict): distance between (parent_joint, child_joint) pairs of the hierarchy.
        Measured from the t-pose. Distances measured in x, y ans z axis separately.

    Returns:
        the hierarchy of a bvh file
    """

    def estimate_positions_with_new_dists(parent_label, parent_pos):
        positions = {}
        base_bone_label = CONFIG_YAML.ROOT_JOINT
        if parent_label == base_bone_label:
            positions[base_bone_label] = np.array([0.0, 0.0, 0.0])
            parent_pos = np.array([0.0, 0.0, 0.0])
        for child_l in CONFIG_YAML.JOINTS_HIERARCHY[parent_label]:
            key = (parent_label, child_l)
            # t_pose einheitsvec * len
            child_pos = parent_pos + t_pose_dirs[key] * inter_joints_dists[key]
            positions[child_l] = child_pos
            # recursion of child bone with respect to previous
            child_positions = estimate_positions_with_new_dists(child_l, child_pos)
            positions.update(child_positions)
        return positions

    def estimate_offsets(positions, parent_bone_label, parent_begin):
        # calc how joints are relative to root
        offsets = {}
        base_bone_label = CONFIG_YAML.ROOT_BONE
        if parent_bone_label == base_bone_label:
            offsets[base_bone_label + '_x'] = 0.0
            offsets[base_bone_label + '_y'] = 0.0
            offsets[base_bone_label + '_z'] = 0.0
            parent_begin = np.array([0.0, 0.0, 0.0])

        for child_bone_l in CONFIG_YAML.BONE_HIERARCHY[parent_bone_label]:
            child_begin = positions[CONFIG_YAML.BONE_BEGIN_AT_JOINT[child_bone_l]]
            # just x,y,z substracted
            offset = child_begin - parent_begin
            offsets[child_bone_l+'_x'] = offset[0]
            offsets[child_bone_l+'_y'] = offset[1]
            offsets[child_bone_l+'_z'] = offset[2]
            child_offsets = estimate_offsets(positions, child_bone_l, child_begin)
            offsets.update(child_offsets)
        return offsets
    # start recursive estimation
    positions_with_dists = estimate_positions_with_new_dists(CONFIG_YAML.ROOT_JOINT, None)
    bones_offsets = estimate_offsets(positions_with_dists, CONFIG_YAML.ROOT_BONE, None)

    def getHierarchyLines(offsets_dict):
        lines = []

        def _rec_est(parent_l, depth):

            for current_l in CONFIG_YAML.BONE_HIERARCHY[parent_l]:
                if current_l.endswith('_end'):
                    bone_bvh_name = CONFIG_YAML.BONE_END_BVH_NAME[current_l]
                else:
                    bone_bvh_name = current_l
                lines.append('  ' * depth + f'JOINT {bone_bvh_name}')
                lines.append('  ' * depth + '{')
                depth += 1
                lines.append('  ' * depth + 'OFFSET {} {} {}'.format(

                    offsets_dict[current_l + '_x'],
                    offsets_dict[current_l + '_y'],
                    offsets_dict[current_l + '_z']

                ))
                lines.append('  ' * depth + 'CHANNELS 3 Zrotation Xrotation Yrotation')
                if current_l.endswith('_end'):
                    lines.append('  ' * depth + 'End Site')
                    lines.append('  ' * depth + '{')
                    lines.append(
                        '  ' * (depth + 1) + 'OFFSET 0.0 0.0 0.0')
                    lines.append('  ' * depth + '}')
                else:
                    _rec_est(current_l, depth)
                depth -= 1
                lines.append('  ' * depth + '}')

        lines.append('HIERARCHY')
        lines.append(f'ROOT {CONFIG_YAML.ROOT_BONE}')
        lines.append('{')
        depth = 1
        lines.append('  ' * depth + 'OFFSET {} {} {}'.format(
            offsets_dict[CONFIG_YAML.ROOT_BONE + '_x'],
            offsets_dict[CONFIG_YAML.ROOT_BONE + '_y'],
            offsets_dict[CONFIG_YAML.ROOT_BONE + '_z']
        ))
        lines.append('  ' * depth + 'CHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation')
        _rec_est(CONFIG_YAML.ROOT_BONE, depth)
        lines.append('}')
        return lines

    hierarchy_lines = getHierarchyLines(bones_offsets)

    return '\n'.join(hierarchy_lines)


def estimate_motion_lines(frames_keys, frames_info, t_pose_dirs, base_t_pose_angle):
    """
    Estimates the motion lines of the bvh file.
    Args:
        frames_keys (list): list with keys in order to extract inorder the frames of frames info
        frames_info (dict): dictionary with Frame_information (parsed values of recording).
        The key in the dictionary corresponds to the timestep of the frame.
        t_pose_dirs (dict): direction vectors between (parent_joint, child_joint) pairs of the hierarchy.
        Measured from the t-pose.
        base_t_pose_angle: the angle that the root bone has in the t_pose

    Returns:
        lines: the motion lines in bvh format
    """
    rots_dicts_per_frame = []
    joint_position_dict_per_frame = []

    for fr_n in range(len(frames_keys)):
        current_frame = frames_info[frames_keys[fr_n]]
        rotation_dict = estimate_rotation_between_joints(t_pose_dirs, base_t_pose_angle, current_frame,
                                                         CONFIG_YAML.JOINTS_HIERARCHY, CONFIG_YAML.ROOT_JOINT)
        rots_dicts_per_frame.append(rotation_dict)

        dict = {}
        for j_name in CONFIG_YAML.JOINTS_NAMES:
            dict[j_name] = current_frame.JOINT_VALUES[j_name].global_pos
        joint_position_dict_per_frame.append(dict)

    def get_order_list_angle_keys():
        angle_keys = []

        def _rec_est(parent_l):

            for current_l in CONFIG_YAML.JOINTS_HIERARCHY[parent_l]:
                angle_keys.append((parent_l, current_l, 'z'))
                angle_keys.append((parent_l, current_l, 'x'))
                angle_keys.append((parent_l, current_l, 'y'))

                if len(CONFIG_YAML.JOINTS_HIERARCHY[current_l]) == 0:
                    angle_keys.append('dummy')
                    angle_keys.append('dummy')
                    angle_keys.append('dummy')
                else:
                    _rec_est(current_l)

        angle_keys.append(('ROOT', CONFIG_YAML.ROOT_JOINT, 'z'))
        angle_keys.append(('ROOT', CONFIG_YAML.ROOT_JOINT, 'x'))
        angle_keys.append(('ROOT', CONFIG_YAML.ROOT_JOINT, 'y'))
        _rec_est(CONFIG_YAML.ROOT_JOINT)
        return angle_keys

    order_angle_keys = get_order_list_angle_keys()
    lines = []
    for i in range(len(frames_keys)):
        rot_dict = rots_dicts_per_frame[i]
        angles_dict = rotation_dict_to_angle_dict(rot_dict)
        angles_dict['dummy'] = 0.
        bvh_row_angles = [angles_dict[key] for key in order_angle_keys]
        if CONFIG_YAML.INIT_TRANSFORMATION_YZ:
            bvh_row_angles[1], bvh_row_angles[2] = bvh_row_angles[2], bvh_row_angles[1]
        pos_dict = joint_position_dict_per_frame[i]
        bvh_row_pos = [pos_dict[CONFIG_YAML.ROOT_JOINT][i] for i in [0, 1, 2]]
        bvh_row = bvh_row_pos + bvh_row_angles
        bvh_row_str = [str(el) for el in bvh_row]
        lines.append(' '.join(bvh_row_str))
    return lines


def create_bvh_file(frames_info, t_pose_dirs, inter_joints_dists, base_t_pose_angle, filename):
    """
    Creates the bvh file from the recorded measures.
    Args:
        frames_info (dict): dictionary with Frame_information (parsed values of recording).
        The key in the dictionary corresponds to the timestep of the frame.
        t_pose_dirs (dict): direction vectors between (parent_joint, child_joint) pairs of the hierarchy.
        Measured from the t-pose.
        inter_joints_dists (dict): distance between (parent_joint, child_joint) pairs of the hierarchy.
        base_t_pose_angle: the angle that the root bone has in the t_pose
        filename: the nam    if args.postprocess and args.toBVH:
        interPolateCSV(args.directory, args.verbose)
        convertToBVH(args.directory, args.verbose)

    elif args.postprocess:
        interPolateCSV(args.directory, args.verbose)

    elif args.toBVH:
        convertToBVH(args.directory, args.verbose)
    e of the file that is created

    """
    hierarchy_str = create_bvh_hierarchy_str(t_pose_dirs, inter_joints_dists)
    frames_keys = list(frames_info.keys())
    frames_keys.sort(key=int)

    lines = estimate_motion_lines(frames_keys, frames_info, t_pose_dirs, base_t_pose_angle)
    # assert len(lines[0].split(" ")) == 39  # 3*number joints
    with open(filename, 'w', newline='') as file_handle:
        file_handle.write(hierarchy_str)
        file_handle.write('\n')
        file_handle.write('MOTION\n')
        file_handle.write('Frames: {}\n'.format(len(frames_keys)))
        file_handle.write('Frame Time: {}\n'.format(1. / CONFIG_YAML.FPS))
        file_handle.write('\n'.join(lines))


def main(input_file, t_pose_file, use_first_frame_as_tpose=False, verbose=False):
    """
    Transforms the animations recordings into bvh file format.
    Additionally, it creates a json file containing the parameters that will be needed for editing the motion
    in blender.
    Args:
        input_file: a csv file with the animation recording
        t_pose_file: a csv file with the recording of the t-pose
    """
    output_file = input_file.replace('.csv', '.bvh')
    info = frames_joint_information(input_file, verbose)
    if use_first_frame_as_tpose:
        first_t_pose_info = get_first_frame(frames_info=info)
    else:
        t_pose_info = frames_joint_information(t_pose_file, verbose)
        first_t_pose_info = get_first_frame(frames_info=t_pose_info)
    # parameters according to the recordings
    measured_inter_joints_dists, measured_t_pose_dirs, measured_base_t_pose_angle = estimate_t_pose_info(
        CONFIG_YAML.JOINTS_HIERARCHY,
        first_t_pose_info,
        CONFIG_YAML.ROOT_JOINT
    )
    create_bvh_file(info, measured_t_pose_dirs, measured_inter_joints_dists, measured_base_t_pose_angle,
                    filename=output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Vicon CSV file to BVH file')
    parser.add_argument('--csv_file', required=True, help='Vicon CSV file')
    parser.add_argument('--t_pose_file', required=True, help='T-pose Vicon CSV file')
    parser.add_argument('--verbose', action='store_true', help='Use this argument to print to the console.')
    args = parser.parse_args()

    input_file = args.csv_file
    t_pose_file = args.t_pose_file
    main(input_file, t_pose_file, args.verbose)
