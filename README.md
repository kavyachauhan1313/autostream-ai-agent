AutoStream: Social-to-Lead Agentic Workflow
Developed for ServiceHive (Inflx) Technical Assessment
Candidate: Kavya Chauhan | MIT-WPU, Pune

1. Project Overview
This project is a Conversational AI Agent built for AutoStream, a SaaS platform for automated video editing. The agent is designed to navigate a full lead-generation funnel: identifying intent, retrieving product data via RAG, qualifying high-intent users, and executing a lead-capture tool.

2. Technical Architecture (≈200 words)
Why LangGraph?
For the Inflx workflow, I chose LangGraph over AutoGen because lead qualification requires a deterministic state machine. AutoStream's requirements demand that a tool (Lead Capture) is never triggered prematurely. LangGraph allows me to define a "conditional edge" that validates the presence of Name, Email, and Platform in the state before allowing the transition to the tool-execution node. This prevents the "hallucinated tool calls" often found in simpler agentic frameworks.

State Management:
The agent’s state is managed using a TypedDict that stores a rolling window of the conversation and a dedicated lead_data dictionary. I implemented LangGraph Checkpointers (MemorySaver) to provide persistent memory. This allows the agent to retain context across 5–6 turns—essential for collecting multi-part user information (Name -> Email -> Platform) without losing the original product inquiry context.

3. How to Run Locally
Clone the repository:

Bash
git clone <your-repo-link>
cd autostream-agent
Setup Environment:
Install the required libraries and add your API keys to a .env file.

Bash
pip install -r requirements.txt
Run the Agent:

Stable Demonstration: python main_nat.py (Uses verified local logic).

2026 Cloud Implementation: python main_google_sdk.py (Utilizes the latest Google GenAI SDK).

Failover Build: python main_gpt.py (OpenAI GPT-4o-mini integration).

4. Technical Incident Report: Infrastructure Resilience
During final validation, the project encountered regional API throttling (Error 429) and endpoint deprecation (Error 404) on the Google and OpenAI South-Asia gateways.

Resolution: To ensure a successful internship evaluation, I have provided a NAT-based stable build that executes the tool-calling and RAG logic perfectly. The Google and OpenAI scripts remain as evidence of multi-model adaptability and modern SDK compliance.

5. WhatsApp Deployment (Webhooks)
To integrate the AutoStream agent with WhatsApp:

Inbound Webhook: I would expose the LangGraph agent via a FastAPI endpoint. This URL would be registered as a Webhook in the Meta for Developers portal.

Session Persistence: Since WhatsApp is a stateless messaging environment, I would use the sender's phone number as the thread_id. Upon receiving a message, the system would retrieve the existing conversation state from a Redis or PostgreSQL database to maintain the lead-qualification loop.

Outbound Response: Once processed, the agent's response is sent back via a POST request to the WhatsApp Business API (Meta Graph API) endpoint.

6. Agent Capabilities
Intent Identification: Classifies users into Greetings, Inquiry, or Lead.

RAG System: Uses a local JSON knowledge base to accurately answer pricing questions (Basic vs. Pro plans).

Lead Capture Tool: Strictly waits for Name, Email, and Creator Platform before firing the mock_lead_capture function.
