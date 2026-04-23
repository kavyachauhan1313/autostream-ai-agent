import os
import json
from dotenv import load_dotenv

# NVIDIA and LangChain Imports
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import SystemMessage, HumanMessage

# 1. SETUP & INFRASTRUCTURE
load_dotenv()
nv_api_key = os.getenv("NVIDIA_API_KEY")

if not nv_api_key:
    print("CRITICAL: NVIDIA_API_KEY not found in .env")
    exit()

# Initializing Llama 3.1 70B via NVIDIA NIM
llm = ChatNVIDIA(
    model="meta/llama-3.1-70b-instruct", 
    nvidia_api_key=nv_api_key, 
    temperature=0.1
)

# 2. DATA & TOOLS
def get_kb_info():
    """Reads the local knowledge base."""
    with open("data/kb.json", "r") as f:
        return json.load(f)

def mock_lead_capture(name, email, platform):
    """The mandatory tool execution required for the assignment."""
    print(f"\n" + "="*30)
    print(f"SUCCESS: Lead captured for {name}")
    print(f"Email: {email} | Platform: {platform}")
    print(f"="*30 + "\n")
    return "Lead recorded successfully."

# 3. AGENT LOGIC
chat_history = []

def handle_conversation(user_input):
    kb = get_kb_info()
    
    # System prompt defines the persona and the trigger rules
    system_prompt = f"""
    You are the AutoStream Support Agent.
    Company Knowledge Base: {json.dumps(kb)}
    
    INSTRUCTIONS:
    - Answer pricing/feature questions accurately.
    - If a user wants to sign up, you MUST collect: Name, Email, and Creator Platform.
    - Once you have all 3, output ONLY this trigger line: 
      TRIGGER_LEAD: [Name], [Email], [Platform]
    """
    
    chat_history.append(HumanMessage(content=user_input))
    
    # Process with Llama 3.1 70B
    response = llm.invoke([SystemMessage(content=system_prompt)] + chat_history)
    content = response.content
    
    # Tool Execution Detection
    if "TRIGGER_LEAD:" in content:
        try:
            # Parsing logic for Name, Email, and Platform
            data_str = content.split("TRIGGER_LEAD:")[1]
            parts = [p.strip(" []") for p in data_str.split(",")]
            
            # Execute the mandatory mock tool
            mock_lead_capture(parts[0], parts[1], parts[2])
            
            success_msg = "Excellent! I've captured your details. Our team will contact you shortly."
            chat_history.append(HumanMessage(content=success_msg))
            return success_msg
        except Exception:
            return "I've noted your interest! Could you please confirm your email one last time?"

    chat_history.append(response)
    return content

# 4. EXECUTION LOOP
if __name__ == "__main__":
    print("\n--- AutoStream Agent Active (NVIDIA Backend) ---")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            u_input = input("User: ").strip()
            
            if not u_input:
                continue
            if u_input.lower() in ["exit", "quit"]:
                break
            
            print("Agent is thinking (via NVIDIA NIM)...")
            reply = handle_conversation(u_input)
            print(f"Agent: {reply}")
            
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print(f"Error: {e}")