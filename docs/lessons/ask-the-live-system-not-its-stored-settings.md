---
id: ask-the-live-system-not-its-stored-settings
applies: scripts/check-campaign-host.py
topics: tooling, windows
roles: main
source: docs/reviews/00-workspace/D00-T03-s12.md#round-11/finding-2
fix: 3e3602b
added: 2026-11-12
status: active
---
Whether a setting is in force (a screen lock, an inactivity policy) is known from the live session or from an event the system records when it takes effect. Stored registry values, file times and arithmetic on the wall clock can each change without the effect changing, and the host check spent ten rounds on them. Read the live state, and where only history exists treat a gap, a clock step or a missing key as not ready.
