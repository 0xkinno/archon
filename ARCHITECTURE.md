# ARCHON: Architecture Deep-Dive

## Architectural Philosophy & Core Tenets

ARCHON is built to transform chaotic physical campus operations into a disciplined, governed, and highly observable autonomous ecosystem. The architecture is guided by five principles:

1. **Tool-Boundary Defense**: Guardrails are placed strictly at tool input/output boundaries (`before_tool_callback` and `after_tool_callback`), preventing compromised model outputs from executing dangerous physical or financial actions.
2. **Specialized Fleet Division**: Seven discrete specialist agents operate strictly within their designated domains. No agent performs another agent's role.
3. **Institutional Memory Continuity**: Context, vendor performance scores, structural quirks, and past incident lessons persist across sessions, shifts, and years via Vertex AI Memory Bank.
4. **Zero-Trust Identity**: Every tool call requires a valid SPIFFE-identified, domain-scoped JWT token validated before execution.
5. **Deterministic Resilience**: When external APIs or LLM backends experience transient outages, ARCHON degrades gracefully with structured fallback outcomes rather than fabricating data.

---

## The 7 Gemini Enterprise Agent Platform (GEAP) Subsystems

```
+-----------------------------------------------------------------------------------+
|                            SIGNAL INGESTION LAYER                                 |
|      IoT BMS Webhooks  |  Vendor Emails  |  Manual Reports  |  Inspection Feeds   |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    1. MODEL ARMOR (governance/armor.py)                          |
|     - 14 Prompt Injection Signatures   - 5 PII Redaction Regexes                  |
|     - Tool Poisoning Detection         - ADK after_tool_callback Screening         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    2. AGENT GATEWAY (governance/gateway.py)                       |
|     - Tainted Source Enforcement       - $10,000 Financial Threshold Escalation   |
|     - 20-Call Per-Incident Rate Limiter- Domain Tool Access Control               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    3. AGENT REGISTRY (governance/registry.py)                     |
|     - Firestore Manifest Catalog       - Semantic Version Tracking                |
|     - Heartbeat Health Monitor         - Dynamic Playbook Discovery Engine        |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    4. AGENT FLEET (agents/* & Google ADK)                         |
|     - incident_commander (Orchestrator, Triage & Playbook Execution)              |
|     - impact_assessor (Blast Radius, Topological Graph & Dependency Mapping)      |
|     - vendor_coordinator (Vendor Scoring, Auto-Dispatch & SLA Management)        |
|     - compliance_inspector (Regulatory Deadlines, Fire/OSHA Gaps, Doc Assembly)   |
|     - communications_officer (Stakeholder Alerts, Multi-Channel Routing)          |
|     - remediation_tracker (Corrective Tasks, Escalations, Shift Handoffs)         |
|     - memory_curator (Precedent Search, Knowledge Extraction, Scorecards)         |
+-----------------------------------------------------------------------------------+
                      |                                       |
                      v                                       v
+------------------------------------+  +-------------------------------------------+
| 5. MEMORY BANK                     |  | 6. AGENT OBSERVABILITY                    |
| (services/memory_service.py)       |  | (governance/observability.py)             |
| - Vertex AI Memory Bank Service    |  | - OpenTelemetry Span Hierarchy            |
| - Incident Lesson Vector Store     |  | - Append-Only Firestore Audit Ledger      |
| - Building Quirks & Vendor History |  | - Full Reasoning Tree Reconstruction      |
+------------------------------------+  +-------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                    7. AGENT IDENTITY (governance/identity.py)                     |
|     - SPIFFE-Compatible URIs (spiffe://archon.campus/agent/{name})               |
|     - HS256 Scoped JWT Tokens with Domain Claims                                  |
|     - Tool Permission Verification Middleware                                     |
+-----------------------------------------------------------------------------------+
```

---

## Subsystem Details

### 1. Model Armor (`backend/governance/armor.py`)
Model Armor is the first line of defense for all inbound signals and tool returns.
- **Prompt Injection Defense**: Evaluates incoming text against 14 battle-tested regex signatures (including instruction resets, role impersonation, system prompt extraction, and admin override tags).
- **PII Redaction**: Automatically identifies and sanitizes phone numbers, emails, Social Security numbers, credit card numbers, and street addresses, replacing them with canonical tokens (`[REDACTED_PHONE]`, `[REDACTED_EMAIL]`, etc.).
- **Tool Poisoning Protection**: Screens tool parameters for malicious meta-commands or attempted code execution.
- **ADK Hook**: Runs inside `after_tool_callback` to ensure tainted payloads are quarantined in session state.

