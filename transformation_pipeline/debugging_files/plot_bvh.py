import pandas as pd
import matplotlib.pyplot as plt

file = "/home/manuel/HIWI/human-robot-animations/Lara_L_elbow/L_elbow.bvh"
file = "/home/manuel/HIWI/LARA/small/small.bvh"
# file = "/home/manuel/HIWI/human-robot-animations/CollaborativeLifting/1.bvh"


# correct ?
# joints = ["root", "hip", "torso", "neck", "neck_end", "left_collar", "left_upper_arm", "left_forearm", "left_forearm_end", "right_collar", "right_upper_arm", "right_forearm", "right_forearm_end"]
# order = ["Rx", "Ry", "Rz", "Tx", "Ty", "Tz"]
# column_names = [joints[i//3] + order[i % 3] for i in range(len(joints) * 3)]
# a = pd.read_csv(file, delimiter=" ", header=None, names=column_names, skiprows=100)

'''
A bvh first contains a Hierarchy Section, describing the skeleton and then a Motion Section.
We want to skip the Hierarchy Section using skiprows

MANUALLY ADJUST THE SKIPROWS PARAMETER!  


'''

a = pd.read_csv(file, delimiter=" ", header=None, skiprows=114,  usecols=[i for i in range(63) if i >2])

print(a)
plt.plot(a)
plt.plot()
plt.show()