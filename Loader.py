import json

@staticmethod
def load_config(file_path: str) -> dict:
    """Loads a JSON file and return dictionary"""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Invalid JSON in file: {file_path}")
        return {}
@staticmethod
def get_model():
    """Returns model used"""
    config = load_config("config.json")
    return config.get("model")

@staticmethod
def get_temperature():
    """Returns temperature used"""
    config = load_config("config.json")
    return config.get("temperature")
