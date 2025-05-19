import numpy as np
import faiss
from typing import List, Dict, Tuple
import json
from pathlib import Path

class SchemaSemanticSearch:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.schema_items: List[Dict] = []
        self.vectors: List[np.ndarray] = []

    def add_schema_item(self, table_name: str, column_name: str, data_type: str, vector: np.ndarray):
        """Add a schema item to the index."""
        self.schema_items.append({
            'table_name': table_name,
            'column_name': column_name,
            'data_type': data_type
        })
        self.vectors.append(vector)
        self.index.add(np.array([vector], dtype=np.float32))

    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict]:
        """Search for similar schema items."""
        distances, indices = self.index.search(np.array([query_vector], dtype=np.float32), k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.schema_items):
                results.append({
                    **self.schema_items[idx],
                    'similarity_score': float(1 / (1 + distances[0][i]))
                })
        return results

    def save(self, path: str):
        """Save the index and schema items to disk."""
        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(save_path / 'schema.index'))
        
        # Save schema items and vectors
        with open(save_path / 'schema_data.json', 'w') as f:
            json.dump({
                'schema_items': self.schema_items,
                'vectors': [v.tolist() for v in self.vectors]
            }, f)

    @classmethod
    def load(cls, path: str) -> 'SchemaSemanticSearch':
        """Load the index and schema items from disk."""
        load_path = Path(path)
        
        # Create new instance
        instance = cls()
        
        # Load FAISS index
        instance.index = faiss.read_index(str(load_path / 'schema.index'))
        
        # Load schema items and vectors
        with open(load_path / 'schema_data.json', 'r') as f:
            data = json.load(f)
            instance.schema_items = data['schema_items']
            instance.vectors = [np.array(v) for v in data['vectors']]
        
        return instance

def get_schema_embeddings(schema_info: Dict) -> List[Tuple[str, str, str, np.ndarray]]:
    """
    Generate embeddings for schema items.
    In a real implementation, this would use a proper embedding model.
    For now, we'll use a simple random vector as a placeholder.
    """
    embeddings = []
    for table_name, info in schema_info.items():
        for column_name, data_type in info['types'].items():
            # Generate a random vector as a placeholder
            # In production, replace this with actual embeddings from a model
            vector = np.random.randn(768).astype(np.float32)
            vector = vector / np.linalg.norm(vector)  # Normalize
            embeddings.append((table_name, column_name, data_type, vector))
    return embeddings 