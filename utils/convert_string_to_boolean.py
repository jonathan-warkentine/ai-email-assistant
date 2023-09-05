def convert_string_to_boolean(s):
    """
    Convert a string to its corresponding boolean value.

    Parameters:
    - s (str): Input string to be converted.

    Returns:
    - bool: True or False based on the input string.
    """
    true_values = ["true", "yes", "1", "t", "y"]
    false_values = ["false", "no", "0", "f", "n"]
    
    s = s.strip().lower()
    if s in true_values:
        return True
    elif s in false_values:
        return False
    else:
        raise ValueError(f"Cannot convert {s} to a boolean value.")
