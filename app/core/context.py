from typing import Optional
from app.services.orchestrator import SyncOrchestrator


class Context:
    orchestrator: Optional[SyncOrchestrator] = None


context = Context()
