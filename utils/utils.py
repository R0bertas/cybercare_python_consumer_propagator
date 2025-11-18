import json


def load_config(type: str ,config_path: str = "config.json") -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f).get(type, {})
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        print(f"Warning: invalid JSON in {config_path}: {e}")
        return {}
    

def load_consumer():
    return load_config( "consumer", "config.json")

 
def load_propagator():
    return load_config( "propagator", "config.json")

