#!/usr/bin/env python
"""
author: Erick Álvarez
contributors: Julian Balletshofer
"""
import numpy as np
from scipy.spatial.transform import Rotation


def calc_rotation_between(dir_vec_from, dir_vec_to):
    """
    Calculates the Rotation (object of scipy) between the unit vector 'dir_vec_from' and 'dir_vec_to'.
    The estimation considers that the Rotation transforms 'dir_vec_from' into 'dir_vec_to'
    Args:
        dir_vec_from (np.array): a unit vector
        dir_vec_to (np.array): a unit vector

    Returns:
        rot (Rotation of scipy)
    """
    assert np.abs(np.linalg.norm(dir_vec_from) - 1.0) < 1e-1, "the norm is {}".format(np.linalg.norm(dir_vec_from))
    assert np.abs(np.linalg.norm(dir_vec_to) - 1.0) < 1e-1, "the norm is {}".format(np.linalg.norm(dir_vec_to))
    if np.allclose(dir_vec_from, dir_vec_to):
        return Rotation.from_rotvec(np.array([0.0, 0.0, 0.0]))

    dot_prod = np.dot(dir_vec_from, dir_vec_to)
    rad_angle = np.arccos(dot_prod)
    degree_angle = np.degrees(rad_angle)

    cross_prod = np.cross(dir_vec_from, dir_vec_to)
    if cross_prod[0] == 0.0 and cross_prod[1] == 0.0 and cross_prod[2] == 0.0:
        if degree_angle == 0.0:
            # vectors pointing in same direction
            return Rotation.from_rotvec(np.array([0.0, 0.0, 0.0]))
        else:
            # vectors in opposite directions
            return Rotation.from_rotvec(np.array(rad_angle * np.array([1.0, 0.0, 0.0])))

    cross_prod_norm = cross_prod / np.linalg.norm(cross_prod)
    rot = Rotation.from_rotvec(rad_angle * cross_prod_norm)
    return rot


def _apply_transformation_to_pos(rot: Rotation, translation: np.ndarray, pos: np.ndarray):
    """
    Given a position vector estimates its' transformed position after a rotation and translation.
    Args:
        rot (Rotation): the rotation to apply
        translation (np.ndarray): the translation to apply
        pos (np.ndarray): the original position

    Returns:
        transformed_pos (np.ndarray)
    """
    rv = rot.apply(pos)
    transformed_pos = rv + translation
    return transformed_pos


def _inverse_transformation(rot: Rotation, translation: np.ndarray):
    """
    It estimated the inverse of a transformation, which itself consists of a rotation and a translation.
    Args:
        rot (Rotation): rotation
        translation (np.ndarray): translation

    Returns:
        rot_inv (Rotation): inverse rotation of transformation
        translation_inv (np.ndarray): inverse translation of transformation
    """
    rot_inv = rot.inv()
    translation_inv = (-1.) * rot_inv.apply(translation)
    return rot_inv, translation_inv


def _compose_transformations(first_rot: Rotation, first_translation: np.ndarray, second_rot: Rotation,
                             second_translation: np.ndarray):
    """
    Combines two transformations. Each one consists of a rotation and a translation. Estimation considers that
    'first_rot' and 'first_translation' are applied first
    Args:
        first_rot (Rotation):
        first_translation (np.ndarray):
        second_rot (Rotation):
        second_translation (np.ndarray):

    Returns:
        rot_compose (Rotation): combined transformation rotation
        translation_compose (np.ndarray): combined transformation translation
    """
    rot_compose = first_rot * second_rot
    translation_compose = first_rot.apply(second_translation) + first_translation
    return rot_compose, translation_compose


