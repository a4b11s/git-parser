import yaml
import os
import unittest
import tempfile
from util import is_int


class Config:
    def __init__(self, yml_path = ''):
        self.yml_path = yml_path
        
        self.config_fields = [
            "MIN_COMMIT_COUNT",
            "MIN_COMMIT_MESSAGE_LENGTH",
            "CLONE_TIMEOUT",
            "MAX_WORKERS",
            "DIRTY_DATA_PATH",
            "GITS_PATH",
            "URLS_PATH",
            "CLEANED_AND_MERGED_FILE_PATH",
            "MAX_COMMIT_MESSAGE_LENGTH",
            "MAX_DIFF_LENGTH"
        ]
        
        
        self.default_config = {
            'MIN_COMMIT_COUNT': 100,
            'MIN_COMMIT_MESSAGE_LENGTH': 10,
            'CLONE_TIMEOUT': 30,
            'MAX_WORKERS': 100,
            'DIRTY_DATA_PATH': 'output/',
            'GITS_PATH': 'git/',
            'URLS_PATH': 'url/',
            'CLEANED_AND_MERGED_FILE_PATH': 'cleaned_output.csv',
            "MAX_COMMIT_MESSAGE_LENGTH": 1000,
            "MAX_DIFF_LENGTH": 100000
        }
        
        self.load_from_yml()
        self.load_default_values()
        self.load_from_env()
        
        self.to_int()
        
        
    def load_from_yml(self):
        if not os.path.exists(self.yml_path):
            return
        
        with open(self.yml_path, mode="r") as config_file:
            yaml_data = yaml.load(config_file.read(), Loader=yaml.FullLoader)
            
            for key, value in yaml_data.items():
                if key in self.config_fields:
                    setattr(self, key, value)
    
    def load_default_values(self):        
        for key, value in self.default_config.items():
            if not hasattr(self, key) and key in self.config_fields:
                setattr(self, key, value)
                
    def load_from_env(self):
        for key, value in os.environ.items():
            if not hasattr(self, key) and key in self.config_fields:
                setattr(self, key, value)
                
    def to_int(self):
        for field in self.config_fields:
            if is_int(getattr(self, field)):
                setattr(self, field, int(getattr(self, field)))
                
                
class TestConfig(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        temp_file = tempfile.NamedTemporaryFile(mode="w")
        
        test_config_file_data = [{filed: 'test'} for filed in self.config.config_fields]
        temp_file.write(yaml.dump(test_config_file_data))
        
        
        self.config_path = temp_file.name
        self.config_with_file = Config(self.config_path)

    def test_yaml_values(self):        
        with open(self.config_path, "r") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for field, value in data.items():
                self.assertEqual(getattr(self.config_with_file, field), value)

    def test_default_values(self):
        for field in self.config.config_fields:
            self.assertEqual(
                getattr(self.config, field),
                self.config.default_config[field]
            )

    def test_env_values(self):
        for field in self.config.config_fields:
            os.environ[field] = str(self.config.default_config[field])
            
        for field in self.config.config_fields:
            self.assertEqual(
                getattr(self.config, field), os.environ.get(field)
            )

if __name__ == '__main__':
    unittest.main()