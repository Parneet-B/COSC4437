from typing import List, Optional, Tuple
import threading

TupleType = Tuple[int, str, str, str, str]  # (bug_id, title, priority, status, assigned_to)

class TupleSpace:
    def __init__(self):
        self._tuples: List[TupleType] = []
        self._lock = threading.RLock()
        self._next_id = 1

    def _match(self, tpl: TupleType, template: Tuple[Optional[object], ...]) -> bool:
        return all(t is None or t == v for t, v in zip(template, tpl))

    def out(self, tpl: TupleType) -> None:
        with self._lock:
            self._tuples.append(tpl)
            self._next_id = max(self._next_id, tpl[0] + 1)

    def rd(self, template: Tuple[Optional[object], ...]) -> Optional[TupleType]:
        with self._lock:
            for t in self._tuples:
                if self._match(t, template):
                    return t
        return None

    def inp(self, template: Tuple[Optional[object], ...]) -> Optional[TupleType]:
        with self._lock:
            for i, t in enumerate(self._tuples):
                if self._match(t, template):
                    return self._tuples.pop(i)
        return None

    def new_bug_id(self) -> int:
        with self._lock:
            bid = self._next_id
            self._next_id += 1
            return bid

    def list_all(self) -> List[TupleType]:
        with self._lock:
            return list(self._tuples)

    def pick_specific(self, bug_id: int, dev: str) -> Optional[TupleType]:
        with self._lock:
            for i, (bid, title, prio, status, assigned) in enumerate(self._tuples):
                if bid == bug_id and status == "Open" and assigned == "Unassigned":
                    updated = (bid, title, prio, "In Progress", dev)
                    self._tuples[i] = updated
                    return updated
        return None

    def update_status(self, bug_id: int, dev: str, new_status: str) -> Optional[TupleType]:
        allowed = {"Open", "In Progress", "Resolved"}
        if new_status not in allowed:
            return None
        with self._lock:
            for i, (bid, title, prio, status, assigned) in enumerate(self._tuples):
                if bid == bug_id:
                    if new_status == "Open":
                        updated = (bid, title, prio, "Open", "Unassigned")
                        self._tuples[i] = updated
                        return updated
                    if assigned == dev:
                        updated = (bid, title, prio, new_status, assigned)
                        self._tuples[i] = updated
                        return updated
        return None
