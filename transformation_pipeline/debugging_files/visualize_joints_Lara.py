import csv
import numpy as np
import matplotlib.pyplot as plt

file_path = 'L01_S01_R01_A17_N01_norm_data.csv'


def take(array, indexes):
    a = np.array([])
    for i in indexes:
        a = np.append(a, array[i])
    return a


ax = plt.figure().add_subplot(projection='3d')

np.set_printoptions(suppress=True)
x = np.array([])
y = np.array([])
z = np.array([])


with open(file_path, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)
    for i in range(10):
        next(reader)
    row1 = next(reader)
    for i in range(2, len(header), 6):
        xi = float(row1[i+3])
        yi = float(row1[i+4])
        zi = float(row1[i+5])
        x = np.append(x, xi)
        y = np.append(y, yi)
        z = np.append(z, zi)
        print(np.array(header[i:i+6]))
        print(np.array(row1[i:i+6], dtype=float))
        ax.text(xi, yi, zi, '%s' % (header[i]), size=20, zorder=1,  color='k')
        # plt.annotate(text=header[i], xy = (xi * (1 + 0.01), yi * (1 + 0.01)), fontsize=12)
        
ax.scatter(x, y, z, zdir='z', label='test (x, y, z)')
mainline = [1, 0, 11, 21]
l_arm = [2, 6, 3, 9, 10]
r_arm = [12, 16, 13, 19, 20]
l_leg = [21, 4, 7, 5, 8]
r_leg = [21, 14, 17, 15, 18]  
ax.plot(x.take(mainline), y.take(mainline), z.take(mainline), zdir='z', label='test (x, y, z)')
ax.plot(take(x,l_arm), take(y,l_arm), take(z,l_arm), zdir='z', label='test (x, y, z)')
ax.plot(take(x,r_arm), take(y,r_arm), take(z,r_arm), zdir='z', label='test (x, y, z)')
ax.plot(take(x,l_leg), take(y,l_leg), take(z,l_leg), zdir='z', label='test (x, y, z)')
ax.plot(take(x,r_leg), take(y,r_leg), take(z,r_leg), zdir='z', label='test (x, y, z)')
ax.set_xlim([-500,500])
ax.set_ylim([-500,500])
ax.set_zlim([-500,500])
plt.show()


"""
0: head_RX
1: head end_RX
2:L collar_RX
3: L elbow_RX	,L elbow_RY,L elbow_RZ,L elbow_TX,L elbow_TY,L elbow_TZ,
4: L femur_RX	,L femur_RY,L femur_RZ,L femur_TX,L femur_TY,L femur_TZ,
5: L foot_RX	,L foot_RY,L foot_RZ,L foot_TX,L foot_TY,L foot_TZ,
6: L humerus_RX		,L humerus_RY,L humerus_RZ,L humerus_TX,L humerus_TY,L humerus_TZ,
7: L tibia_RX		,L tibia_RY,L tibia_RZ,L tibia_TX,L tibia_TY,L tibia_TZ,
8: L toe_RX		,L toe_RY,L toe_RZ,L toe_TX,L toe_TY,L toe_TZ,
9: L wrist_RX		,L wrist_RY,L wrist_RZ,L wrist_TX,L wrist_TY,L wrist_TZ,
10: L wrist end_RX		,L wrist end_RY,L wrist end_RZ,L wrist end_TX,L wrist end_TY,L wrist end_TZ,
11: lower back_RX		,lower back_RY,lower back_RZ,lower back_TX,lower back_TY,lower back_TZ,
12: R collar_RX		,R collar_RY,R collar_RZ,R collar_TX,R collar_TY,R collar_TZ,
13: R elbow_RX		,R elbow_RY,R elbow_RZ,R elbow_TX,R elbow_TY,R elbow_TZ,
14: R femur_RX		,R femur_RY,R femur_RZ,R femur_TX,R femur_TY,R femur_TZ,
15: R foot_RX		,R foot_R	Y,R foot_RZ,R foot_TX,R foot_TY,R foot_TZ,
16: R humerus_RX	,R humerus_RY,R humerus_RZ,R humerus_TX,R humerus_TY,R humerus_TZ,
17: R tibia_RX		,R tibia_RY,R tibia_RZ,R tibia_TX,R tibia_TY,R tibia_TZ,
18: R toe_RX		,R toe_RY,R toe_RZ,R toe_TX,R toe_TY,R toe_TZ,
19: R wrist_RX		,R wrist_RY,R wrist_RZ,R wrist_TX,R wrist_TY,R wrist_TZ,
20: R wrist end_RX	,R wrist end_RY,R wrist end_RZ,R wrist end_TX,R wrist end_TY,R wrist end_TZ,
21: root_RX		,root_RY,root_RZ,root_TX,root_TY,root_TZ
"""

