import os
import json

def load_example():
    """
    Loads example data for hospital_a.
    The default path is /examples/example_a.json, but you can override with EXAMPLE_PATH env var.
    """
    example_path = os.getenv("EXAMPLE_PATH", "/examples/example_a.json")
    if not os.path.exists(example_path):
        raise RuntimeError(f"Example file not found: {example_path}")

    with open(example_path, "r") as f:
        return json.load(f)