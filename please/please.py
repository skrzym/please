#!/usr/bin/env python
import datetime
import json
import os
import random
import shutil
from os.path import expanduser

import typer
from typing_extensions import Annotated
from typing import Optional
from rich.align import Align
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule
from rich.table import Table

app = typer.Typer()
console = Console()

COLOR_INFO = "cyan1 on purple3"
COLOR_SUCCESS = "black on green"
COLOR_WARNING = "bright_red on bright_white"
COLOR_ERROR = "black on bright_red"


def center_print(text, style: str = None, wrap: bool = False) -> None:
    """Print text with center alignment.

    Args:
        text (Union[str, Rule, Table]): object to center align
        style (str, optional): styling of the object. Defaults to None.
    """
    if wrap:
        width = shutil.get_terminal_size().columns // 2
    else:
        width = shutil.get_terminal_size().columns

    console.print(Align.center(text, style=style, width=width))


def write_config(data: dict) -> None:
    with open(os.path.join(config_path, "config.json"), "w") as of:
        of.write(json.dumps(data, indent=2))


def check_for_completed_tasks_file() -> None:
    if not os.path.exists(os.path.join(config_path, "completed_tasks.json")):
        with open(os.path.join(config_path, "completed_tasks.json"), "w") as of:
            of.write("[]")


def read_completed_tasks() -> dict:
    check_for_completed_tasks_file()
    with open(os.path.join(config_path, "completed_tasks.json"), "r") as of:
        existing_data = json.load(of)
    return existing_data


def write_completed_tasks(data: dict) -> None:
    check_for_completed_tasks_file()
    existing_data = read_completed_tasks()
    existing_data.extend(data)
    with open(os.path.join(config_path, "completed_tasks.json"), "w") as of:
        of.write(json.dumps(existing_data, indent=2))


def all_tasks_done() -> bool:
    return all(task["done"] for task in config["tasks"])


@app.command(short_help="Change name without resetting data")
def callme(name: str) -> None:
    config["user_name"] = name
    write_config(config)
    center_print("\nThanks for letting me know your name!\n", "black on green")


@app.command(short_help="Add a Task")
def add(task: str) -> None:
    new_task = {"name": task, "done": False}
    config["tasks"].append(new_task)
    write_config(config)
    center_print(f'Added "{task}" to the list', COLOR_SUCCESS)
    print_tasks()


@app.command(short_help="Deletes a Task")
def delete(index: int) -> None:
    index = index - 1
    if len(config["tasks"]) == 0:
        center_print(
            "Sorry, There are no tasks left to delete", COLOR_INFO, wrap=True
        )
        return

    if not 0 <= index < len(config["tasks"]):
        center_print(
            "Are you sure you gave me the correct number to delete?",
            COLOR_WARNING,
            wrap=True,
        )
    else:
        deleted_task = config["tasks"][index]
        del config["tasks"][index]
        write_config(config)
        center_print(f"Deleted '{deleted_task['name']}'", COLOR_SUCCESS)
        print_tasks(True)


@app.command(short_help="Mark a task as done")
def do(index: int) -> None:
    index = index - 1

    if not 0 <= index < len(config["tasks"]):
        center_print(
            "Are you sure you gave me the correct number to mark as done?",
            COLOR_WARNING,
            wrap=True,
        )
        return

    if len(config["tasks"]) == 0:
        center_print(
            "Sorry, There are no tasks to mark as done", COLOR_ERROR, wrap=True
        )
        return

    if (config["tasks"][index]["done"] == True):
        center_print("No Updates Made, Task Already Done",
                     COLOR_INFO)
        print_tasks()
        return

    if all_tasks_done():
        center_print("All tasks are already completed!", COLOR_SUCCESS)
        return

    config["tasks"][index]["done"] = True
    write_config(config)
    center_print("Updated Task List", COLOR_SUCCESS)
    print_tasks()


@app.command(short_help="Mark a task as undone")
def undo(index: int) -> None:
    index = index - 1

    if not 0 <= index < len(config["tasks"]):
        center_print(
            "Are you sure you gave me the correct number to mark as undone?",
            COLOR_WARNING,
            wrap=True,
        )
        return

    if len(config["tasks"]) == 0:
        center_print(
            "Sorry, There are no tasks to mark as undone", COLOR_INFO, wrap=True
        )
        return

    if (config["tasks"][index]["done"] == False):
        center_print("No Updates Made, Task Still Pending",
                     COLOR_INFO)
        print_tasks()
        return

    config["tasks"][index]["done"] = False
    write_config(config)
    center_print("Updated Task List", COLOR_SUCCESS)
    print_tasks()


@app.command(short_help="Change task order")
def move(old_index: int, new_index: int):
    if (len(config["tasks"]) == 0):
        center_print(
            "Sorry, cannot move tasks as the Task list is empty", COLOR_ERROR
        )
        return

    try:
        config["tasks"][old_index - 1], config["tasks"][new_index - 1] = (
            config["tasks"][new_index - 1],
            config["tasks"][old_index - 1],
        )
        write_config(config)
        if old_index != new_index:
            center_print("Updated Task List", COLOR_SUCCESS)
        else:
            center_print("No Updates Made", COLOR_INFO)
        print_tasks(config["tasks"])
    except:
        center_print(
            "Please check the entered index values", COLOR_WARNING
        )


