---
title: AI conversation memory
description: Incremental conversation imports, source version checks and topic state management.
date: 2026-10-27
---

A local information management tool for long-running collaboration with AI. It imports conversations incrementally, checks source versions and maintains current topic state. A new conversation can read the saved state to recover project progress and open questions.

## Information layers

Original sources, message indexes and current state are stored separately. Original material supports close reading; indexes record message locations; current state summarizes decisions, progress and unresolved questions.

Sources are versioned with SHA256. When a file changes, it returns to the reading queue. A submitted reading record is checked against the source version and rejected if it is stale.

![Source versions and reading records](/site-assets/ai-memory.png)

## Working example

The public demo uses fictional material to show three steps:

1. A first scan finds two sources awaiting reading.
2. A maintainer reads them, updates current state and registers the versions read.
3. A source changes; submitting the old record is rejected.

The maintainer reads the material and updates state. The program handles indexing, version comparison and record validation.

## Implementation

`prompt_intake.py` reads exported JSONL conversations and stores file offsets and deduplication indexes in SQLite. `continuity.py` compares source versions with reading records. `knowledge_gate.py` checks tags, links and graph references.

The public implementation uses the Python standard library. I designed the requirements, information layers and acceptance criteria, with AI assistance for implementation.

Related note: [Conversation records and current state](/notes/conversation-memory/).
