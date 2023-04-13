import os, sys, argparse
from rich import print as rprint
from rich.text import Text
from rich.console import Console
from .settings import is_testing, native_language, start_cmd, startfrom_cmd, startas_cmd, roles_cmd, restart_cmd, exit_cmd, edit_cmd

from .my_utils import openai_generate, get_user_input, InvalidInputError, get_ai_prompt_text
from .prompts import get_prompt_info, default_prompt_info, filter_roles
from .logger import Logger
from .settings import log_dir


# global variables
command = sys.argv[0].split('/')[-1]
console = Console()
logger = Logger(log_dir)
history = []
prompt_info = default_prompt_info
user_prompt_to_edit = ''
next_file_name = ''
lasted_printed_roles = []

def update_prompt_info(role):
    global prompt_info
    prompt_info = get_prompt_info(role)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("language", type=str, nargs="?", default=None, help="language")
    return parser.parse_args()

def get_history_from_terminal():
    args = parse_args()
    language = args.language
    global history

    if (language == None and command == 'facilitator'):
        update_prompt_info('Writing Facilitator')
    elif (language != None and language.lower() == 'german'):
        update_prompt_info('German Language Facilitator')
    else: 
        update_prompt_info('Assistant')
    _, history, _ = logger.init_roles(None, prompt_info)

def print_ai_roles(condition):
    global lasted_printed_roles
    roles = filter_roles(condition)
    rprint([str(i) + ". " + r for i, r in enumerate(roles)])
    lasted_printed_roles = roles

def process_cmds(q):
    # /start
    # /startfrom
    # /startas
    # /roles: with filter string
    global history
    global prompt_info
    global user_prompt_to_edit
    global next_file_name
    user_prompt_to_edit = ''
    cmd = ''

    q = q.strip()
    if q.startswith(startfrom_cmd):
        index = q[len(startfrom_cmd):]
        prompt_info, history, user_prompt_to_edit = logger.update_roles(index, None, file_name=next_file_name)
        next_file_name = ''
    elif q.startswith(edit_cmd):
        index = q[len(edit_cmd):]
        prompt_info, history, user_prompt_to_edit = logger.update_roles(index, None, file_name=next_file_name, save=False)
        next_file_name = ''
    elif q.startswith(restart_cmd):
        _, history, _ = logger.update_roles(None, prompt_info, file_name=next_file_name)
        file_name = q[len(restart_cmd):]
        if file_name: 
            next_file_name = file_name
    elif q.startswith(exit_cmd):
        file_name = q[len(exit_cmd):].strip()
        if not file_name: 
            file_name = next_file_name
        logger.save(file_name)
        exit(1)
    elif q.startswith(start_cmd):
        update_prompt_info('Assistant')
        _, history, _ = logger.update_roles(None, prompt_info, file_name=next_file_name)
        next_file_name = q[len(start_cmd):]
    elif q.startswith(startas_cmd):
        role = q[len(startas_cmd):].strip()
        if role.isdigit():
            role = lasted_printed_roles[int(role)]
        update_prompt_info(role)
        _, history, _ = logger.update_roles(None, prompt_info, file_name=next_file_name)
        next_file_name = ''
    elif q.startswith(roles_cmd):
        print_ai_roles(q[len(roles_cmd):])
    else:
        return


def main():
    global user_prompt_to_edit
    get_history_from_terminal()
    while (q := get_user_input(user_role=prompt_info['user_role'], default=user_prompt_to_edit, index=logger.get_coming_user_prompt_index())) not in ['q', 'exit', 'quit', 'exit()']:
        if len(q) == 0:
            continue
        user_prompt_to_edit = ''
        if q.startswith('/'):
            try:
                process_cmds(q)
            except Exception as e:
                rprint(f'[red]Invalide input error: {e}[/]')
            continue

        history.append({"role": "user", "content": q})
        logger.update_history(history)

        out = ''
        out = openai_generate(history=history, test=is_testing)
        if out == None:
            continue
        formated_out = Text(out, justify="right")
        console.print(get_ai_prompt_text(prompt_info['ai_role'], out))

        history.append({"role": "assistant", "content": out})
        logger.update_history(history)

    logger.save(next_file_name)