@app.command(short_help="Edit task name")
def edit(index: int, new_name: str) -> None:
    if not 0 <= index - 1 < len(config["tasks"]):
        center_print(
            "Are you sure you gave me the correct task number?",
            COLOR_WARNING,
            wrap=True,
        )
        return

    if (len(config["tasks"]) == 0):
        center_print(
            "Sorry, cannot edit tasks as the Task list is empty", COLOR_ERROR
        )
        return

    if (len(new_name) == 0):
        center_print(
            "Please enter a valid name", COLOR_ERROR
        )
        return

    try:
        old_name = config["tasks"][index - 1]["name"]
        config["tasks"][index - 1]["name"] = new_name
        write_config(config)
        if old_name != new_name:
            center_print("Updated Task Name", COLOR_SUCCESS)
        else:
            center_print("No Updates Made", COLOR_INFO)
        print_tasks(config["tasks"])
    except:
        center_print(
            "Please check the entered Task index and new Task name", COLOR_WARNING
        )


@app.command(short_help="Clean up tasks marked as done from the task list")
def clean() -> None:
    res = []
    completed = []
    for i in config['tasks']:
        if i['done'] != True:
            res.append(i)
        else:
            completed.append(i)
    if config['tasks'] != res:
        config['tasks'] = res
        write_config(config)
        write_completed_tasks(completed)
        center_print(f"Updated Task List. Archived {len(completed)} tasks.", COLOR_SUCCESS)
        print_tasks(config["tasks"])
        return
    center_print("No Updates Made", COLOR_INFO)
    print_tasks(config["tasks"])


@app.command(short_help="Set a custom file to fetch quotes")
def changequotes(quotes_file: str) -> None:
    #Check if file exists and it is a valid JSON
    try:
        with open(quotes_file, "r") as qf:
            quotes = json.load(qf)

        #Check if the file has at least one quote
        if len(quotes) == 0:
            center_print(
                "There must be at least 1 quote", COLOR_ERROR
            )
            return

        #Check if the file has the right keys
        try:
            for q in quotes:
                content = q["content"]
                author = q["author"]
            
            # File is valid, replace the path in the config.json
            config["quotes_file"] = quotes_file
            center_print("Changed quote file to " + quotes_file,
                         COLOR_SUCCESS)
            write_config(config)
        
        #Catch wrong key error exception
        except KeyError:
            center_print(
                "The JSON must have the \"author\" and \"content\" fields", COLOR_ERROR
            )

    #Catch no file exception
    except FileNotFoundError:
        center_print(
            "Sorry, the file was not found, ensure that you provided the full path\n of the JSON file and the file exists", COLOR_ERROR
        )
    #Catch a bag JSON format exception
    except json.decoder.JSONDecodeError:
        center_print(
            "Please insert a file with a valid JSON format", COLOR_ERROR
        )


def print_tasks(status:str = '') -> None:
    tasks = config["tasks"]
    table1 = Table(
        title="Tasks",
        title_style="grey39",
        header_style="#e85d04",
        style="#e85d04 bold",
    )
    table1.add_column("Number", style="#e85d04")
    table1.add_column("Task")
    table1.add_column("Status")

    if status == 'completed':
        task_list = [task for task in tasks if task['done'] == True]
    elif status == 'pending':
        task_list = [task for task in tasks if task['done'] == False]
    else:
        task_list = tasks.copy()

    for index, task in enumerate(task_list):
        if task["done"]:
            task_name = f"[#A0FF55] {task['name']}[/]"
            task_status = f'{config.get("done_icon", "✅")}'
            task_index = f"[#A0FF55] {str(index + 1)} [/]"
        else:
            task_name = f"[#FF5555] {task['name']}[/]"
            task_status = f'{config.get("notdone_icon", "❌")}'
            task_index = f"[#FF5555] {str(index + 1)} [/]"

        table1.add_row(task_index, task_name, task_status)
    
    if table1.row_count == 0:
        center_print("No tasks to show", COLOR_INFO)
    else:
        center_print(table1)


def showarchive() -> None:
    completed_tasks = read_completed_tasks()
    table1 = Table(
        title="Completed Tasks",
        title_style="grey39",
        header_style="#e85d04",
        style="#e85d04 bold",
    )
    table1.add_column("Number", style="#e85d04")
    table1.add_column("Task")
    table1.add_column("Status")

    if len(completed_tasks) == 0:
        center_print(table1)
    else:
        for index, task in enumerate(completed_tasks):
            task_name = f"[#A0FF55] {task['name']}[/]"
            task_status = f'{config.get("done_icon", "✅")}'
            task_index = f"[#A0FF55] {str(index + 1)} [/]"
            table1.add_row(task_index, task_name, task_status)
        center_print(table1)


