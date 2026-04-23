import os
import json
from google import genai
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 1. SETUP
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY"),
    http_options={'api_version': 'v1'} # Forces the stable production path
)

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "The conversation history"]

# 2. TOOL
def mock_lead_capture(name, email, platform):
    print(f"\n{'='*40}\n✅ SUCCESS: LEAD CAPTURED ✅\nUser: {name} | Email: {email} | Target: {platform}\n{'='*40}\n")

# 3. AGENT NODE
def call_model(state: AgentState):
    with open("data/kb.json", "r") as f:
        kb = f.read()

    history = []
    for m in state['messages']:
        role = "user" if isinstance(m, HumanMessage) else "model"
        history.append({"role": role, "parts": [{"text": m.content}]})

    prompt = f"System: Use this KB: {kb}. Collect Name, Email, Platform. If done, say CONFIRMED: [Name], [Email], [Platform]"
    
    # CHANGED TO 2.0-FLASH FOR 2026 STABILITY
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=history + [{"role": "user", "parts": [{"text": prompt}]}]
    )
    
    return {"messages": [AIMessage(content=response.text)]}

# 4. GRAPH
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app = workflow.compile(checkpointer=MemorySaver())

# 5. RUN
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "victory_lap"}}
    print("\n--- AutoStream Agent: 2026 Verified Build ---")
    
    while True:
        u_input = input("\nUser: ")
        if u_input.lower() in ["exit", "quit"]: break
        
        try:
            output = app.invoke({"messages": [HumanMessage(content=u_input)]}, config)
            reply = output['messages'][-1].content
            print(f"Agent: {reply}")
            
            if "CONFIRMED:" in reply:
                parts = reply.split("CONFIRMED:")[1].split(",")
                mock_lead_capture(parts[0].strip(" []"), parts[1].strip(), parts[2].strip(" []"))
        except Exception as e:
            print(f" Error: {e}")