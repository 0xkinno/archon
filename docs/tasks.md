# ARCHON Build Tasks

## Phase 1: Foundation (Backend Core)
- [x] Task 1.1: Initialize Python project and create `requirements.txt` with ADK, FastAPI, Firestore, OpenTelemetry, PyJWT, and Pydantic v2.
- [x] Task 1.2: Build `config.py` with environment variable schema and validation.
- [x] Task 1.3: Define Pydantic models for Incidents, Agents, Audits, Vendors, Buildings, and Tasks in `models/`.
- [x] Task 1.4: Author JSON seed data for 12 campus buildings, 8 vendors, 6 inspections, and 8 playbooks in `data/`.
- [x] Task 1.5: Build `firestore_service.py` with async CRUD and in-memory fallback.
- [x] Task 1.6: Create `health.py` and `main.py` application entry points.
- [x] Task 1.7: Create backend `Dockerfile`.

## Phase 2: Governance Layer
- [x] Task 2.1: Implement Model Armor in `governance/armor.py` with 14 injection regexes, 5 PII redactors, and tool poisoning defense.
- [x] Task 2.2: Implement Agent Gateway in `governance/gateway.py` with 5 core policy checks and ADK `before_tool_callback`.
- [x] Task 2.3: Implement Agent Identity in `governance/identity.py` with SPIFFE URI generation and scoped JWT validation.
- [x] Task 2.4: Implement Agent Registry in `governance/registry.py` with manifest discovery and heartbeat status updates.
- [x] Task 2.5: Implement Agent Observability in `governance/observability.py` with OpenTelemetry tracing and reasoning tree reconstruction.
- [x] Task 2.6: Implement Resilience in `governance/resilience.py` with model error fail-safes and loop detection.

## Phase 3: Agent Fleet (ADK Core)
- [x] Task 3.1: Build `gemini_service.py` with `HttpRetryOptions` exponential backoff configuration.
- [x] Task 3.2: Implement `building_systems.py` tool suite for BMS queries, occupancy checks, and dependency graphs.
- [x] Task 3.3: Implement `vendor_management.py` tool suite for vendor search, scoring, and auto-dispatch.
- [x] Task 3.4: Implement `compliance_tools.py` for inspection lookups and compliance documentation generation.
- [x] Task 3.5: Implement `notification_tools.py` for multi-channel stakeholder alerting.
- [x] Task 3.6: Implement `remediation_tools.py` for task tracking, escalation, and shift handoffs.
- [x] Task 3.7: Implement `memory_tools.py` and `memory_service.py` for Vertex AI Memory Bank operations.
- [x] Task 3.8: Define all 7 ADK agents with domain instructions, tools, and 4 governance callbacks.

## Phase 4: API Layer & Real-time WebSocket
- [x] Task 4.1: Build REST endpoints in `api/routes.py` covering incidents, agents, memory, traces, approvals, and armor.
- [x] Task 4.2: Build WebSocket hub in `api/websocket.py` for live broadcasting of 10 system event types.
- [x] Task 4.3: Implement cascading simulation engine for the Storm Response scenario.

## Phase 5 & 6: Frontend Landing & Operations Dashboard
- [x] Task 5.1: Configure Next.js 14, Tailwind CSS, TypeScript, and custom command color tokens.
- [x] Task 5.2: Create landing page components (Hero, Problem, Solution, Fleet, Governance, Architecture, Demo, TechStack, Footer).
- [x] Task 5.3: Build Operations Dashboard layout with collapsible sidebar and metrics strip.
- [x] Task 5.4: Build live Incident Timeline, WebSocket Live Feed, Agent Status Grid, Detail View, Memory Explorer, Trace Tree Viewer, and Approval Queue.

## Phase 7, 8, 9 & 10: Testing, Deployment, Documentation & Polish
- [x] Task 7.1: Create deployment scripts for Cloud Run and Vertex AI Agent Platform.
- [x] Task 8.1: Write 42+ unit and integration tests across 6 test modules.
- [x] Task 9.1: Assemble story-mode `README.md`, diagrams, and competitive analysis.
- [x] Task 10.1: Prepare video script and submission materials.
