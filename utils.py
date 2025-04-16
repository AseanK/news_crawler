import platform
import json


def get_platform():
    os = platform.system()
    return (os == 'Linux' or os == 'Windows')


def convert_to_json(inp):
    if inp.startswith("```json"):
        inp = inp.strip("```json").strip().strip("```")

    try:
        json_data = json.loads(inp)
        return json_data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
