# create a function of year and province that does all the job
import os
import csv

def get_params(file, delimiter=';', numerical_key = False):
    """
    Creates dictionary from csv file with 3 columns (name, value, type)
    """
    d_params = {}
    with open(file) as params:
        rows = csv.reader(params,delimiter=delimiter)
        next(rows)
        for row in rows:
            var, value, var_type = row[:3]
            if var_type == 'int':
                d_params[var] = int(value)
            elif var_type == 'float':
                d_params[var] = float(value)
            elif var_type == 'bool':
                d_params[var] = bool(int(value))
            else:
                d_params[var] = value
    if numerical_key:
        d_params = {int(k): v for k, v in d_params.items()}
    return d_params

def get_schedule(file, delimiter=';'):
    d_schedule = {}
    with open(file) as params:
        rows = csv.reader(params, delimiter=delimiter)
        for row in rows:
            var, value = row[0], row[1:]
            value = [float(v) for v in value]
            d_schedule[var] = value
    return d_schedule

def add_schedule_as_attr(inst, path, delimiter=';'):
    d_schedule = get_schedule(path,delimiter=delimiter)
    inst.__dict__.update(d_schedule)

def add_params_as_attr(inst, path,delimiter=';'):
    d_params = get_params(path,delimiter)
    inst.__dict__.update(d_params)