#!/usr/bin/env python
"""
author: Simon Dobers
contributors: Julian Balletshofer
"""
from scipy.signal import butter, sosfiltfilt, sosfilt
import pandas as pd
import sys


def postprocess(fileCSV, newFile, postprocess_config, verbose=False):
    """
    Applies interpolation to the CSV file of the recorded motion.
    Args:
        fileCSV: The CSV file to interpolate
        newFile: The name of the output file
        postprocess_config : configuration for postprocessing defined in config.yaml,
        see default values below to check which values must be provided
    """
    if postprocess_config is None:
        # if no config is provided, use default postprocessing config

        postprocess_config = {
            "fps": 100,
            'interpolation_type': 'polynomial',
            'polynomial_degree': 2,
            'median_filter': True,
            'median_window': 10,
            'lowpass_filter': True,
            'lowpass_critical_frequency': 2,
            'order_lowpass_filter': 4,
            'use_bidirectional_filter': True
        }

    try:
        df = pd.read_csv(fileCSV, sep=",", skiprows=5, header=None)

        if postprocess_config["interpolation_type"] == "polynomial":
            order = int(postprocess_config["polynomial_degree"])
            df = df.interpolate(limit=30, method="polynomial", order=order, axis=0)
        else:
            df = df.interpolate(limit=30, method="linear", axis=0)

        if postprocess_config["median_filter"]:
            median_window = int(postprocess_config["median_window"])
            for column in df:
                if column > 1:
                    df[column] = df[column].rolling(median_window, min_periods=1).median()

        if postprocess_config["lowpass_filter"]:
            df = df.dropna()
            signal_frequency = postprocess_config["fps"]
            order_lowpass_filter = int(postprocess_config["order_lowpass_filter"])
            lowpass_critical_frequency = float(postprocess_config["lowpass_critical_frequency"])
            sos = butter(
                order_lowpass_filter,
                lowpass_critical_frequency,
                fs=signal_frequency,
                output='sos'
            )

            for column in df:
                if column > 1:

                    if postprocess_config["use_bidirectional_filter"]:
                        df[column] = sosfiltfilt(sos, df[column])
                    else:
                        df[column] = sosfilt(sos, df[column])

        with open(fileCSV, "r") as f1, open(newFile, "w") as f2:
            for _ in range(5):
                l = f1.readline()
                f2.write(l)
        df.to_csv(newFile, mode="a", header=False, index=False)
        if verbose:
            print("Postprocessed file written to: " + newFile)

    except Exception as e:
        print("invalid postprocessing config provided: ", e)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python postprocess_data.py <file.csv>")
        sys.exit(1)
    fileCSV = sys.argv[1]
