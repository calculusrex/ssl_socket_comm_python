import json
import functools as ft
import numpy as np


def dict_from_np_array(arr):
    return {
        'type': 'numpy_array',
        'dtype': arr.dtype.name,
        'nested_list': arr.tolist(),
    }

def np_array_from_dict(data):
    return np.array(
        data['nested_list'],
        dtype=np.dtype(data['dtype']))

def is_leaf(data):
    return ft.reduce(
        lambda a, b: a or b,
        map(lambda typ: type(data) == typ,
            [str, int, float, type(None), bool]),
        False)

def is_array(data):
    return type(data) == np.ndarray

def is_list(data):
    return type(data) == list

def is_dict(data):
    return type(data) == dict

def is_serial_repr(data):
    return ft.reduce(
        lambda a, b: a and b,
        [
            type(data) == dict,
            'type' in data.keys(),
        ],
        True)

def is_serialized_array(data):
    if is_serial_repr(data):
        if data['type'] == 'numpy_array':
            return True
    return False

def serializable_structure_from(data):
    if is_leaf(data):
        return data
    elif is_array(data):
        return dict_from_np_array(data)
    elif is_list(data):
        return list(
            map(serializable_structure_from,
                data))
    elif is_dict(data):
        out = {}
        for key in data.keys():
            out[key] = serializable_structure_from(
                data[key])
        return out
    else:
        raise Exception(
            "\n".join([
                f'-- CALCULUSREX --',
                f'Data type unaccounted for: {type(data)}',
                f'{data}'
            ]))

def nonserializable_structure_from(data):
    if is_leaf(data):
        return data
    elif is_list(data):
        return list(
            map(nonserializable_structure_from,
                data))
    elif is_serialized_array(data):
        return np_array_from_dict(data)
    elif is_dict(data):
        out = {}
        for key in data.keys():
            out[key] = nonserializable_structure_from(
                data[key])
        return out
    else:
        raise Exception(
            "\n".join([
                f'-- CALCULUSREX --',
                f'Data type unaccounted for: {type(data)}',
                f'{data}'
            ]))


def json_dumps(data_structure):
    return json.dumps(
        serializable_structure_from(
            data_structure))

def json_loads(data_string):
    return nonserializable_structure_from(
        json.loads(
            data_string))
