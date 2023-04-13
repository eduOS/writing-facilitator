import os
from rich.console import Console
from rich import print as rprint
import time
import openai

from pygments.token import Token

# settings
openai.api_key = os.getenv("OPENAI_API_KEY")


class InvalidInputError(Exception):
    def __init__(self, error_message):
        super().__init__(error_message)


console = Console()

# set api key
if not openai.api_key:
    console.print("[bold red]Please set OPENAI_API_KEY environment variable[/]")
    exit(1)

def update_file_name(name):
    file_name = name.strip("""" '""").lower().replace(' ', '_')
    file_name = file_name if file_name.endswith('.txt') else file_name + '.txt'
    return file_name


def openai_generate(history, test=False, waiting_message="Awaiting OpenAI's response..."):
    if test:
        time.sleep(1)
        return "test_return.txt"

    r = None
    try:
        with console.status(waiting_message) as status:
            r = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=history,
            )
    except KeyboardInterrupt:
        return None
    except openai.error.RateLimitError:
        rprint('[red]Rate limit error from OpenAI[/]')
        return None
    except openai.error.APIError:
        rprint('[red]API error from OpenAI[/]')
        return None
    except openai.error.OpenAIError as e:
        rprint(f'[red]Error from OpenAI: {e}[/]')
        return None


    out = r["choices"][0]["message"]["content"]
    return out.strip()

from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.formatted_text import FormattedText, HTML
from prompt_toolkit.styles import Style
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from .settings import inputing_mode, is_testing, start_cmd, startfrom_cmd, startas_cmd, roles_cmd, user_input_history_dir, editing_mode
from typing import Callable
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text.base import StyleAndTextTuples
from prompt_toolkit.shortcuts import prompt
import prompt_toolkit.lexers
import re

class CustomRegexLexer(prompt_toolkit.lexers.Lexer):
    def __init__(self, regex_mapping):
        super().__init__()
        self.regex_mapping = regex_mapping

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        def lex(_: int):
            line = document.text
            tokens = []
            while len(line) != 0:
                for pattern, style_string in self.regex_mapping.items():
                    match: re.Match = pattern.search(line)

                    if not match:
                        continue
                    else:
                        pass
                    match_string = line[:match.span()[1]]
                    line = line[match.span()[1]:]
                    tokens.append((style_string, match_string))
                    break
            return tokens
        return lex

class regexes:
    cmds_allowed = [start_cmd+"$", startfrom_cmd+" ", startas_cmd+" ", roles_cmd+"$"]
    cmds = re.compile(r"^("+'|'.join([f"{x}" for x in cmds_allowed])+")")
    index = re.compile(fr"(?<={startfrom_cmd})\s*\d+.\d+")
    role = re.compile(fr"(?<={startas_cmd})\s*.+")
    text = re.compile(r"^.")

regex_mapping = {
    regexes.cmds: "#ff70e5",  # Change colors according to your requirement
    regexes.index: "#ffa500",
    regexes.text: "#333333",
    regexes.role: "#2ef5ff",
}

MyCalculatorLexer = CustomRegexLexer(regex_mapping)

# settings
user_input_history = FileHistory(user_input_history_dir)


def get_user_prompt_text(index, user_role):
    return f'[{index}] {user_role} > \n'

def get_ai_prompt_text(ai_role, output):
    return f"[bold green]{ai_role} > \n[/][bold black]{output}[/]\n\n"

def add_to_console_history(message):
    user_input_history.append_string(message)

custom_bindings = KeyBindings()

@custom_bindings.add(Keys.Enter)
def _(event):
    # When Enter is pressed, signal the end of the input
    event.app.exit(result=event.cli.current_buffer.document)

@custom_bindings.add(Keys.ControlN)
def _(event):
    event.cli.current_buffer.insert_text('\n')

user_prompt_style = Style.from_dict({
    'prompt': 'ansired bold',
    'input': '',
})

def get_user_input(user_role='user', default='', index='1.1'):
    _input = ''
    try:
        user_prompt_text = get_user_prompt_text(index, user_role)
        session = PromptSession(history=user_input_history, style=user_prompt_style)
        session.app.key_bindings = custom_bindings

        placeholder = HTML('<ansigray> enter `q` or `exit` to save the chat log and exit</ansigray>')
        user_input_doc = session.prompt(
                user_prompt_text, placeholder=placeholder, multiline=True, default=default, 
                editing_mode=editing_mode)
        user_input = user_input_doc.text.strip()
        if len(user_input) > 1:
            add_to_console_history(user_input)
    except KeyboardInterrupt:
        return ''

    return user_input
