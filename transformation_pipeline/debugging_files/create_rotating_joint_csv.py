import csv
import math
import numpy as np


header_v1 = "sample,label,head_RX,head_RY,head_RZ,head_TX,head_TY,head_TZ,head end_RX,head end_RY,head end_RZ,head end_TX,head end_TY,head end_TZ,L collar_RX,L collar_RY,L collar_RZ,L collar_TX,L collar_TY,L collar_TZ,L elbow_RX,L elbow_RY,L elbow_RZ,L elbow_TX,L elbow_TY,L elbow_TZ,L femur_RX,L femur_RY,L femur_RZ,L femur_TX,L femur_TY,L femur_TZ,L foot_RX,L foot_RY,L foot_RZ,L foot_TX,L foot_TY,L foot_TZ,L humerus_RX,L humerus_RY,L humerus_RZ,L humerus_TX,L humerus_TY,L humerus_TZ,L tibia_RX,L tibia_RY,L tibia_RZ,L tibia_TX,L tibia_TY,L tibia_TZ,L toe_RX,L toe_RY,L toe_RZ,L toe_TX,L toe_TY,L toe_TZ,L wrist_RX,L wrist_RY,L wrist_RZ,L wrist_TX,L wrist_TY,L wrist_TZ,L wrist end_RX,L wrist end_RY,L wrist end_RZ,L wrist end_TX,L wrist end_TY,L wrist end_TZ,lower back_RX,lower back_RY,lower back_RZ,lower back_TX,lower back_TY,lower back_TZ,R collar_RX,R collar_RY,R collar_RZ,R collar_TX,R collar_TY,R collar_TZ,R elbow_RX,R elbow_RY,R elbow_RZ,R elbow_TX,R elbow_TY,R elbow_TZ,R femur_RX,R femur_RY,R femur_RZ,R femur_TX,R femur_TY,R femur_TZ,R foot_RX,R foot_RY,R foot_RZ,R foot_TX,R foot_TY,R foot_TZ,R humerus_RX,R humerus_RY,R humerus_RZ,R humerus_TX,R humerus_TY,R humerus_TZ,R tibia_RX,R tibia_RY,R tibia_RZ,R tibia_TX,R tibia_TY,R tibia_TZ,R toe_RX,R toe_RY,R toe_RZ,R toe_TX,R toe_TY,R toe_TZ,R wrist_RX,R wrist_RY,R wrist_RZ,R wrist_TX,R wrist_TY,R wrist_TZ,R wrist end_RX,R wrist end_RY,R wrist end_RZ,R wrist end_TX,R wrist end_TY,R wrist end_TZ,root_RX,root_RY,root_RZ,root_TX,root_TY,root_TZ\n"
header = "Segments\n" + \
    "200\n" + \
    ",,Subject01:Head,,,,,,Subject01:Head_End,,,,,,Subject01:L_Collar,,,,,,Subject01:L_Elbow,,,,,,Subject01:L_Femur,,,,,,Subject01:L_Foot,,,,,,Subject01:L_Humerus,,,,,,Subject01:L_Tibia,,,,,,Subject01:L_Toe,,,,,,Subject01:L_Wrist,,,,,,Subject01:L_Wrist_End,,,,,,Subject01:LowerBack,,,,,,Subject01:R_Collar,,,,,,Subject01:R_Elbow,,,,,,Subject01:R_Femur,,,,,,Subject01:R_Foot,,,,,,Subject01:R_Humerus,,,,,,Subject01:R_Tibia,,,,,,Subject01:R_Toe,,,,,,Subject01:R_Wrist,,,,,,Subject01:R_Wrist_End,,,,,,Subject01:Root,,,,,,\n" +\
    "Frame,Sub Frame,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ,RX,RY,RZ,TX,TY,TZ\n" +\
    ",,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm,deg,deg,deg,mm,mm,mm\n"

