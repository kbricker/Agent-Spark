---
name: Multi-agent orchestration research (2025-2026)
description: Research findings on multi-agent patterns, failure modes, and scaling limits for software development tasks
type: reference
scope: global
---

Key findings from research conducted 2026-03-26:

- **Orchestrator-worker pattern** is the best for software engineering (what Hive uses)
- **Structured artifact passing** (plans, checklists, diffs) beats free-form chat — validated by MetaGPT research
- Performance **degrades past ~4 agents** without structured coordination topology (Google DeepMind, Dec 2025)
- **17.2x error amplification** in unstructured systems; centralized coordination contains to 4.4x
- Don't parallelize inherently sequential work — 39-70% worse
- Cost scales 3-7x for agent teams vs single sessions
- **14 failure modes** identified in MAST taxonomy (Cemri et al., March 2025): poor decomposition, error cascading, handoff ambiguity, premature completion marking
- 40%+ of agentic AI projects predicted to be canceled by 2027 due to complexity (Gartner)

Key papers: arXiv:2503.13657 (MAST failure taxonomy), arXiv:2512.08296 (DeepMind scaling)
Frameworks: LangGraph (best for complex), CrewAI (simpler but teams hit limits), Microsoft Agent Framework (enterprise)
