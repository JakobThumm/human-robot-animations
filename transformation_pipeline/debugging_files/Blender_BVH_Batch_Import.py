import bpy
import os

path = "/home/manuel/Downloads/HIWI/human-robot-animations/Lara_Tailored/"
#parts_list = ['head', 'head_end', 'L_collar', 'L_elbow', 'L_femur', 'L_foot', 'L_humerus',
#              'L_tibia', 'L_toe', 'L_wrist', 'L_wrist_end', 'lower_back', 'R_collar',
#              'R_elbow', 'R_femur', 'R_foot', 'R_humerus', 'R_tibia', 'R_toe', 'R_wrist',
#              'R_wrist_end', 'root']
parts_list = ['head', 'head_end', 'L_collar', 'L_elbow', 'L_humerus',
              'L_wrist', 'L_wrist_end', 'lower_back', 'R_collar',
              'R_elbow', 'R_humerus', 'R_wrist',
              'R_wrist_end', 'root']

for a in parts_list:
    bpy.ops.import_anim.bvh(filepath=path+a+".bvh", global_scale=0.001)