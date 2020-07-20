# create a function of year and province that does all the job
import csv


def get_params(file, delimiter=';', numerical_key=False):
    """
    Crée un dictionnaire contenant les noms des variables et leur valeur
    à partir d'un fichier csv.

    Parameters
    ----------
    file: _io.TextIOWrapper
        fichier csv de paramètres
    delimiter: str
        séparateur dans le fichier csv
    numerical_key: boolean
        True si les clés du dictionnaire sont des nombres entiers.

    Returns
    -------
    dict:
        un dictionnaire de paramètres.
    """
    d_params = {}
    with open(file) as params:
        rows = csv.reader(params, delimiter=delimiter)
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
    """
    Crée un dictionnaire contenant les noms des variables et leur valeur
    à partir d'un fichier csv.

    Parameters
    ----------
    file: str
        adresse du fichier csv
    delimiter: str
        séparateur dans le fichier csv

    Returns
    -------
    dict:
        un dictionnaire de listes de paramètres.
    """

    d_schedule = {}
    with open(file) as params:
        rows = csv.reader(params, delimiter=delimiter)
        for row in rows:
            var, value = row[0], row[1:]
            value = [float(v) for v in value]
            d_schedule[var] = value
    return d_schedule

def add_schedule_as_attr(inst, path, delimiter=';'):
    """
    Ajoute des listes à l'instance de classe à partir d'un fichier csv.

    Parameters
    ----------
    inst: object
        instance de classe
    path: str
        addresse du fichier csv
    delimiter: str
        séparateur dans le fichier csv
    """
    d_schedule = get_schedule(path, delimiter=delimiter)
    inst.__dict__.update(d_schedule)

def add_params_as_attr(inst, path, delimiter=';'):
    """
    Ajoute des paramètres à l'instance de classe à partir d'un fichier csv.

    Parameters
    ----------
    inst: object
        instance de classe
    path: str
        addresse du fichier csv
    delimiter: str
        séparateur dans le fichier csv
    """
    d_params = get_params(path, delimiter)
    inst.__dict__.update(d_params)
