# renameCSVitems.py
After finishing some recordings we noticed that we had some mistakes in the marker's names in the Vicon Tracker program. For this reason, the names were also incorrect in the columns of the exported CSV file. We wrote this script to correct those msitakes. With this script we can replace specific strings in the name.
This is not part of the transformation pipeline, but we leave the script for the case that someone makes the same mistake.

# postprocess_data.py
This script implements postprocessing as defined in the postprocessing section of `config.yaml` with the following steps:
### interpolation 
Interpolation of the data using either polynomial or linear interpolation as defined in `interpolation_type`. If `interpolation_type` is polynomial, `polynomial_degree` defines 
the order of the polynomial function used for interpolation. If type is linear, `polynomial_degree` entry is ignored.

### median filtering
Rolling median filtering to remove "outlier spikes". `median_window` defines the number of signal points used to compute the mean.

### lowpass filtering
Implements a butterworth lowpass filter (see [documentation](https://docs.scipy.org/doc/scipy/reference/signal.html)) to remove high frequency noise from the recordings. The following parameters must be specified:

|parameter|meaning|
|-----|-----|
|`lowpass_filter`|Whether to apply lowpass filtering or not|
|`lowpass_critical_frequency`|Choose the critical frequency of the filter (frequencies greater than this value will be damped, see [detailed explanation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html#scipy.signal.butter), default is 2|
|`order_lowpass_filter`|System order of the lowpass filter. 4 seemed to be the best working value.|
|`use_bidirectional_filter`|Whether to apply forward-backward filtering or simply forward-filtering (forward-backward is recommended). See [example](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html#scipy.signal.sosfiltfilt) for more details.|




# angle_estimation.py
This is the script that we use to estimate the angles of the BVH file when converting from the CSV file to BVH. Here are some important information that helped us to understand basic concepts:
+ skeletal animation and the usage of animation matrices: [video](https://www.youtube.com/watch?v=f3Cr8Yx3GGA).
+ inverse kinematics - [geometrical solution](https://robotacademy.net.au/lesson/inverse-kinematics-for-a-2-joint-robot-arm-using-geometry/).
+ [estimating angle](https://www.omnicalculator.com/math/angle-between-two-vectors) between two vectors.

A row of the CSV file contains the absolute positions of the joints for an specific pose. In order to express this pose in BVH format, we must find the angles that move the joints to these global positions. We solve this with inverse kinematics. To be more specific, we iterate over pairs of joints along the skeleton and with their positions we estimate the angle using the geometrical solution for inverse kinematics.
