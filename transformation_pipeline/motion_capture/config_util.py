#!/usr/bin/env python
"""
author: Erick Álvarez
contributors: Marc Gavilán Gil, Julian Balletshofer, Simon Dobers
"""
import yaml
import sys
import numpy as np
import os


class Configuration:
    """
    class with all the configurable values
    """
    def __init__(self, config_parser):
        self.joint_name_pattern_csv = config_parser['joint_name_pattern_csv']
        self.FPS = config_parser['FPS']
        self.JOINTS_HIERARCHY = config_parser['JOINTS_HIERARCHY']
        self.JOINTS_NAMES = list(self.JOINTS_HIERARCHY.keys())
        self.ROOT_JOINT = config_parser['ROOT_JOINT']

        self.BONE_HIERARCHY = config_parser['BONE_HIERARCHY']
        self.BONE_END_BVH_NAME = config_parser['BONE_END_BVH_NAME']
        self.BONE_NAMES = list(self.BONE_HIERARCHY.keys())
        self.ROOT_BONE = config_parser['ROOT_BONE']

        self.BONE_BEGIN_AT_JOINT = config_parser['BONE_BEGIN_AT_JOINT']
        self.BONE_END_AT_JOINT = config_parser['BONE_END_AT_JOINT']

        try : 
            self.postprocessing = config_parser['postprocessing']
        except KeyError:
            self.postprocessing = None


def read_configfile(filename):
    """
    helper function to read the configuration file
    """
    with open(filename, 'r') as f:
        try:
            config_parser = yaml.load(f, Loader=yaml.Loader)
            config = Configuration(config_parser)
            return config

        except yaml.YAMLError as exc:
            print(exc)
            sys.exit(1)


conf_filename = os.getenv('MOT_TRANS_CONF_FILE')
if conf_filename is None:
    #sets default
    conf_filename = os.path.dirname(os.path.realpath(__file__)) + "/config.yaml"
CONFIG_YAML = read_configfile(conf_filename)
