from utils.spelling_bee import spelling_bee_tool
import os
from typing import List, TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from langgraph.graph import StateGraph, END
from operator import add as add_messages

load_dotenv()
api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"
llm = ChatMistralAI(
    model=model,
    temperature=0
)
tools = [spelling_bee_tool]
llm = llm.bind_tools(tools)

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

system_prompt = """
You are a Spelling Bee puzzle solver. Use the `spelling_bee` tool to find all valid words for a given central letter and peripheral letters.
Always return the results as a list of tuples, grouped by word length.
"""

def call_llm(state: AgentState) -> AgentState:
    messages = [SystemMessage(content=system_prompt)] + list(state['messages'])
    message = llm.invoke(messages)
    return {'messages': [message]}

def take_action(state: AgentState) -> AgentState:
    tool_calls = state['messages'][-1].tool_calls
    results = []
    for t in tool_calls:
        result = spelling_bee_tool.invoke(t['args'])
        results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
    return {'messages': results}

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("tools", take_action)

def should_continue(state: AgentState):
    return hasattr(state['messages'][-1], 'tool_calls') and len(state['messages'][-1].tool_calls) > 0

graph.add_conditional_edges("llm", should_continue, {True: "tools", False: END})
graph.add_edge("tools", "llm")
graph.set_entry_point("llm")

spelling_bee_agent = graph.compile()

def run_agent():
    """
    Function to run agent on Terminal.
    """
    print("\n=== The Spelling Bee Agent ===")
    while True:
        user_input = input("\nEnter central letter and peripheral letters (e.g., 'E, A G L N O Y'): ")
        if user_input.lower() in ['exit', 'quit']:
            break
        central_letter, *peripheral_letters = user_input.replace(" ", "").split(",")
        messages = [HumanMessage(content=f"Solve for central letter '{central_letter}' and peripheral letters {peripheral_letters}")]
        result = spelling_bee_agent.invoke({"messages": messages})
        print("\n=== Results ===")
        print(result['messages'][-1].content)

def message_to_HumanMessage(message):
    return HumanMessage(content=message)

def message_to_AIMessage(message):
    return AIMessage(content=message)

def spelling_bee_reply(messages: List[BaseMessage]):
    messages_for_agent = [{"role": "human" if isinstance(msg, HumanMessage) else "ai", "content": msg.content} for msg in messages]
    result = spelling_bee_agent.invoke({"messages": messages_for_agent})
    answer = result['messages'][-1].content
    return answer



if __name__ == "__main__":
    run_agent()