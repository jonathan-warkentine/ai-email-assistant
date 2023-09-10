import json
import os

class Data_store:
    def __init__(self, json_store_filepath):
        self.json_store_filepath = json_store_filepath
        
        # Check if the file exists. If not, create it with an empty dictionary
        if not os.path.exists(json_store_filepath):
            with open(json_store_filepath, 'w') as f:
                json.dump({}, f)
        
        with open(json_store_filepath, 'r') as f:
            self.data = json.load(f)

    def write(self, key, value):
        self.data[key] = value
        with open(self.json_store_filepath, 'w') as f:
            json.dump(self.data, f)
        return value

    def read(self, key):
        return self.data.get(key, None)  # Returns None if the key doesn't exist
