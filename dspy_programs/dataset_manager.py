import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict, is_dataclass

@dataclass
class DatasetMetadata:
    version: str
    created_at: str
    last_modified: str
    size: int
    description: str
    source: str

class DatasetManager:
    def __init__(self, filename: str):
        self.filename = filename
        self.metadata = None
        self.data = []
        self._load()

    def _load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.metadata = DatasetMetadata(**data['metadata'])
                self.data = data['dataset']
        else:
            self._create_new_dataset()

    def _create_new_dataset(self):
        self.metadata = DatasetMetadata(
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            size=0,
            description="Initial dataset",
            source="active_learning"
        )
        self.data = []
        self._save()

    def _save(self):
        self.metadata.last_modified = datetime.now().isoformat()
        self.metadata.size = len(self.data)
        
        with open(self.filename, 'w') as f:
            json.dump({
                'metadata': asdict(self.metadata),
                'dataset': self.data
            }, f, indent=2)

    def add_examples(self, examples: List[Any]):
        for example in examples:
            if is_dataclass(example):
                self.data.append(asdict(example))
            else:
                self.data.append(example)
        self._save()

    def get_all_examples(self) -> List[Any]:
        return self.data

    def get_examples_by_source(self, source: str) -> List[Any]:
        return [ex for ex in self.data if ex.get('source') == source]

    def get_dataset_stats(self) -> Dict[str, Any]:
        scores = [ex['score'] for ex in self.data if 'score' in ex]
        return {
            'size': len(self.data),
            'avg_score': sum(scores) / len(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'max_score': max(scores) if scores else 0,
            'sources': set(ex.get('source', 'unknown') for ex in self.data)
        }

    def create_version(self, description: str):
        version_hash = hashlib.sha256(json.dumps(self.data).encode()).hexdigest()[:8]
        self.metadata.version = f"{self.metadata.version}.{version_hash}"
        self.metadata.description = description
        self._save()

    def merge_dataset(self, other_filename: str):
        other_manager = DatasetManager(other_filename)
        self.data.extend(other_manager.data)
        self._save()
