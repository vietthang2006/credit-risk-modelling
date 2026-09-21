from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_ROOT / "config" / "path.yaml"

class Config:
    def __init__(self, config_file: Path = CONFIG_PATH):
        self.project_root = PROJECT_ROOT

        if not config_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file config tại {config_file}")
        
        with open(config_file, "r", encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

        self.data_dir = self.project_root / self.data.get("data_dir", "Home Credit Dataset")
        self.raw_dir = self.data_dir / self.data["dirs"]["raw"]
        self.train_dir = self.data_dir / self.data["dirs"]["train"]
        self.test_dir = self.data_dir / self.data["dirs"]["test"]
        self.modelling_train_dir = self.data_dir / self.data["dirs"]["modelling_train"]
        self.modelling_test_dir = self.data_dir / self.data["dirs"]["modelling_test"]

        # Processed
        self.processed_train_dir = self.data_dir / self.data['dirs']['processed_train']
        self.processed_test_dir = self.data_dir / self.data['dirs']['processed_test']
        self.processed_valid_dir = self.data_dir / self.data['dirs']['processed_valid']

        self._files = self.data.get("files", {})

    # Processed data
    def get_processed_train(self, file_key: str) -> Path:
        filename = self._files.get(file_key, f"{file_key}.csv")
        return self.processed_train_dir / filename
    
    def get_processed_valid(self, file_key: str) -> Path:
        filename = self._files.get(file_key, f"{file_key}.csv")
        return self.processed_valid_dir / filename

    def get_processed_test(self, file_key: str) -> Path:
            filename = self._files.get(file_key, f"{file_key}.csv")
            return self.processed_test_dir / filename
    

    def get_raw(self, file_key: str) -> Path:
        filename = self._files.get(file_key, f"{file_key}.csv")
        return self.raw_dir / filename

    def get_train(self, file_key: str) -> Path:
        if file_key == "columns_description": 
            pass
        filename = self._files.get(file_key, f"{file_key}.csv")
        return self.train_dir / filename 

    def get_test(self, file_key: str) -> Path:
        if file_key == "columns_description": 
            pass
        filename = self._files.get(file_key, f"{file_key}.csv")
        return self.test_dir / filename

    def get_modelling_train(self, file_key: str) -> Path:
        filename = self._files.get(file_key, f"{file_key}.csv")
        return self.modelling_train_dir / filename

    def get_modelling_valid(self, file_key: str) -> Path:
        filename = self._files.get(file_key, f"{file_key}.csv")
        return self.modelling_test_dir / filename
    
cfg = Config()