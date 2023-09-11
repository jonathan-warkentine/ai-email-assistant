import yaml
import os

def curry_config_parser(filename='config/config.yaml'):
    """
    Initializes a curried YAML parser for the given filename.
    
    The function reads the content of the YAML file and returns a curried function
    to parse the content step by step, using prefixes/keys.
    
    :param filename: Name of the YAML file to be parsed.
    :type filename: str
    :return: A curried function to parse the YAML content or None if an error occurs.
    :rtype: function, None

    Usage:
    ------
    parser = curry_config_parser('config.yaml')
    
    # If you expect 'root' to lead to another nested structure:
    nested = parser('root')

    # If 'nested' leads to a value, then calling it will retrieve the value:
    value = nested('key1')
    """

    try:
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"\nERROR: File {os.getcwd()}/{filename} not found. Make sure {filename}'s extension matches (.yaml/.yml) the config file.\n")
        return None

    def parse_prefix(yaml_prefix):
        """
        Parses the current YAML content using the provided prefix/key.
        
        If the prefix leads to another nested structure, the function returns itself,
        allowing for further parsing. If the prefix leads to a value, it returns the value.
        
        :param yaml_prefix: The prefix or key to access the next level or value in the YAML content.
        :type yaml_prefix: str
        :return: The next level in the YAML content, the final value, or None if an error occurs.
        :rtype: dict, str, int, float, list, None
        """
        
        nonlocal data

        if yaml_prefix not in data:
            print(f"\nERROR: Prefix {yaml_prefix} not found in {filename}.\n")
            return None

        data = data[yaml_prefix]

        if isinstance(data, dict):
            return parse_prefix
        else:
            return data

    return parse_prefix