def getquotes() -> dict:
    """Select a random quote.

    Returns:
        dict: quote with its metadata
    """

    with open(config["quotes_file"], "r") as qf:
        quotes_file = json.load(qf)
    return quotes_file[random.randrange(0, len(quotes_file))]


@app.command(short_help="Reset all data and run setup")
def setup() -> None:
    """Initialize the config file."""
    config = {}
    config["user_name"] = typer.prompt(
        typer.style("Hello! What can I call you?", fg=typer.colors.CYAN)
    )

    code_markdown = Markdown(
        """
        please callme <Your Name Goes Here>
    """
    )
    center_print("\nThanks for letting me know your name!")
    center_print("If you wanna change your name later, please use:", "red")
    console.print(code_markdown)

    #Get location
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )

    config["initial_setup_done"] = True
    config["tasks"] = []
    config["options"] = {
        "line": True,
        "quotes": True,
        "greeting": True,
        "24h_time_format": False,
        "clear_console": False,
    }
    config["done_icon"] = "✅"
    config["notdone_icon"] = "❌"
    config["quotes_file"] = os.path.join(__location__, "quotes.json")
    write_config(config)


@app.callback(invoke_without_command=True)
def base(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        show()


def display_header() -> None:
    if "clear_console" in config['options'].keys() and config['options']["clear_console"] == True:
        console.clear()
    else:
        config['options']["clear_console"] = False
        write_config(config)
    
    date_now = datetime.datetime.now()
    user_name = config["user_name"]
    
    date_text = ""

    if "greeting" in config['options'].keys() and config['options']["greeting"] == False:
        pass
    else:
        config['options']["greeting"] = True
        write_config(config)
        try:
            if config['options']["24h_time_format"] is (None or False):
                date_text = f"[#FFBF00] Hello {user_name}! It's {date_now.strftime('%d %b | %I:%M %p')}[/]"
            else:
                date_text = f"[#FFBF00] Hello {user_name}! It's {date_now.strftime('%d %b | %H:%M')}[/]"
        except:
            config['options']["24h_time_format"] = False
            write_config(config)
            date_text = f"[#FFBF00] Hello {user_name}! It's {date_now.strftime('%d %b | %I:%M %p')}[/]"

    if "line" in config['options'].keys() and config['options']["line"] == False:
        center_print(date_text)
    else:
        config['options']["line"] = True
        write_config(config)
        console.rule(date_text, align="center", style="#FFBF00")

    if "quotes" in config['options'].keys() and config['options']["quotes"] == False:
        pass
    else:
        config['options']["quotes"] = True
        write_config(config)
        quote = getquotes()
        center_print(f'[#63D2FF]"{quote["content"]}"[/]', wrap=True)
        center_print(
            f'[#F03A47][i]- {quote["author"]}[/i][/]\n', wrap=True)


@app.command(short_help="Chose what to show")
def show(
        thing: Optional[str] = typer.Argument(default=''), 
        completed:bool  = None, 
        pending:bool    = None, 
        archived:bool   = None
    ) -> None:
    if thing == '':
        center_print("Please enter a valid option: ['tasks']", COLOR_INFO)
    elif thing == 'tasks':
        display_header()
        if completed:
            print_tasks(status='completed')
        elif pending:
            print_tasks(status='pending')
        elif archived:
            showarchive()
        else:
            print_tasks()
    elif type(thing) == str:
        display_header()
        center_print(f'{thing} -> Not implemented yet. Valid options are ["tasks"]', COLOR_ERROR)
    else: #if what got passed is not a string and doesn't match any of the above
        display_header()
        print_tasks()


@app.command(short_help="Disable/Enable various settings")
def toggle(name: str) -> None:
    options = ["line", "quotes", "greeting", "24h_time_format", "clear_console"]
    if name not in options:
        center_print(
            f"Invalid option. Valid options are {options}", COLOR_ERROR)
        return
    try:
        if config['options'][name] is (None or False):
            config['options'][name] = True
            center_print(f"Enabled {name}", COLOR_SUCCESS)
        else:
            config['options'][name] = False
            center_print(f"Disabled {name}", COLOR_SUCCESS)
    except:
        config['options'][name] = True
    write_config(config)


def main() -> None:
    """Load config file and program initialization."""
    global config_path
    config_path = os.path.join(expanduser("~"), ".config", "please")
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    try:
        with open(os.path.join(config_path, "config.json")) as config_file:
            global config
            config = json.load(config_file)
    except FileNotFoundError:
        open(os.path.join(config_path, "config.json"), "w")
        typer.run(setup)
    except json.JSONDecodeError:
        center_print(
            "Something's wrong with your config file. You can fix ~/.config/please/config.json file manually or you can enter your name again in the setup wizard to reset the config file. ENTERING NAME WILL OVERWRITE YOUR PREVIOUS CONFIG.", COLOR_WARNING)
        typer.run(setup)
    else:
        if config["initial_setup_done"] is True:
            app()
        else:
            typer.run(setup)


main()
