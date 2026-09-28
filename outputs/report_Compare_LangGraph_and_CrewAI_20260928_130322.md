# Research Report: Compare LangGraph and CrewAI: state persistence and human-in-the-loop support

LangGraph and CrewAI both support human-in-the-loop (HITL) workflows, but they differ in their approach to state persistence and human-in-the-loop support. 

LangGraph uses `interrupt()` to pause execution mid-step, save the graph state via Checkpointers, and resume after a human decision. The `StateSnapshot` captures the complete context of the agent, including `values`, `next`, `config`, `tasks`, and metadata. LangGraph's persistence layer ensures that the graph state is saved at every "super-step" of the workflow, enabling durable persistence and allowing execution to pause safely and resume later.

CrewAI supports HITL through the `@human_feedback` decorator, which pauses execution, presents output for review, collects feedback, and routes to different paths based on the response. It also provides task replay, allowing specific tasks from a previous crew execution to be rerun without refetching data. CrewAI's persistence layer ensures that the full state of the workflow is preserved across async human interactions.

LangGraph's `interrupt()` function allows for precise control over when and how human input is handled, while CrewAI's `@human_feedback` decorator provides a more integrated and user-friendly interface for HITL. Both systems support durable persistence, but LangGraph emphasizes checkpointing at every "super-step" with a focus on state management and resumption, whereas CrewAI focuses on integrating HITL into the workflow through annotations and task replay.

## References

- [Human-in-the-Loop Agents: State & Interrupts](https://medium.com/data-science-collective/architecting-human-in-the-loop-agents-interrupts-persistence-and-state-management-in-langgraph-fa36c9663d6f)
- [Making it easier to build human-in-the-loop agents with ...](https://www.langchain.com/blog/making-it-easier-to-build-human-in-the-loop-agents-with-interrupt)
- [Human-in-the-Loop](https://www.guild.ai/glossary/human-in-the-loop)
- [LangGraph - Persistence & Human-in-the-Loop Workflow](https://www.youtube.com/watch?v=9BPCV5TYPmg)
- [Running CrewAI Reliably with Catalyst's Durable Execution | Diagrid Learn](https://www.diagrid.io/learn/crewai-durable-execution)
- [A Missing Layer in Agentic Systems? | CrewAI](https://crewai.com/blog/a-missing-layer-in-agentic-systems)
- [Human-in-the-loop - Docs by LangChain](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
- [[QUESTION] How to design asynchronous human-in-the-loop Crews running on the backend? · Issue #2051 · crewAIInc/crewAI](https://github.com/crewAIInc/crewAI/issues/2051)

---
*Editor verdict: ✅ Accepted — Looks good.*