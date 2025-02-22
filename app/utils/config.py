import yaml

class Config:
    """
    Handles configuration loading and parsing.
    """
    def __init__(self, config_file=None):
        self.config_data = {}
        if config_file:
            self.load(config_file)

    def load(self, config_file):
        with open(config_file, 'r') as file:
            self.config_data = yaml.safe_load(file)

    def get(self, key, default=None):
        return self.config_data.get(key, default)
