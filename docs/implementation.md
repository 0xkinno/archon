# ARCHON Implementation Decisions & Technical Rationale

## 1. Guardrail Placement: Tool Boundary vs Model Boundary
- **Decision**: Implemented Model Armor in `after_tool_callback` and Agent Gateway in `before_tool_callback`.
- **Rationale**: Intercepting data at the tool boundary ensures that malicious content from external sources (such as vendor emails or IoT payloads) is quarantined before any downstream tool executes. Screening at the model boundary is unable to distinguish between user intent and agent reasoning context.

## 2. Callback Context Keyword Requirement in Google ADK
- **Decision**: All ADK callback signatures explicitly name the context parameter `callback_context`.
- **Rationale**: Google ADK invokes callbacks using explicit keyword arguments. Omitting or renaming this parameter causes runtime keyword dispatch errors during execution turns.

## 3. Universal Sub-Agent Callback Attachment
- **Decision**: Attached `after_agent_callback` and `before_tool_callback` to every sub-agent, not just the root orchestrator.
- **Rationale**: In ADK multi-agent handoffs via `transfer_to_agent`, the delegating agent turn terminates immediately. If callbacks exist only on the root agent, intermediate agent operations would escape memory logging and policy governance.

## 4. Multi-Tier Storage Strategy with In-Memory Dev Fallback
- **Decision**: Developed `FirestoreService` and `ArchonMemoryService` to seamlessly toggle between live Google Cloud APIs and robust in-memory datastores based on environment credentials.
- **Rationale**: Guarantees zero-dependency offline test execution for CI/CD and local development while remaining 100% production-ready for Google Cloud deployment.
