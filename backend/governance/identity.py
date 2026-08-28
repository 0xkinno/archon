import time
import jwt
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from config import settings
from models.agent_models import AgentIdentityModel
from .gateway import DOMAIN_TOOL_REGISTRY

logger = logging.getLogger("archon.identity")


class AgentIdentityManager:
    """Zero-trust SPIFFE-compatible identity and cryptographic token issuance system."""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_seconds = settings.JWT_EXPIRATION_SECONDS

    def create_agent_identity(self, agent_name: str, domain: str, allowed_tools: Optional[List[str]] = None) -> AgentIdentityModel:
        """Constructs a canonical SPIFFE identity model for a specialist agent."""
        spiffe_id = f"spiffe://archon.campus/agent/{agent_name}"
        tools = allowed_tools or DOMAIN_TOOL_REGISTRY.get(domain, [])
        now = datetime.utcnow()
        expires = now + timedelta(seconds=self.expiration_seconds)

        return AgentIdentityModel(
            agent_id=spiffe_id,
            agent_name=agent_name,
            domain=domain,
            allowed_tools=tools,
            spiffe_id=spiffe_id,
            issued_at=now,
            expires_at=expires,
        )

    def issue_token(self, identity: AgentIdentityModel) -> str:
        """Issues a signed JWT token containing scoped agent claims."""
        now_ts = int(time.time())
        exp_ts = now_ts + self.expiration_seconds
        payload = {
            "sub": identity.spiffe_id,
            "agent_name": identity.agent_name,
            "domain": identity.domain,
            "allowed_tools": identity.allowed_tools,
            "iat": now_ts,
            "exp": exp_ts,
            "iss": "archon-identity-authority",
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token

    def validate_token(self, token: str) -> Optional[AgentIdentityModel]:
        """Validates cryptographic signature, expiry, and decodes claims."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], issuer="archon-identity-authority")
            return AgentIdentityModel(
                agent_id=payload["sub"],
                agent_name=payload["agent_name"],
                domain=payload["domain"],
                allowed_tools=payload.get("allowed_tools", []),
                spiffe_id=payload["sub"],
                issued_at=datetime.fromtimestamp(payload["iat"]),
                expires_at=datetime.fromtimestamp(payload["exp"]),
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Agent identity token signature expired")
            return None
        except Exception as e:
            logger.error(f"Agent identity token validation failed: {e}")
            return None

    def check_tool_authorization(self, token: str, tool_name: str) -> bool:
        """Verifies if the token bearer is cryptographically authorized to execute the tool."""
        identity = self.validate_token(token)
        if not identity:
            return False
        return tool_name in identity.allowed_tools or identity.domain == "orchestration"


identity_manager = AgentIdentityManager()
