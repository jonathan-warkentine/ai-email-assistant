from copy import deepcopy

def deep_merge_dicts(x, y):
    """
    Deeply merge two dictionaries.

    Recursively merges dictionary y into dictionary x so that x takes precedence 
    over y in case of a conflict. This is a deep merge, meaning that it will 
    handle nested dictionaries appropriately, rather than just overwriting 
    them.

    Parameters:
    - x (dict): The primary dictionary. This dictionary will take precedence 
                over y in case of overlapping keys.
    - y (dict): The secondary dictionary.

    Returns:
    - dict: A new dictionary that is the result of deeply merging x and y.

    Examples:
    --------
    >>> x = {'a': {'b': 'c', 'd': 'e'}}
    >>> y = {'a': {'b': 'f', 'g': 'h'}}
    >>> deep_merge_dicts(x, y)
    {'a': {'b': 'c', 'd': 'e', 'g': 'h'}}
    """
    
    z = {}
    overlapping_keys = x.keys() & y.keys()
    for key in overlapping_keys:
        z[key] = deep_merge_dicts(x[key], y[key])
    for key in x.keys() - overlapping_keys:
        z[key] = deepcopy(x[key])
    for key in y.keys() - overlapping_keys:
        z[key] = deepcopy(y[key])
    return z