# starting poses
head = [1.909999999999882903e-01, -1.834699999999999775e+00, 2.448659999999999837e+00, -1.690000000000009095e+01, 4.029999999999995453e+01, 4.431999999999998181e+02]
head_end = [-1.909999999999882903e-01, -1.834699999999999775e+00, 2.448659999999999837e+00, -2.679999999999995453e+01, 5.129999999999995453e+01, 5.571999999999998181e+02]
L_collar = [-5.678999999999987836e+00, 7.354189999999999827e+01, -5.731089999999999662e+01, -1.240000000000009095e+01, 2.950000000000000000e+01, 3.245999999999999091e+02]
L_elbow = [-1.270649999999999977e+02, -6.649809999999999377e+01, 1.170541000000000054e+02, 2.632999999999999545e+02, -1.089999999999986358e+01, 5.769999999999981810e+01]
L_femur = [8.540000000000006253e+00, 8.730000000000000426e+00, 1.344209999999999994e+01, 1.104000000000000909e+02, 1.740000000000009095e+01, -1.345800000000000409e+02]
L_foot = [5.005000000000009663e+00, 3.168890000000000029e+01, -1.864789999999999992e+01, 1.910000000000000000e+02, 7.070000000000004547e+01, -1.014063000000000102e+03]
L_humerus = [2.613600000000000989e+01, 1.413009000000000128e+02, -1.169958999999999918e+02, 1.640999999999999091e+02, 2.290000000000009095e+01, 3.521999999999998181e+02]
L_tibia = [7.629000000000004889e+00, 8.646300000000000097e+00, 1.343110000000000070e+01, 1.512999999999999545e+02, 4.820000000000004547e+01, -5.851300000000001091e+02]
L_toe = [5.005000000000009663e+00, 3.168890000000000029e+01, -1.864789999999999992e+01, 1.949000000000000909e+02, -1.532999999999999545e+02, -1.023131000000000085e+03]
L_wrist = [-1.562459999999999809e+02, -5.828910000000000480e+01, 1.438740999999999985e+02, 2.110999999999999091e+02, -8.420000000000004547e+01, -1.648300000000000409e+02]
L_wrist_end = [-1.562459999999999809e+02, -5.828910000000000480e+01, 1.438740999999999985e+02, 2.297000000000000455e+02, -1.535999999999999091e+02, -2.343600000000001273e+02]
lower_back = [0.000000000000000000e+00, 0.000000000000000000e+00, 0.000000000000000000e+00, 0.000000000000000000e+00, 0.000000000000000000e+00, 0.000000000000000000e+00]
R_collar = [-2.657199999999999562e+01, -5.248810000000000286e+01, 7.396410000000000196e+01, -1.240000000000009095e+01, 2.950000000000000000e+01, 3.245999999999999091e+02]
R_elbow = [-4.513199999999999079e+01, -1.065990999999999929e+02, 1.688240999999999872e+02, -2.740000000000000000e+02, 1.920000000000004547e+01, 3.019999999999981810e+01]
R_femur = [-2.182999999999992724e+00, -2.530709999999999837e+01, -3.797090000000000032e+01, -1.035000000000000000e+02, 3.290000000000009095e+01, -1.371300000000001091e+02]
R_foot = [4.250000000000000000e+00, -2.294010000000000105e+01, 2.951409999999999911e+01, -1.389000000000000909e+02, 9.160000000000013642e+01, -1.016304000000000087e+03]
R_humerus = [-1.519979999999999905e+02, 1.077009000000000043e+02, -9.002490000000000236e+01, -1.907000000000000455e+02, 4.150000000000000000e+01, 3.305999999999999091e+02]
R_tibia = [6.482000000000013529e+00, -2.936809999999999832e+01, -3.602689999999999770e+01, -1.484000000000000909e+02, 3.860000000000013642e+01, -5.883100000000001728e+02]
R_toe = [4.250000000000000000e+00, -2.294010000000000105e+01, 2.951409999999999911e+01, -1.455000000000000000e+02, -1.322000000000000455e+02, -1.027730999999999995e+03]
R_wrist = [-2.602599999999999625e+01, -7.762210000000000321e+01, 1.501540999999999997e+02, -2.422000000000000455e+02, -5.729999999999995453e+01, -1.950900000000001455e+02]
R_wrist_end = [-2.602599999999999625e+01, -7.762210000000000321e+01, 1.501540999999999997e+02, -2.740000000000000000e+02, -1.125999999999999091e+02, -2.721300000000001091e+02]
root = [1.563600000000000989e+01, 3.095000000000000639e+00, 9.327999999999998515e-01, 3.500000000000000000e+00, 2.510000000000013642e+01, -1.358600000000001273e+02]

"""

head = [0, 0, 0, 0, 0, 0]
head_end = [0, 0, 0, 0, 0, 0]
L_collar = [0, 0, 0, 0, 0, 0]
L_elbow = [0, 0, 0, 0, 0, 0]
L_femur = [0, 0, 0, 0, 0, 0]
L_foot = [0, 0, 0, 0, 0, 0]
L_humerus = [0, 0, 0, 0, 0, 0]
L_tibia = [0, 0, 0, 0, 0, 0]
L_toe = [0, 0, 0, 0, 0, 0]
L_wrist = [0, 0, 0, 0, 0, 0]
L_wrist_end = [0, 0, 0, 0, 0, 0]
lower_back = [0, 0, 0, 0, 0, 0]
R_collar = [0, 0, 0, 0, 0, 0]
R_elbow = [0, 0, 0, 0, 0, 0]
R_femur = [0, 0, 0, 0, 0, 0]
R_foot = [0, 0, 0, 0, 0, 0]
R_humerus = [0, 0, 0, 0, 0, 0]
R_tibia = [0, 0, 0, 0, 0, 0]
R_toe = [0, 0, 0, 0, 0, 0]
R_wrist = [0, 0, 0, 0, 0, 0]
R_wrist_end = [0, 0, 0, 0, 0, 0]
root = [0, 0, 0, 0, 0, 0]
"""

