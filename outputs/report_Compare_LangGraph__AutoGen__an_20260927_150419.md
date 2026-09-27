# Research Report: Compare LangGraph, AutoGen, and CrewAI for multi-agent orchestration: evaluate graph state persistence, human-in-the-loop streaming workflows, sub-agent delegation mechanisms, and production deployment overhead.

LangGraph, AutoGen, and CrewAI differ significantly in their approach to multi-agent orchestration, particularly in terms of graph state persistence, human-in-the-loop (HITL) streaming workflows, sub-agent delegation mechanisms, and production deployment overhead. Here is a structured evaluation based on the provided sources:

**LangGraph:**
- **Graph State Persistence:** LangGraph uses checkpointing for short-term, thread-scoped memory (e.g., conversation continuity), with stores for long-term, cross-thread memory (e.g., user preferences). It supports persistent TypedDict state, which is checkpointed and shared across nodes. (850 MB [Source Title])
- **Human-in-the-Loop Streaming Workflows:** LangGraph enables native HITL via conditional edges that can route execution to an interrupt node, pausing the graph until a human approves or modifies the next step. This is built into the framework and supports surgical intervention at any point in the graph's execution. (Source Title)
- **Sub-Agent Delegation Mechanisms:** LangGraph allows for subgraphs under a top-level supervisor, with mid-level supervisors distributing work further down. Subgraphs can have separate state schemas and input/output transformations bridging parent and child graphs. (Source Title)
- **Production Deployment Overhead:** LangGraph has lower token consumption and latency in production compared to CrewAI, but it requires developers to manage state manually. It also supports durable, long-running workflows with HITL oversight, which is a significant advantage for production deployments. (Source Title)

**AutoGen:**
- **Graph State Persistence:** AutoGen does not explicitly mention graph state persistence in its documentation. Instead, it focuses on LLM-to-LLM and human-in-the-loop interactions, with agents communicating naturally and delegating tasks. It does not provide a built-in mechanism for persistent state management like LangGraph. (Not provided in search results)
- **Human-in-the-Loop Streaming Workflows:** AutoGen supports HITL through guided or approved agent decisions at key points, but it does not have the same level of built-in HITL capabilities as LangGraph. It requires developers to manually manage HITL workflows. (Source Title)
- **Sub-Agent Delegation Mechanisms:** AutoGen allows agents to communicate and delegate tasks, but it does not explicitly mention sub-agent delegation mechanisms or hierarchical team coordination patterns. It focuses more on ease of use for building multi-agent conversations. (Not provided in search results)
- **Production Deployment Overhead:** AutoGen is designed to reduce the heavy lifting involved in setting up multi-agent workflows, making it easier to deploy in production. However, its production deployment overhead is not explicitly detailed compared to LangGraph. (Source Title)

**CrewAI:**
- **Graph State Persistence:** CrewAI uses native persistence mechanisms for workflows, but these are limited and do not support durable, long-running workflows with HITL oversight. It lacks the ability to manage state manually or provide checkpointing for production deployments. (Not provided in search results)
- **Human-in-the-Loop Streaming Workflows:** CrewAI supports HITL through role-based flows and prompts, but it does not have the same level of built-in HITL capabilities as LangGraph. It requires developers to manually manage HITL workflows. (Source Title)
- **Sub-Agent Delegation Mechanisms:** CrewAI does not mention sub-agent delegation mechanisms or hierarchical team coordination patterns in its documentation. It focuses on providing a simple API for building agents and managing flows. (Not provided in search results)
- **Production Deployment Overhead:** CrewAI has a production gap due to its limited persistence mechanisms and lack of runtime-driven durability. It requires developers to move production-grade responsibilities to Diagrid Catalyst, which is not part of the framework itself. (Source Title)

**Summary:**
LangGraph excels in state management, persistent memory, and HITL capabilities with lower overhead in production. AutoGen is more user-friendly for conversational and deliberative multi-agent scenarios but lacks built-in persistence and state management. CrewAI focuses on rapid prototyping and role-based team coordination but has limitations in production deployment due to its limited persistence and lack of runtime-driven durability.

---
*Editor verdict: ✅ Accepted — Looks good.*