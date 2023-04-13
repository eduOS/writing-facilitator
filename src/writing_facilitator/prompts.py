import csv
from .settings import prompt_path

prompt_settings = {}

default_prompt_info = {
        "ai_role": "Assistant",
        "system_prompt": "You are a helpful assistant.",
        "greetings": "[bold green]I am your helpful assistant.[/]",
        "command": "chat",
        "user_role": "User"
        }

def extract_prompts():
    global prompt_settings

    with open(prompt_path, newline='') as csv_file:
        prompt_settings = {d['ai_role']: d for d in csv.DictReader(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)}


extract_prompts()


def get_prompt_info(ai_role):
    return prompt_settings.get(ai_role.strip(), default_prompt_info)


def filter_roles(condition):
    condition = condition.lower().strip()
    return [r for r in prompt_settings.keys() if condition in r.lower()]
