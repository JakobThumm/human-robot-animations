#!/usr/bin/env python
"""
from last years group ajdusted
author: Julian Balletshofer
contributors: Simon Dobers
"""
from tqdm import tqdm
import os
from motion_capture.converters.viconCSV_to_bvh import main as CSV_to_BVH
from motion_capture.converters.viconCSV_to_point_animation import main as CSV_to_PointAnimation
from motion_capture.help_scripts.postprocess_data import postprocess
from motion_capture.help_scripts.renameCSVitems import renameCSVelements, renameDictionary
from motion_capture.converters.convert_bvh import convert_to_mujoco
from motion_capture.config_util import CONFIG_YAML


def convertToBVH(directory, verbose):
    # Search for tPose file in directory
    # ToDo: check if tPose is fine else warning
    tPose = None
    tPoseFilename = None
    for (_, _, filenames) in os.walk(directory):
        for filename in filenames:
            if filename.startswith("tPose") and filename.endswith(".csv"):
                tPose = os.path.join(directory, filename)
                tPoseFilename = filename
                break
        if tPose:
            break

    if verbose:
        iterable = tqdm(os.walk(directory), desc="Converting files to BVH")
    else:
        iterable = os.walk(directory)
    for (path_to_file, _, filenames) in iterable:
        for filename in filenames:
            if filename.endswith(".csv"):
                if verbose:
                    print("\n--------" + filename + "--------\n")
                if filename != tPoseFilename:
                    file_with_path = os.path.join(path_to_file, filename)
                    CSV_to_BVH(file_with_path, tPose, verbose)


def convertToPointAnimation(directory, verbose):
    if verbose:
        iterable = tqdm(os.walk(directory), desc="Converting files to BVH")
    else:
        iterable = os.walk(directory)
    # create sub directory for point animations
    point_animation_path = os.path.join(directory, "point_animations")
    if not os.path.exists(point_animation_path):
        os.mkdir(point_animation_path)
    for (path_to_file, _, filenames) in iterable:
        for filename in filenames:
            if filename.endswith(".csv"):
                if verbose:
                    print("\n--------" + filename + "--------\n")
                file_with_path = os.path.join(path_to_file, filename)
                CSV_to_PointAnimation(file_with_path, point_animation_path, verbose)


def postprocessCSV(directory, verbose):
    out_path = os.path.join(directory, "postprocessed")
    # get postprocessing config
    if CONFIG_YAML.postprocessing is not None:
        postprocessing_config = CONFIG_YAML.postprocessing
    else:
        print(
            "No postprocessing config found in config.yaml, using default config"
            "see postprocess_data.py for details."
        )
        postprocessing_config = None

    try:
        os.makedirs(out_path, exist_ok=True)
        if verbose:
            print("Directory '%s' created successfully" % out_path)

        if verbose:
            iterable = tqdm(os.listdir(directory), desc="Postprocessing BVH files")
        else:
            iterable = os.listdir(directory)
        for file in iterable:
            filename = os.fsdecode(file)
            if filename.endswith(".csv"):
                # first rename the measurements in the csv file to align with the config file
                renameCSVelements(os.path.join(directory, filename), renameDictionary)
                if not filename.startswith("tPose"):
                    postprocess(
                        os.path.join(directory, filename),
                        os.path.join(out_path, filename),
                        postprocessing_config,
                        verbose
                    )
    except OSError:
        print("Directory '%s' can not be created" % out_path)


def convertToMujoco(directory, verbose):
    assert os.path.exists(directory), "Directory does not exist!"

    if verbose:
        iterable = tqdm(os.walk(directory), desc="Converting files to mujoco usable format")
    else:
        iterable = os.walk(directory)
    for (path_to_file, _, filenames) in iterable:
        out_path = os.path.join(path_to_file, "mujoco")
        try:
            os.makedirs(out_path, exist_ok=True)
            if verbose:
                print("Directory '%s' created successfully" % out_path)
        except OSError:
            print("Directory '%s' can not be created" % out_path)

        for filename in filenames:
            if filename.endswith(".bvh"):
                if verbose:
                    print("\n--------" + filename.split('.', 1)[0] + "--------\n")
                file_with_path = os.path.join(path_to_file, filename)
                convert_to_mujoco(file_with_path, os.path.join(out_path, filename))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Data augmentation')
    parser.add_argument('--directory', type=str, help='Directory that contains the CSV vicon animations and the T-pose')
    parser.add_argument('--toBVH', action='store_true', help='Convert the CSV files into BVH files')
    parser.add_argument('--toMujoco', action='store_true', help='Convert the CSV files into Mujoco files')
    parser.add_argument('--toPointAnimation', action='store_true', help='Convert the CSV files into point movement files')
    parser.add_argument(
        '--postprocess',
        action='store_true',
        help='Postprocess missing values and smoothen with rolling median'
    )
    parser.add_argument('--verbose', action='store_true', help='Use this argument to print to the console.')
    args = parser.parse_args()

    if args.postprocess:
        print("\n-------- Postprocessing .csv files -------\n")
        postprocessCSV(args.directory, args.verbose)
        args.directory = os.path.join(args.directory, "postprocessed")

    if args.toBVH:
        convertToBVH(args.directory, args.verbose)

    if args.toMujoco:
        print("\n-------- Converting to .pkl (for Mujoco) -------\n")
        convertToMujoco(args.directory, args.verbose)

    if args.toPointAnimation:
        print("\n-------- Converting to .pkl (for Point Animation) -------\n")
        convertToPointAnimation(args.directory, args.verbose)

    print("Done.")
