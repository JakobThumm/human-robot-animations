#!/usr/bin/env python
"""
author: Marc Gavilán Gil
contributors:Julian Balletshofer, Simon Dobers
"""


def renameCSVelements(csvFile, renameDictionary):
    new_file_content = ""
    with open(csvFile, 'r') as csvfile:
        for i, line in enumerate(csvfile):
            if i == 2:
                line_elems = line.split(",")
                renamed_line_elems = []
                for elem in line_elems:
                    renamed_elem = elem
                    for key, value in renameDictionary.items():
                        renamed_elem = renamed_elem.replace(key, value)
                    renamed_line_elems.append(renamed_elem)
                renamed_line = ",".join(renamed_line_elems)
                new_file_content += renamed_line
            else:
                new_file_content += line
    with open(csvFile, 'w') as csvfile:
        csvfile.write(new_file_content)


# rename dic adjusted for our current names in the csv files
renameDictionary = {
        "Collar": "collar",
        "Head": "head",
        "LElbow": "left_elbow",
        "LHand": "left_hand",
        "LShoulder": "left_shoulder",
        "RElbow": "right_elbow",
        "RHand": "right_hand",
        "RShoulder": "right_shoulder",
        "Torso": "hip",
        "knee_left_2910": "collar",
        "knee_l_2911": "collar"
    }

if __name__ == '__main__':

    """Obtain the arguments from the command line"""
    import argparse
    parser = argparse.ArgumentParser(description='Rename the elements in a csv file')
    parser.add_argument('csvFile', help='The csv file to be renamed')
    renameCSVelements(parser.parse_args().csvFile, renameDictionary)
