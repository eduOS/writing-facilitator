import os
import time
import copy
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText, HTML
from rich import print as rprint

from .settings import is_testing
from .my_utils import openai_generate, InvalidInputError, get_ai_prompt_text, get_user_prompt_text, update_file_name
from .prompts import get_prompt_info

terminal_prompt_for_title = "Edit the file name to save: "

# histories format:
# {
#   1: {
#        "ai_role": 'some role',
#        "user_role": 'some role',
#        "history": [{"role": "", "content": "", "timestamp": ""}, {}, {}]
#      }
#   2: same format 
#   3: same format
# }

# saved file format:
# {
#   ai_role: '',
#   user_role: '',
#   history: []
# }

class Logger():
    def __init__(self, dir_name='./'):
        self.dir_name = dir_name
        self.histories = {}
        self.current_standard_history = []
        self.init_roles = self.update_roles
        self.prompt_info = {}

    def print_greetings_and_history(self):
        rprint(self.prompt_info['greetings'].replace('\\n', '\n'))

        session_no = self.current_history_index
        turn_no = 1
        for turn in self.current_standard_history:
            if turn['role'] == "assistant":
                rprint(get_ai_prompt_text(self.prompt_info['ai_role'], turn['content']))
            if turn['role'] == "user":
                index = f"{session_no}.{turn_no}"
                turn_no += 1
                rprint("[bold red]" + get_user_prompt_text(index, self.prompt_info['user_role']) + "[/]" + turn['content'])

    def get_coming_user_prompt_index(self):
        session_no = self.current_history_index
        turn_no = len([t for t in self.current_standard_history if t['role']=='user']) + 1
        return str(session_no) + "." + str(turn_no)

    def update_current_standard_history_by_index(self, session_no, turn_no):
        prompt_info = get_prompt_info(self.histories[session_no]['ai_role'])

        if turn_no:
            self.current_standard_history = []
            user_turn = 0
            user_prompt_to_edit = ''
            for turn in self.histories[session_no]['history']:
                if turn['role'] == 'user':
                    user_turn += 1
                    if user_turn == turn_no:
                        user_prompt_to_edit = turn['content']
                        break
                self.current_standard_history.append({"role": turn['role'], "content": turn['content']})
            prompt_info = get_prompt_info(self.histories[session_no]['ai_role'])
            return user_prompt_to_edit, prompt_info
        else:
            self.current_standard_history = [{
                "role": 'system',
                "content": prompt_info['system_prompt'],
                }]
            return "", prompt_info

    def update_roles(self, index=None, prompt_info=None, file_name='', save=True):
        user_prompt_to_edit = ""

        if save:
            self.save(file_name)

        if index != None:
            session_no = None
            turn_no = None
            index = index.replace(' ', '').strip()
            try:
                session_no, turn_no = index.split('.')
                session_no = int(session_no)
                assert session_no > 0 and session_no <= self.current_history_index
                if turn_no != '':
                    turn_no = int(turn_no)
                    assert turn_no >= 0 and turn_no < len(self.histories[session_no]['history'])
            except AssertionError:
                raise InvalidInputError(f'first number should be: 0 < an_integer <= {self.current_history_index}; and the second should be: empty or 0 <= an_integer < {len(self.histories[session_no]["history"])}')
                return 
            user_prompt_to_edit, prompt_info = self.update_current_standard_history_by_index(session_no, turn_no)
            self.prompt_info = prompt_info
        elif prompt_info != None:
            self.prompt_info = prompt_info
            self.current_standard_history = [{
                "role": 'system',
                "content": prompt_info['system_prompt'],
                }]
        else:
            raise InvalidInputError('index and role cannot cooccur')


        new_index = self.current_history_index+1
        self.histories[new_index] = {
                "ai_role": prompt_info['ai_role'],
                "user_role": prompt_info['user_role'],
                "history": copy.deepcopy(self.current_standard_history)
                }
        if index == None:
            self.histories[new_index]['history'][-1]['timestamp'] = time.time()

        self.print_greetings_and_history()
        return prompt_info, self.current_standard_history, user_prompt_to_edit.strip()

    @property
    def current_history_index(self):
        return len(self.histories)

    def get_file_name(self, generate=False):
        if not generate:
            return ''
        title_request = [{"role": "user", "content": get_prompt_info('File-naming Expert')['system_prompt']}]
        history = [d for d in self.current_standard_history[1:2] if d['role']=='user'] + title_request
        ai_file_name = openai_generate(history=history, test=is_testing, waiting_message="Generating filename...")

        prefix = terminal_prompt_for_title 
        default_text = ai_file_name or ''

        prompt_text = FormattedText([("class:prompt-prefix", prefix), ("", '')])
        file_name = prompt(message=prompt_text, placeholder='', default=default_text)
        return file_name.strip().replace(' ', '_')

    def save(self, file_name=''):
        if self.current_history_index == 0:
            return
        current_history_info = self.histories[self.current_history_index]
        if len(current_history_info['history']) < 2:
            return

        file_name = str(int(time.time())) + "_" + update_file_name(file_name or self.get_file_name())
        path = os.path.join(self.dir_name, file_name)
        with open(path, 'w') as f:
            rprint(current_history_info, file=f)
            rprint(f"[green]Chat log saved in {path}[/]")

    def update_history(self, standard_history):
        if (not isinstance(standard_history, list) or len(standard_history)<2):
            return

        last_record = copy.deepcopy(standard_history[-1])
        last_record['timestamp'] = time.time()
        self.histories[self.current_history_index]['history'].append(last_record)

        self.current_standard_history = copy.deepcopy(standard_history)
