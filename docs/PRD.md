# ARCHON Product Requirements Document (PRD)

## 1. Problem Statement & Target Persona
Campus operations directors and facility managers at universities, hospitals, and large commercial complexes manage millions of square feet with hundreds of interconnected systems. When cascading incidents occur (such as a water main rupture impacting chiller loops and neonatal units), operators are overwhelmed with manual phone coordination, fragmented vendor contracts, and lost tribal knowledge.

ARCHON delivers an enterprise fleet of governed AI agents that autonomously triage signals, map blast radius, dispatch emergency vendors, assemble compliance packets, and preserve institutional knowledge across decades.

## 2. Key User Stories
- **As a Campus Operations Director**, I want incoming IoT alerts to automatically trigger dependency analysis so I immediately know which critical facilities are at risk.
- **As a Facility Safety Officer**, I want vendor communications screened for prompt injections and malicious instructions before any work orders or dispatches are issued.
- **As a Compliance Inspector**, I want the system to cross-reference upcoming regulatory inspections against active repairs so we never fail an audit due to missing paperwork.
- **As a Shift Supervisor**, I want lessons learned from past mechanical failures recalled automatically so technicians do not repeat costly diagnostic mistakes.

## 3. Functional Requirements
- **FR-1 Multi-Signal Ingestion**: Ingest IoT webhooks, vendor emails, operator text reports, and inspection calendar feeds.
- **FR-2 Model Armor Screening**: Filter 14+ injection signatures, redact 5+ PII types, and detect tool parameter poisoning.
- **FR-3 Dynamic Orchestration**: Execute 8+ structured playbooks using Google ADK `transfer_to_agent`.
- **FR-4 Topological Blast Radius Mapping**: Traverse building system dependency graphs to identify secondary failure zones.
- **FR-5 Vendor Management & Auto-Dispatch**: Rank vendors by reliability, response SLA, and contract terms, enforcing human approval for costs over $10,000.
- **FR-6 Real-time Event Streaming**: Stream agent spans, health metrics, and incident statuses over WebSockets at sub-second latency.
- **FR-7 Persistent Institutional Memory**: Store and retrieve historical incident retrospectives, equipment quirks, and vendor ratings via Vertex AI Memory Bank.

## 4. Non-Functional Requirements
- **NFR-1 Offline Resilience**: All tests and services must support local in-memory fallback without requiring live GCP credentials.
- **NFR-2 Zero Trust Security**: Enforce SPIFFE identity validation and domain-scoped JWT permissions on every tool execution.
- **NFR-3 Sub-Second UI Responsiveness**: Deliver a modern Next.js 14 glassmorphism interface with fluid Framer Motion transitions.
- **NFR-4 Comprehensive Test Coverage**: Maintain 42+ unit and integration tests covering governance, resilience, and agent workflows.
