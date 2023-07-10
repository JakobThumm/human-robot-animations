"""This file defines a converter from BVH to pickle animations.

Load in a human animation BVH file and transform it to an usable human animation.

Owner:
    Jakob Thumm (JT)

Contributors:
    Julian Balletshofer
Changelog:
    2.5.22 JT Formatted docstrings
    11.6.22 changed the way angles are red and safed to be conform with the simulation -
    now from zxy to xyz since assumption that mujoco assumes xyz
    23.6.22 added try and except
    23.6.22 created function for pipeline + added outpath
"""
import argparse
import os
import numpy as np
import pickle

from bvh import Bvh
from scipy.spatial.transform import Rotation


def convert_to_mujoco(path, output):
    file_name, file_extension = os.path.splitext(path)
    assert file_extension == ".bvh", "BVH file has to end in .bvh"
    assert os.path.isfile(path), "BVH file does not exist!"
    # else:
    # split .bvh away
    output = output.rsplit('.', 1)[0]
    # create new save_path
    save_path = output + ".pkl"

    # << Load BVH file >>
    with open(path) as f:
        mocap = Bvh(f.read())
    mocap.get_joint_channels_index("hip")
    mocap.get_joint("hip")
    # write the corresponding name of each recorded joint
    mujoco_to_mocap_names = {
        "L_Hip": None,
        "R_Hip": None,
        "Torso": "torso",
        "L_Knee": None,
        "R_Knee": None,
        "Spine": None,
        "L_Ankle": None,
        "R_Ankle": None,
        "Chest": None,
        "L_Toe": None,
        "R_Toe": None,
        "Neck": "neck",
        "L_Thorax": "left_collar",
        "R_Thorax": "right_collar",
        "Head": "head",
        "L_Shoulder": "left_upper_arm",
        "R_Shoulder": "right_upper_arm",
        "L_Elbow": "left_forearm",
        "R_Elbow": "right_forearm",
        "L_Wrist": "left_hand",
        "R_Wrist": "right_hand",
        "L_Hand": None,
        "R_Hand": None,
    }
    frames = np.asarray(mocap.frames, dtype=np.float64, order="C")
    data = {}
    channel_dict = {}
    base_idx = mocap.get_joint_channels_index("hip")
    for (i, channel_name) in enumerate(mocap.joint_channels("hip")):
        channel_dict[channel_name] = base_idx + i
    # check if motion lines are empty - could sometimes happen
    # if they are empty you can't access them with frames[:,channel_dict["Xposition"]]
    # only safes working files into mujoco folder
    try:
        data["Pelvis_pos_y"] = frames[:, channel_dict["Yposition"]] / 1000
        # issue: human walked into wrong direction
        # transformation to align with mujoco
        # negation of z,x data to align coord. system with mujoco
        # alternatively 180 degress around y-axis
        data["Pelvis_pos_z"] = -frames[:, channel_dict["Zposition"]] / 1000
        data["Pelvis_pos_x"] = -frames[:, channel_dict["Xposition"]] / 1000

        # switched x,y since human rotated around the wrong axes
        rot = Rotation.from_euler(
             "ZYX",
             np.swapaxes(
                 np.array(
                     [
                        # issue: rotaitons were around the wrong axes + wrong direction
                        # switch x and y axes for right rotation axes
                        # negation since animation rotated in wrong direction
                        frames[:, channel_dict["Zrotation"]],
                        frames[:, channel_dict["Xrotation"]],
                        -frames[:, channel_dict["Yrotation"]],
                     ]
                 ),
                 0,
                 1,
             ),
             degrees=True,
         )

        data["Pelvis_quat"] = rot.as_quat()

        for joint_name in mujoco_to_mocap_names:

            if mujoco_to_mocap_names[joint_name] is not None:
                mocap_name = mujoco_to_mocap_names[joint_name]
                base_idx = mocap.get_joint_channels_index(mocap_name)
                channel_dict = {}
                for (i, channel_name) in enumerate(mocap.joint_channels(mocap_name)):
                    channel_dict[channel_name] = base_idx + i

                # BVH files store rotations around joints as euler zxy rotation
                # mujoco takes the individual rotations ordered by xyz (assumption from testing)
                # convert zxy to xyz as the following
                # negate x,y rotation to be able to use same human.xml file as cmu
                for j in range(len(frames[:, channel_dict["Xrotation"]])):

                    x_rot = -frames[j, channel_dict["Xrotation"]]
                    y_rot = frames[j, channel_dict["Yrotation"]]
                    z_rot = -frames[j, channel_dict["Zrotation"]]

                    rot_zxy = Rotation.from_euler('zxy', [z_rot, x_rot, y_rot], degrees=True)

                    rot_xyz = rot_zxy.as_euler('xyz', degrees=True)

                    frames[j, channel_dict["Xrotation"]] = rot_xyz[0]
                    frames[j, channel_dict["Yrotation"]] = rot_xyz[1]
                    frames[j, channel_dict["Zrotation"]] = rot_xyz[2]

                data[joint_name + "_x"] = np.clip(
                    np.radians(frames[:, channel_dict["Xrotation"]]), -1.56, 1.56
                )
                data[joint_name + "_y"] = np.clip(
                    np.radians(frames[:, channel_dict["Yrotation"]]), -1.56, 1.56
                )
                data[joint_name + "_z"] = np.clip(
                    np.radians(frames[:, channel_dict["Zrotation"]]), -1.56, 1.56
                )

            else:
                data[joint_name + "_x"] = np.zeros(data["Pelvis_pos_x"].shape)
                data[joint_name + "_y"] = np.zeros(data["Pelvis_pos_x"].shape)
                data[joint_name + "_z"] = np.zeros(data["Pelvis_pos_x"].shape)

        output = open(save_path, "wb")
        pickle.dump(data, output)
        output.close()
    except:
        print("this following files has no motion lines " + file_name)


if __name__ == "__main__":
    # << Load in arguments >>
    parser = argparse.ArgumentParser(
        description="Convert a BVH motion capture file to a usable animation and save the animation as a pickle file."
    )
    parser.add_argument("path", help="Path to bvh file. Has to end in .bvh", type=str)
    parser.add_argument(
        "--save_path",
        "-s",
        help="Path to save the pickle file. Has to end in .pkl",
        type=str,
    )
    args = parser.parse_args()
    path = args.path