def estimate_rotation_between_joints(t_pose_dir_vecs, base_t_pose_rotation,
                                     current_frame, hierarchy, root_el):
    """
    Estimate the angle between joints that moves a skeleton from a resting position to some pose
    Args:
        t_pose_dir_vecs: dictionary with direction vectors between the joints in the joint hierarchy of the skeleton
        inter_joints_dists: dictionary with distance between the joints in the joint hierarchy of the skeleton
        base_t_pose_rotation: the orientation of the hip in the t_pose. In rotational axis representation
        current_frame (Frame_information): object containing information of a line of the parsed CSV.
                                           Here in particular the global positions of the joints is used.
        hierarchy: dictionary containing the hierarchy of the joints. The key is the parent joint and
                   the value is a list of all the children of this joint.
        root_el: The first joint of the hierarchy

    Returns:
        rotations: a dictionary containing the estimated rotation betwen two joints.
                   E.g.: {('collar, 'shoulder'):<Rotation_instance>}
    """

    rotations = {}

    first_parent_l = root_el
    first_parent_pos = current_frame.JOINT_VALUES[first_parent_l].global_pos

    r1 = Rotation.from_rotvec(current_frame.JOINT_VALUES[first_parent_l].global_angle)
    r0 = Rotation.from_rotvec(base_t_pose_rotation)
    r0_inv = r0.inv()
    rot_first_to_world = r1 * r0_inv

    rotations[('ROOT', root_el)] = rot_first_to_world

    transl_first_to_world = first_parent_pos
    rot_0_to_1, transl_0_to_1 = _inverse_transformation(rot_first_to_world, transl_first_to_world)

    def rec_estimation(parent_l, rot_0_to_parent: Rotation, transl_0_to_parent):
        for child_l in hierarchy[parent_l]:
            parent_child_key = (parent_l, child_l)

            # this term frame refers to frame of coordinate system
            # gives position of point in the coordinate system of the parent
            c_pos = current_frame.JOINT_VALUES[child_l].global_pos
            # make transformation to transform it into coord frame of parent joint instead of the vicon frame
            # f.e. elbow hand => hand pos relative to elbow
            p_frame_actual_child_pos = _apply_transformation_to_pos(rot_0_to_parent,
                                                                    transl_0_to_parent,
                                                                    c_pos)
            # unit vector to calculate the rotation between the 2 joints
            p_frame_actual_dir = p_frame_actual_child_pos / np.linalg.norm(p_frame_actual_child_pos)

            p_frame_should_dir = t_pose_dir_vecs[parent_child_key]

            rotation = calc_rotation_between(p_frame_should_dir, p_frame_actual_dir)

            rotations[(parent_l, child_l)] = rotation
            rot_child_to_parent = rotation

            translation_child_to_parent = p_frame_actual_child_pos
            rot_parent_to_child, transl_parent_to_child = _inverse_transformation(rot_child_to_parent,
                                                                                  translation_child_to_parent)
            rot_0_to_child, transl_0_to_child = _compose_transformations(rot_parent_to_child,
                                                                         transl_parent_to_child,
                                                                         rot_0_to_parent,
                                                                         transl_0_to_parent)

            rec_estimation(child_l, rot_0_to_child, transl_0_to_child)

    rec_estimation(first_parent_l, rot_0_to_1, transl_0_to_1)

    return rotations


def rotation_dict_to_angle_dict(rotation_dict):
    """
    Given the dictionary with Rotation between two joints, decompose the Rotation into the respective euler angles.
    It returns a dictionary with the same kez joints and the respective axis of rotation.
    E.g.:
    For an input: {('collar, 'shoulder'):<Rotation_instance>}
    It returns: {('collar', 'shoulder', 'z'): <rotation_angle_in_z_axis>,
                 ('collar', 'shoulder', 'x'): <rotation_angle_in_x_axis>,
                 ('collar', 'shoulder', 'y'): <rotation_angle_in_y_axis>}
    Args:
        rotation_dict: a dictionary with the Rotation for the joints

    Returns:
        angles_dict
    """
    angles_dict = {}
    for k, rot in rotation_dict.items():
        euler_angles_zxy = rot.as_euler('zxy', degrees=True)
        key_z = (k[0], k[1], 'z')
        key_x = (k[0], k[1], 'x')
        key_y = (k[0], k[1], 'y')
        angles_dict[key_z] = euler_angles_zxy[0]
        angles_dict[key_x] = euler_angles_zxy[1]
        angles_dict[key_y] = euler_angles_zxy[2]
    return angles_dict
