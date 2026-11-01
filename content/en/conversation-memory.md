---
title: Conversation records and current state
description: Original sources, message indexes, current state and source version checks.
date: 2026-10-27
kind: Development note
---

Long-running conversations need both original material and the latest decisions. Older records help verify specific wording; current state helps recover progress. They contain different information and change at different rates.

The [memory tool](/projects/ai-memory/) uses file layers and version checks to handle conversation imports, source updates and reading records.

## Information layers

| Layer | Purpose |
|---|---|
| Original material | Preserve specific wording for reading and verification |
| Message index | Record sources, message locations and import progress |
| Current state | Summarize recent decisions, project progress and open questions |

When project scope changes, current state needs an update. The original discussion remains available to explain why it changed.

## Version checks

Each source receives a SHA256 fingerprint. Reading records link to a source ID and a specific version. When a scan detects a change, the source returns to the reading queue.

The program checks the version again when a reading record is submitted. An old record is rejected after the source changes, preventing new material from being marked as processed.

## Reading and updating

A maintainer reads changed material, decides which progress or conclusions it affects, and updates current state. The program records the processed source version and output files.

These records support separate checks: whether material was imported, whether that version was read, and whether current state was updated.

## Public example

The repository uses two fictional sources to demonstrate the first scan, registration of read versions and a source update. In the third step, one source changes and the old record is submitted to test version validation.

Original text, indexes and state remain local files. SQLite records file locations and deduplication information for inspecting the import process.
