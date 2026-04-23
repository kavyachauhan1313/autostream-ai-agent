import os
import json
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv

# OpenAI + LangGraph Stack
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# 1. INITIALIZE GPT-4o MINI
# This model is extremely stable and rarely hits 429s for basic support tasks
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0
)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The conversation history"]

def mock_lead_capture(name, email, platform):
    print(f"\n{'='*40}\n SUCCESS: LEAD CAPTURED \nUser: {name} | Email: {email} | Target: {platform}\n{'='*40}\n")

# 2. AGENT NODE
def call_model(state: AgentState):
    with open("data/kb.json", "r") as f:
        kb = f.read()

    system_prompt = SystemMessage(content=f"""
    You are the AutoStream Support Agent. KB: {kb}
    If you have Name, Email, and Platform, say: CONFIRMED: [Name], [Email], [Platform]
    """)
    
    response = llm.invoke([system_prompt] + state['messages'])
    return {"messages": [response]}

# 3. GRAPH CONSTRUCTION
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app = workflow.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "gpt_demo"}}
    print("\n--- AutoStream Agent: GPT-4o mini Build ---")
    
    while True:
        u_input = input("\nUser: ")
        if u_input.lower() in ["exit", "quit"]: break
        
        output = app.invoke({"messages": [HumanMessage(content=u_input)]}, config)
        reply = output['messages'][-1].content
        print(f"Agent: {reply}")
        
        if "CONFIRMED:" in reply:
            try:
                parts = reply.split("CONFIRMED:")[1].split(",")
                mock_lead_capture(parts[0].strip(" []"), parts[1].strip(), parts[2].strip(" []"))
            except: pass