#parts = [head, head_end, L_collar, L_elbow, L_femur, L_foot, L_humerus,
#         L_tibia, L_toe, L_wrist, L_wrist_end, lower_back, R_collar,
#         R_elbow, R_femur, R_foot, R_humerus, R_tibia, R_toe, R_wrist,
#         R_wrist_end, root]

parts_dict = {
    'head': head,
    'head_end': head_end,
    'L_collar': L_collar,
    'L_elbow': L_elbow,
    'L_femur': L_femur,
    'L_foot': L_foot,
    'L_humerus': L_humerus,
    'L_tibia': L_tibia,
    'L_toe': L_toe,
    'L_wrist': L_wrist,
    'L_wrist_end': L_wrist_end,
    'lower_back': lower_back,
    'R_collar': R_collar,
    'R_elbow': R_elbow,
    'R_femur': R_femur,
    'R_foot': R_foot,
    'R_humerus': R_humerus,
    'R_tibia': R_tibia,
    'R_toe': R_toe,
    'R_wrist': R_wrist,
    'R_wrist_end': R_wrist_end,
    'root': root
}
relevant_parts_dict = {
    'head': head,
    'head_end': head_end,
    'L_collar': L_collar,
    'L_elbow': L_elbow,
    'L_humerus': L_humerus,
    'L_wrist': L_wrist,
    'L_wrist_end': L_wrist_end,
    'lower_back': lower_back,
    'R_collar': R_collar,
    'R_elbow': R_elbow,
    'R_humerus': R_humerus,
    'R_wrist': R_wrist,
    'R_wrist_end': R_wrist_end,
    'root': root
}

parents_dict = {
    'head': L_collar,
    'head_end': head,
    'L_collar': lower_back,
    'L_elbow': L_humerus,
    'L_humerus': L_collar,
    'L_wrist': L_elbow,
    'L_wrist_end': L_wrist,
    'lower_back': lower_back,
    'R_collar': lower_back,
    'R_elbow': R_humerus,
    'R_humerus': R_collar,
    'R_wrist': R_elbow,
    'R_wrist_end': R_wrist,
    'root': root
}


# indices for moving
RX = 0
RY = 1
RZ = 2
TX = 3
TY = 4
TZ = 5

JointMovement = TZ


def rotate_point_3d(a, b, angle, axis):
    """
    Rotate point b around point a by a given angle in radians, around a specified axis.

    Parameters:
    a (tuple): The coordinates of point a (the center of rotation).
    b (tuple): The coordinates of point b (the point to rotate).
    angle (float): The angle of rotation in radians.
    axis (tuple): The axis of rotation (must be a unit vector).

    Returns:
    tuple: The new coordinates of point b after rotation.
    """
    # Convert a, b, axis to numpy arrays
    print(a)
    a = np.array(a)
    b = np.array(b)
    axis = np.array(axis)

    # Ensure the axis is a unit vector
    axis = axis / np.linalg.norm(axis)

    # Translate point b to origin relative to a
    b_relative = b - a

    # Rodrigues' rotation formula components
    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)
    ux, uy, uz = axis

    # Rotation matrix
    rotation_matrix = np.array([
        [cos_theta + ux ** 2 * (1 - cos_theta), ux * uy * (1 - cos_theta) - uz * sin_theta,
         ux * uz * (1 - cos_theta) + uy * sin_theta],
        [uy * ux * (1 - cos_theta) + uz * sin_theta, cos_theta + uy ** 2 * (1 - cos_theta),
         uy * uz * (1 - cos_theta) - ux * sin_theta],
        [uz * ux * (1 - cos_theta) - uy * sin_theta, uz * uy * (1 - cos_theta) + ux * sin_theta,
         cos_theta + uz ** 2 * (1 - cos_theta)]
    ])

    # Apply the rotation
    b_rotated = np.dot(rotation_matrix, b_relative)

    # Translate back
    new_b = b_rotated + a

    return new_b


for moving_bone in relevant_parts_dict.keys():
    csv_file_path = moving_bone + ".csv"

    with open(csv_file_path, mode='w', newline='') as file:
        # Create a CSV writer
        csv_writer = csv.writer(file)
        file.write(header)
        ORIG = parts_dict[moving_bone][3:]
        Origin = parents_dict[moving_bone][3:].copy()
        axis = (0, 0, 1)  # Rotate around the Z-axis

        for i in range(300):
            row = []
            # move some joint
            #print(parts_dict[moving_bone][3:])
            #print(rotate_point_3d(Origin, ORIG, i, axis))
            print(Origin)
            parts_dict[moving_bone][3:] = rotate_point_3d(Origin, ORIG, i/100, axis)


            # write to csv
            # sample = str(i) + ".0000000000e+00"
            row.append(i)
            row.append(0)
            for _, part in parts_dict.items():
                for value in part:
                    row.append(value)
            csv_writer.writerow(row)
        # reset bone
        parts_dict[moving_bone][3:] = ORIG


