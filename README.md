# Human-Robot-Animations

This repository contains a library of human motion capture data recorded with a Vicon tracker system.

Furthermore, it provides a processing pipeline for transforming the recorded data from `.csv` files to `.bvh` and further to `.pkl` files that can be used in mujoco simulations.

## Clone this repo
```
git@github.com:JakobThumm/human-robot-animations.git
```

## Installation
We work on Ubuntu 20.04. If you want to participate, you need to run this version

1. Install anaconda 
2. Create an environment 
    ```
    conda create -n human-motion python==3.8
    ```
3. Activate the environment
    ```
    conda activate human-motion 
    ```
4. Move to the `transformation_pipeline` subdirectory as it contains the transformation pipeline script
    ```
    cd transformation_pipeline/
    ```
5. Install the requirements
    ```
    pip install -r requirements.txt 
    ```
6. Run the pipeline to convert the collected csv data to a mujoco usable format
    ```
    python transformationPipeline.py --directory motion_capture/dataset/motions/{name of the folder} 
    ```
    use the following arguments:

    `--postprocess` (apply postprocessing)

    `--toBVH` (convert CSV to BVH)

    `--toMujoco` (convert BVH to mujoco usable format)

The pipeline creates an extra folder called **mujoco** for the mujoco usable files (.pkl)

Please make sure you have a file `tPose*.csv` present in the folder containing the other `.csv` files you would like to convert. It should contain data of a human performing a t-Pose. We use only the first frame of this file in the transformation pipeline. Make sure all markers are visible in that frame!


## Lara
Download the [LaRA V3](https://zenodo.org/records/8189341) dataset.

Use the following command:
```
cd transformation_pipeline
pip install -r requirements.txt
MOT_TRANS_CONF_FILE=motion_capture/Lara_config.yaml python transformationPipeline.py --directory <PATH_OF_LARA_DIR> --toBVH --sameFileAsTpose --multithreaded
```

Explanation:
- Set the config file with `MOT_TRANS_CONF_FILE=motion_capture/Lara_config.yaml`, otherwiese `motion_capture/config.yaml` will be used
- `--directory <PATH_OF_LARA_DIR>` set the directory that stores the Lara CSV's
- `--sameFileAsTpose` use the first frame as Tpose. Important since Lara does not have seperate T-pose files
- `--multithreaded` Spawn multiple processes to convert the files in parallel.