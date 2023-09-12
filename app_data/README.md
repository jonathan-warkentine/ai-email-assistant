# PERSISTENT JSON DATA STORE


Primitive db solution for persistently storing non-critical client synchronization data. Allows for this python app to be killed or restarted without having to re-synchronize the Gmail client, eg.

The custom `data_util.py` tool here handles initialization, reading, and writing to the respective `.json` files.