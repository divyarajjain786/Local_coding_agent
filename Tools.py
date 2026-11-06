from datetime import datetime
from pathlib import Path
import time as t
import subprocess
from typing import Annotated, Literal, TypedDict
from langchain_core.tools import tool

from langgraph.graph import END, START, StateGraph

# --- 2. Define Tools ---
@tool
def file_opener(file_path: str) -> str:
    """Opens a file and returns its contents in the current directory."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def file_writer(file_path: str, content: str) -> str:
    """Writes content to a file in the current directory or creates a new file. To create a new folder, just make an empty file at the path and folder would automatically be created"""
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return f"File {file_path} written successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"
@tool
def folder_creator(folder_path: str) -> str:
    """Creates a new folder in the current directory."""
    try:
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        return f"Folder {folder_path} created successfully."
    except Exception as e:
        return f"Error creating folder: {str(e)}"

@tool
def shell_executor(command: str) -> str:
    """Executes a Windows shell command and returns its output."""

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        return result.stdout or result.stderr

    except Exception as e:
        return f"Error executing command: {str(e)}"

@tool
def time_fetcher() -> str:
    """Fetches the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def wait(seconds: int) -> bool:
    """Provides a mechanism to wait for time supplied in seconds"""
    t.sleep(seconds)
    return True

@tool
def get_struc() -> dict:
    """Returns name of all => files in the current directory along with file paths"""
    dir_path = Path(".")
    files_list = [f.name for f in dir_path.iterdir() if f.is_file()]
    return {"Files": files_list}

@tool
def continue_conversation() -> str:
    """Invoke this tool to engage in multi turn conversations and take input from user"""
    user = input("User: ")
    return f"User: {user}"

#------------FINAL LIST-------------#
tools = [file_opener, file_writer, folder_creator, shell_executor, time_fetcher, wait, get_struc, continue_conversation]