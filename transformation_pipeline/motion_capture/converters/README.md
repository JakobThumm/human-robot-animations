# CSV to BVH
The script viconCSV_to_bvh.py performs the conversion of the CSV file into the BVH format. The input for this file are
the CSV file of the animation one wants to transform and the CSV file of the recording of the t-pose.

The output of this script is 2 files. If the name of the CSV file with the motion is 
<motion_file_name>.csv, then the output is <motion_file_name>.bvh. This file 
contains the motion in BVH format.

This script needs that the following parameters of the config file have valid values:
+ JOINTS_HIERARCHY
+ ROOT_JOINT
+ BONE_HIERARCHY
+ BONE_END_BVH_NAME
+ BONE_BEGIN_AT_JOINT
+ BONE_END_AT_JOINT
+ joint_name_pattern_csv

Other values still need to be present in the config file but can have any value. We recommend doing this, if the
purpose is to run this **just this script**.

---

# BVH to Mujoco

The script convert_bvh.py takes the data from the .bvh file and converts it into a format that is usable for Mujoco. Here we apply some transformations to align the coordinate axes with the one in Mujoco. Additionally we convert the Euler-Rotation that is defined as zxy in the bvh file to xyz and scale the coordinates from millimeter to meter to align with Mujoco.


