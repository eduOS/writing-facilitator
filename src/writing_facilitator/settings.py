# settings to be placed in yml file
from pathlib import Path
from prompt_toolkit.enums import EditingMode

current_dir = Path(__file__).parent
src_dir = current_dir.parent
package_dir = src_dir.parent

prompt_path = current_dir / "./prompts.csv"
log_dir = package_dir / "logs"
user_input_history_dir = log_dir / ".chatlog"

editing_mode = EditingMode.VI
is_testing = False
inputing_mode = None # vi_mode, editing_mode or None
native_language = 'Chinese'
start_cmd = '/start'
exit_cmd = '/q'
edit_cmd = '/edit'
restart_cmd = '/restart'
startfrom_cmd = '/startfrom'
# switch role and start
startas_cmd =  '/actas'
roles_cmd = '/roles' # with filter string
