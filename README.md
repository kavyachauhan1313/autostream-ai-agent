## Architecture Explanation
For this project, I chose **LangGraph** because of its superior ability to manage complex, stateful multi-turn conversations compared to standard linear chains. In an agentic support workflow, state management is critical; LangGraph allows for a "cyclic" graph where the agent can transition between knowledge retrieval (RAG) and lead qualification nodes while maintaining a persistent `AgentState`. 

The state is managed using a `TypedDict` that stores the message history and a `user_data` dictionary. By using a `MemorySaver` checkpointer, the agent retains context across 5-6+ turns, satisfying the requirement for long-term memory. The RAG pipeline is integrated directly into the system prompt, allowing **Gemini 1.5 Flash** to reason over the `kb.json` data in real-time. This architecture ensures that intent detection (transitioning from 'info-seeking' to 'signup-ready') is handled naturally through the LLM’s reasoning rather than rigid hard-coded rules.

## WhatsApp Deployment Question
To integrate this agent with WhatsApp:
1. **Webhook Setup**: I would build a **FastAPI** or **Flask** server to act as a Webhook endpoint. 
2. **Provider Integration**: Using the **Twilio Messaging API** or **Meta’s WhatsApp Business API**, I would configure the WhatsApp number to send a POST request to my server whenever a message is received.
3. **Session Management**: I would use the sender's WhatsApp phone number as the `thread_id` in LangGraph. This ensures that each user has their own unique memory state.
4. **Response Loop**: The server would process the message through the LangGraph `app.invoke()`, and the resulting agent output would be sent back to the user via a WhatsApp API call.