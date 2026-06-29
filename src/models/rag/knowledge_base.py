import json
from pathlib import Path
from typing import List, Dict, Any


class KnowledgeBase:
    def __init__(self, kb_path: str = "data/processed/knowledge_base.json"):
        self.kb_path = Path(kb_path)
        self.entries = []
        self._load()

    def _load(self):
        if self.kb_path.exists():
            with open(self.kb_path) as f:
                self.entries = json.load(f)

    def get_all(self) -> List[Dict[str, Any]]:
        return self.entries

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [e for e in self.entries if e.get("category") == category]

    def search(self, query: str) -> List[Dict[str, Any]]:
        query = query.lower()
        results = []
        for entry in self.entries:
            text = f"{entry.get('title', '')} {entry.get('content', '')}".lower()
            if query in text:
                results.append(entry)
        return results

    def add_entry(self, entry: Dict[str, Any]):
        self.entries.append(entry)
        self._save()

    def _save(self):
        self.kb_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.kb_path, "w") as f:
            json.dump(self.entries, f, indent=2)
