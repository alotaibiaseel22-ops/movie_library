from __future__ import annotations
from collections import defaultdict
from typing import Callable, Dict, List, Any

class EventBus:
    _subs: Dict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)

    @classmethod
    def subscribe(cls, event: str, handler: Callable[[Dict[str, Any]], None]):
        cls._subs[event].append(handler)

    @classmethod
    def publish(cls, event: str, payload: Dict[str, Any]):
        for h in cls._subs.get(event, []):
            try:
                h(payload)
            except Exception:
                pass
