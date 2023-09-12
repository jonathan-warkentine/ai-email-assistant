import yaml
import os
from functools import partial

from utils import deep_merge_dicts


def curry_config_parser(config_filepath='config/config.yaml', credentials_filepath='config/credentials.yaml'):
    """
    Initializes a curried YAML parser for the given filepath.
    
    The function reads the content of the YAML file and returns a curried function
    to parse the content step by step, using prefixes/keys.
    
    :param filepath: Name of the YAML file to be parsed.
    :type filepath: str
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
    config_file_data = _load_yaml(config_filepath)
    credentials_file_data = _load_yaml(credentials_filepath)
    master_config_data = deep_merge_dicts(config_file_data, credentials_file_data)

    def parse_prefix(yaml_prefix, data=master_config_data, return_dicts=False):
        """
        Parses the current YAML content using the provided prefix/key.
        
        If the prefix leads to another nested structure, the function returns itself,
        allowing for further parsing. If the prefix leads to a value, it returns the value.
        
        :param yaml_prefix: The prefix or key to access the next level or value in the YAML content.
        :type yaml_prefix: str
        :return: The next level in the YAML content, the final value, or None if an error occurs.
        :rtype: dict, str, int, float, list, None
        """
        if yaml_prefix not in data.keys():
            print(f"\nERROR: Prefix {yaml_prefix} not found in config or credential files.\n")
            return None

        result = data[yaml_prefix]

        if isinstance(result, dict) and not return_dicts:
            return partial(parse_prefix, data=result)
        else:
            return result

    
    return parse_prefix

def _load_yaml(filepath):
    try:
        with open(filepath, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"\nERROR: File {os.getcwd()}/{filepath} not found. Make sure {filepath}'s extension matches (.yaml/.yml) the config file.\n")
        return None