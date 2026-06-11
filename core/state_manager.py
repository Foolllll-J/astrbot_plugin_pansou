import time
from math import ceil

STATE_TTL = 1800


class SearchState:
    def __init__(self, keyword: str, results: list[dict], per_page: int = 5):
        self.keyword = keyword
        self.results = results
        self.page = 1
        self.per_page = per_page
        self.cloud_type = None
        self.check_map: dict[str, str] = {}
        self.timestamp = time.time()

    @property
    def total_pages(self) -> int:
        return max(1, ceil(len(self.filtered_results) / self.per_page))

    @property
    def filtered_results(self) -> list[dict]:
        if not self.cloud_type:
            return self.results
        filtered = []
        for r in self.results:
            links = r.get("links", [])
            if any(l.get("type") == self.cloud_type for l in links):
                filtered.append(r)
        return filtered

    def is_expired(self) -> bool:
        return time.time() - self.timestamp > STATE_TTL


class StateManager:
    def __init__(self):
        self._states: dict[str, SearchState] = {}

    def save(self, user_id: str, state: SearchState):
        self._cleanup()
        self._states[user_id] = state

    def get(self, user_id: str) -> SearchState | None:
        self._cleanup()
        state = self._states.get(user_id)
        if state and state.is_expired():
            del self._states[user_id]
            return None
        return state

    def clear(self, user_id: str):
        self._states.pop(user_id, None)

    def _cleanup(self):
        now = time.time()
        expired = [uid for uid, s in self._states.items() if now - s.timestamp > STATE_TTL]
        for uid in expired:
            del self._states[uid]