### 2. Agent Gateway (`backend/governance/gateway.py`)
The Gateway enforces deterministic governance rules across all agent tool requests via `before_tool_callback`.
- **Policy 1 (Tainted Source)**: Rejects tool calls referencing sources quarantined by Model Armor.
- **Policy 2 (Financial Threshold)**: Holds any purchase order, dispatch, or remediation exceeding $10,000 in an approval queue, requiring explicit human sign-off.
- **Policy 3 (Domain Scoping)**: Enforces least-privilege tool execution based on registered agent manifests (e.g., `vendor_coordinator` cannot invoke compliance tools).
- **Policy 4 (Rate Limiting)**: Limits each agent to 20 tool executions per incident cycle to prevent infinite reasoning loops.
- **Policy 5 (P1 Life-Safety Escalation)**: Forces immediate high-priority stakeholder notifications on P1 critical alerts.

### 3. Agent Identity (`backend/governance/identity.py`)
Zero-trust agent identity powered by SPIFFE standards:
- Each agent possesses a canonical SPIFFE ID: `spiffe://archon.campus/agent/{agent_name}`.
- Generates short-lived cryptographic JWT tokens carrying claims: `agent_id`, `domain`, `allowed_tools`, and timestamp windows.
- Every tool validates the caller token signature and verifies domain permissions before executing backend operations.

### 4. Agent Registry (`backend/governance/registry.py`)
The centralized agent catalog backed by Firestore:
- Self-registration on boot with semantic versioning (`1.0.0`), operational capabilities, and available tools.
- Heartbeat tracking with automated health transitions: Active -> Degraded (3 missed intervals) -> Offline (10 missed intervals).
- Dynamic Playbook Discovery: Matches incident categories to specific multi-agent orchestration sequences.

### 5. Memory Bank (`backend/services/memory_service.py`)
Institutional memory retention utilizing Google Vertex AI Memory Bank:
- Stores structured knowledge items: incident lessons learned, equipment quirks, structural vulnerabilities, and vendor performance history.
- Contextual search retrieves precedents during incident triage, preventing recurring campus issues from being treated as isolated anomalies.
- Automatic fallback to persistent Firestore-backed memory for offline testing and local development.

### 6. Agent Observability (`backend/governance/observability.py`)
Full visibility into distributed agent reasoning:
- Generates OpenTelemetry-compatible traces and hierarchical spans (Root -> Sub-agent -> Tool Call).
- Records decision rationale, timestamps, input parameters, and results in an immutable Firestore audit log.
- Provides reasoning chain reconstruction for compliance reviews, insurance claims, and post-incident retrospectives.

### 7. Agent Resilience (`backend/governance/resilience.py`)
Deterministic safety mechanisms:
- Handles 429/503 model exceptions with exponential backoff and explicit "NO ACTION TAKEN" fail-safe responses.
- Detects agent looping (3+ identical tool invocations) and halts execution safely.
- Enforces strict 60-second timeouts on tool calls.

---

## Data Flow: The Cascading Incident Pipeline

1. **Signal Intake**: Ingests IoT alerts, vendor emails, operator logs, or regulatory notifications.
2. **Quarantine & Screening**: Model Armor cleans PII and screens for injection patterns.
3. **Gateway Verification**: The Gateway authenticates the source, validates the agent SPIFFE identity, and checks rate limits.
4. **Triage & Orchestration**: `incident_commander` classifies severity (P1-P4), searches Memory Bank for precedent, selects the playbook, and transfers execution to specialist sub-agents.
5. **Specialist Execution**:
   - `impact_assessor` maps building system interdependencies.
   - `vendor_coordinator` ranks vendors and issues dispatches (subject to $10k financial threshold check).
   - `compliance_inspector` evaluates regulatory exposure.
   - `communications_officer` dispatches tailored stakeholder updates.
   - `remediation_tracker` creates actionable follow-up work orders.
   - `memory_curator` synthesizes lessons learned into permanent memory.
6. **Live Observability Stream**: Every span and decision is broadcast via WebSockets to the Next.js Operations Dashboard in real time.

---

## Tech Stack & Ecosystem

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **Development Environment** | **Gemini Antigravity** | Advanced Agentic Coding & Pair Programming IDE |
| **Agent Framework** | Google ADK 2.6.2+ | Multi-agent coordination, `transfer_to_agent`, lifecycle callbacks |
| **LLM Reasoning Engine** | Gemini 2.5/3.5 Flash | Real-time triage, classification, and operational reasoning |
| **Cloud Database** | Google Cloud Firestore | Live persistent collections, state ledger, and audit logs |
| **Backend Compute** | Render / Cloud Run | FastAPI REST & high-throughput WebSocket server |
| **Frontend Delivery** | Vercel / Next.js 14 | Command center dashboard with glassmorphism UI |
| **Security & Policy** | PyJWT & SPIFFE | Zero-trust agent authentication and Model Armor firewall |
| **Observability** | OpenTelemetry | Distributed trace spans and reasoning chains |

