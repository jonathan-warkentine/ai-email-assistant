import yaml

def config_loader(filename='config.yaml'):
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data