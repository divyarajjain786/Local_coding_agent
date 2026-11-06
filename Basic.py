import os
import subprocess
import Loader
from datetime import datetime
from typing import Annotated, Literal, TypedDict
from dotenv import load_dotenv

from langchain_core.runnables import RunnableConfig
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt
from Tools import tools

load_dotenv()

# --- 1. Define State ---
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    Plan: str
    CurrAction: str
    Reason: str
    Impact: str
    Files: list[str]
    Understanding: str
    Home: str
    Rule: str


#Tools moved to an external file for better organization and maintainability. --05/11/2026--
#tools = [file_opener, file_writer, shell_executor, time_fetcher]

# --- 3. Model & Node Definition ---
#model = ChatOllama(model="qwen2.5-coder:7b", temperature=0.7).bind_tools(tools) #Coder doesn't support tool calls --05/11/2026--
model = ChatOllama(model=str(Loader.get_model()), temperature=Loader.get_temperature()).bind_tools(tools)


def call_model(state: State) -> dict:
    messages = state["messages"]

    response = model.invoke(messages)

    #print(response.content)
    print("\n--- LLM DEBUG ---")
    print("Content:", response.content)
    print("Native tool calls:", response.tool_calls)
    print("-----------------\n")

    return {"messages": [response]}

# --- 4. Build Graph ---
workflow = StateGraph(State)

workflow.add_node("llm", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "llm")
workflow.add_conditional_edges("llm", tools_condition, ["tools", END])
workflow.add_edge("tools", "llm")

# Memory saver required for interrupt / HITL support
memory = MemorySaver()
compiled = workflow.compile(checkpointer=memory)
print(compiled.get_graph().draw_mermaid())


# --- 5. Execution ---
if __name__ == "__main__":
    from pathlib import Path
    
    user_prompt = input("Give a prompt for the llm to follow: ")
    dir_path = Path(".")
    files_list = [f.name for f in dir_path.iterdir() if f.is_file()]
    
    initial_state: State = {
        "messages": [HumanMessage(content=user_prompt)],
        "Files": files_list,
        "Plan": "",
        "CurrAction": "",
        "Reason": "",
        "Impact": "",
        "Understanding": "",
        "Home": "",
        "Rule": ""
    }

    config: RunnableConfig = {"configurable": {"thread_id": "1"}}
    
    for event in compiled.stream(initial_state, config=config):
        for value in event.values():
            if "messages" in value:
                print("Response:", value["messages"][-1].content) 