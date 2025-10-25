"""
Automated Dataset Versioning and Provenance Tracker
Tracks dataset versions, transformations, lineage, and metadata
"""

import hashlib
import json
import os
import shutil
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np


class DatasetVersion:
    """Represents a single version of a dataset"""
    
    def __init__(self, version_id: str, parent_id: Optional[str], metadata: Dict):
        self.version_id = version_id
        self.parent_id = parent_id
        self.metadata = metadata
        self.timestamp = datetime.now().isoformat()
        self.children = []
    
    def to_dict(self) -> Dict:
        return {
            'version_id': self.version_id,
            'parent_id': self.parent_id,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'children': self.children
        }


class DatasetProvenanceTracker:
    """
    Automated dataset versioning and provenance tracking system
    """
    
    def __init__(self, base_path: str = "./dataset_versions"):
        self.base_path = Path(base_path)
        self.versions_path = self.base_path / "versions"
        self.metadata_path = self.base_path / "metadata"
        self.provenance_file = self.base_path / "provenance.json"
        
        # Create directory structure
        self.base_path.mkdir(exist_ok=True)
        self.versions_path.mkdir(exist_ok=True)
        self.metadata_path.mkdir(exist_ok=True)
        
        # Load or initialize provenance graph
        self.provenance = self._load_provenance()
        self.current_version = None
    
    def _load_provenance(self) -> Dict:
        """Load provenance graph from disk"""
        if self.provenance_file.exists():
            with open(self.provenance_file, 'r') as f:
                return json.load(f)
        return {'versions': {}, 'lineage': {}}
    
    def _save_provenance(self):
        """Save provenance graph to disk"""
        with open(self.provenance_file, 'w') as f:
            json.dump(self.provenance, f, indent=2)
    
    def _compute_hash(self, data: Union[pd.DataFrame, np.ndarray, str]) -> str:
        """Compute hash of dataset for versioning"""
        if isinstance(data, pd.DataFrame):
            # Hash DataFrame content
            return hashlib.sha256(
                pd.util.hash_pandas_object(data, index=True).values
            ).hexdigest()[:16]
        elif isinstance(data, np.ndarray):
            # Hash numpy array
            return hashlib.sha256(data.tobytes()).hexdigest()[:16]
        elif isinstance(data, str) and os.path.isfile(data):
            # Hash file content
            with open(data, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        else:
            # Hash serialized object
            return hashlib.sha256(str(data).encode()).hexdigest()[:16]
    
    def _get_data_stats(self, data: Union[pd.DataFrame, np.ndarray]) -> Dict:
        """Extract statistics from data"""
        stats = {}
        
        if isinstance(data, pd.DataFrame):
            stats = {
                'type': 'DataFrame',
                'shape': data.shape,
                'columns': list(data.columns),
                'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'memory_usage': data.memory_usage(deep=True).sum(),
                'null_counts': data.isnull().sum().to_dict(),
                'numeric_summary': data.describe().to_dict() if len(data.select_dtypes(include=[np.number]).columns) > 0 else {}
            }
        elif isinstance(data, np.ndarray):
            stats = {
                'type': 'ndarray',
                'shape': data.shape,
                'dtype': str(data.dtype),
                'memory_usage': data.nbytes,
                'min': float(data.min()) if np.issubdtype(data.dtype, np.number) else None,
                'max': float(data.max()) if np.issubdtype(data.dtype, np.number) else None,
                'mean': float(data.mean()) if np.issubdtype(data.dtype, np.number) else None
            }
        
        return stats
    
    def create_version(self, 
                      data: Union[pd.DataFrame, np.ndarray, str],
                      name: str,
                      description: str = "",
                      tags: List[str] = None,
                      parent_version: Optional[str] = None,
                      transformation: Optional[Dict] = None,
                      custom_metadata: Dict = None) -> str:
        """
        Create a new dataset version
        
        Args:
            data: Dataset (DataFrame, array, or file path)
            name: Version name
            description: Version description
            tags: List of tags for categorization
            parent_version: Parent version ID (for lineage)
            transformation: Dict describing transformation applied
            custom_metadata: Additional custom metadata
        
        Returns:
            version_id: Unique version identifier
        """
        # Compute hash and create version ID
        data_hash = self._compute_hash(data)
        version_id = f"v_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{data_hash}"
        
        # Check if version already exists
        if version_id in self.provenance['versions']:
            print(f"⚠️  Version {version_id} already exists")
            return version_id
        
        # Gather metadata
        metadata = {
            'name': name,
            'description': description,
            'tags': tags or [],
            'hash': data_hash,
            'timestamp': datetime.now().isoformat(),
            'stats': self._get_data_stats(data) if not isinstance(data, str) else {},
            'transformation': transformation or {},
            'custom': custom_metadata or {}
        }
        
        # Save dataset
        version_path = self.versions_path / version_id
        version_path.mkdir(exist_ok=True)
        
        if isinstance(data, pd.DataFrame):
            data.to_parquet(version_path / "data.parquet")
        elif isinstance(data, np.ndarray):
            np.save(version_path / "data.npy", data)
        elif isinstance(data, str) and os.path.isfile(data):
            shutil.copy2(data, version_path / Path(data).name)
        else:
            with open(version_path / "data.pkl", 'wb') as f:
                pickle.dump(data, f)
        
        # Update provenance
        self.provenance['versions'][version_id] = {
            'metadata': metadata,
            'parent': parent_version,
            'children': []
        }
        
        # Update lineage
        if parent_version:
            if parent_version in self.provenance['versions']:
                self.provenance['versions'][parent_version]['children'].append(version_id)
            self.provenance['lineage'][version_id] = self._build_lineage(parent_version) + [version_id]
        else:
            self.provenance['lineage'][version_id] = [version_id]
        
        # Save metadata
        metadata_file = self.metadata_path / f"{version_id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self._save_provenance()
        self.current_version = version_id
        
        print(f"✓ Created version: {version_id}")
        print(f"  Name: {name}")
        print(f"  Parent: {parent_version or 'None (root)'}")
        
        return version_id
    
    def load_version(self, version_id: str) -> Union[pd.DataFrame, np.ndarray, Any]:
        """Load a specific dataset version"""
        if version_id not in self.provenance['versions']:
            raise ValueError(f"Version {version_id} not found")
        
        version_path = self.versions_path / version_id
        
        # Try different file types
        if (version_path / "data.parquet").exists():
            return pd.read_parquet(version_path / "data.parquet")
        elif (version_path / "data.npy").exists():
            return np.load(version_path / "data.npy")
        elif (version_path / "data.pkl").exists():
            with open(version_path / "data.pkl", 'rb') as f:
                return pickle.load(f)
        else:
            # Return first file found
            files = list(version_path.glob("*"))
            if files:
                return str(files[0])
        
        raise FileNotFoundError(f"No data found for version {version_id}")
    
    def get_metadata(self, version_id: str) -> Dict:
        """Get metadata for a specific version"""
        if version_id not in self.provenance['versions']:
            raise ValueError(f"Version {version_id} not found")
        
        return self.provenance['versions'][version_id]['metadata']
    
    def _build_lineage(self, version_id: str) -> List[str]:
        """Build lineage path for a version"""
        if version_id not in self.provenance['versions']:
            return []
        
        parent = self.provenance['versions'][version_id]['parent']
        if parent:
            return self._build_lineage(parent) + [version_id]
        return [version_id]
    
    def get_lineage(self, version_id: str) -> List[str]:
        """Get complete lineage for a version"""
        if version_id not in self.provenance['lineage']:
            raise ValueError(f"Version {version_id} not found")
        
        return self.provenance['lineage'][version_id]
    
    def get_children(self, version_id: str) -> List[str]:
        """Get direct children of a version"""
        if version_id not in self.provenance['versions']:
            raise ValueError(f"Version {version_id} not found")
        
        return self.provenance['versions'][version_id]['children']
    
    def list_versions(self, tags: Optional[List[str]] = None) -> List[Dict]:
        """List all versions, optionally filtered by tags"""
        versions = []
        
        for vid, vdata in self.provenance['versions'].items():
            metadata = vdata['metadata']
            
            # Filter by tags if specified
            if tags:
                if not any(tag in metadata['tags'] for tag in tags):
                    continue
            
            versions.append({
                'version_id': vid,
                'name': metadata['name'],
                'description': metadata['description'],
                'timestamp': metadata['timestamp'],
                'tags': metadata['tags'],
                'parent': vdata['parent']
            })
        
        # Sort by timestamp
        versions.sort(key=lambda x: x['timestamp'], reverse=True)
        return versions
    
    def compare_versions(self, version1: str, version2: str) -> Dict:
        """Compare two versions"""
        if version1 not in self.provenance['versions']:
            raise ValueError(f"Version {version1} not found")
        if version2 not in self.provenance['versions']:
            raise ValueError(f"Version {version2} not found")
        
        meta1 = self.get_metadata(version1)
        meta2 = self.get_metadata(version2)
        
        comparison = {
            'version1': version1,
            'version2': version2,
            'timestamp_diff': meta2['timestamp'],
            'hash_match': meta1['hash'] == meta2['hash'],
            'stats_diff': {}
        }
        
        # Compare stats if available
        if 'stats' in meta1 and 'stats' in meta2:
            stats1 = meta1['stats']
            stats2 = meta2['stats']
            
            if 'shape' in stats1 and 'shape' in stats2:
                comparison['stats_diff']['shape'] = {
                    'before': stats1['shape'],
                    'after': stats2['shape']
                }
        
        return comparison
    
    def visualize_lineage(self, version_id: str):
        """Print ASCII visualization of lineage"""
        lineage = self.get_lineage(version_id)
        
        print(f"\n{'='*80}")
        print(f"LINEAGE FOR: {version_id}")
        print(f"{'='*80}\n")
        
        for i, vid in enumerate(lineage):
            metadata = self.get_metadata(vid)
            indent = "  " * i
            connector = "└─ " if i > 0 else ""
            
            print(f"{indent}{connector}{vid}")
            print(f"{indent}   Name: {metadata['name']}")
            print(f"{indent}   Time: {metadata['timestamp']}")
            if metadata['transformation']:
                print(f"{indent}   Transform: {metadata['transformation'].get('operation', 'N/A')}")
            print()
    
    def rollback(self, version_id: str) -> Union[pd.DataFrame, np.ndarray, Any]:
        """Rollback to a specific version"""
        print(f"🔄 Rolling back to version: {version_id}")
        data = self.load_version(version_id)
        self.current_version = version_id
        return data
    
    def tag_version(self, version_id: str, tags: List[str]):
        """Add tags to a version"""
        if version_id not in self.provenance['versions']:
            raise ValueError(f"Version {version_id} not found")
        
        current_tags = self.provenance['versions'][version_id]['metadata']['tags']
        self.provenance['versions'][version_id]['metadata']['tags'] = list(set(current_tags + tags))
        self._save_provenance()
        
        print(f"✓ Added tags to {version_id}: {tags}")
    
    def export_provenance(self, filename: str = "provenance_graph.json"):
        """Export provenance graph"""
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'total_versions': len(self.provenance['versions']),
            'provenance': self.provenance
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✓ Provenance exported to {filename}")


def demo():
    """Demonstration of the dataset versioning system"""
    
    # Initialize tracker
    tracker = DatasetProvenanceTracker("./demo_versions")
    
    print("="*80)
    print("DATASET VERSIONING & PROVENANCE TRACKER - DEMO")
    print("="*80)
    
    # Create initial dataset
    print("\n1. Creating initial dataset...")
    df1 = pd.DataFrame({
        'id': range(1, 101),
        'value': np.random.randn(100),
        'category': np.random.choice(['A', 'B', 'C'], 100)
    })
    
    v1 = tracker.create_version(
        data=df1,
        name="Initial Dataset",
        description="Raw data from source system",
        tags=["raw", "production"]
    )
    
    # Create cleaned version
    print("\n2. Creating cleaned version...")
    df2 = df1.dropna()
    df2 = df2[df2['value'] > -2]
    
    v2 = tracker.create_version(
        data=df2,
        name="Cleaned Dataset",
        description="Removed outliers and missing values",
        tags=["cleaned", "production"],
        parent_version=v1,
        transformation={
            'operation': 'cleaning',
            'steps': ['drop_na', 'filter_outliers'],
            'rows_removed': len(df1) - len(df2)
        }
    )
    
    # Create feature-engineered version
    print("\n3. Creating feature-engineered version...")
    df3 = df2.copy()
    df3['value_squared'] = df3['value'] ** 2
    df3['value_log'] = np.log(np.abs(df3['value']) + 1)
    
    v3 = tracker.create_version(
        data=df3,
        name="Feature Engineered",
        description="Added squared and log features",
        tags=["features", "production"],
        parent_version=v2,
        transformation={
            'operation': 'feature_engineering',
            'features_added': ['value_squared', 'value_log']
        }
    )
    
    # List all versions
    print("\n4. Listing all versions...")
    print("-"*80)
    versions = tracker.list_versions()
    for v in versions:
        print(f"  {v['name']:<25} | {v['version_id']:<20} | {v['timestamp']}")
    
    # Show lineage
    print("\n5. Visualizing lineage...")
    tracker.visualize_lineage(v3)
    
    # Compare versions
    print("\n6. Comparing versions...")
    comparison = tracker.compare_versions(v1, v3)
    print(f"  Hash match: {comparison['hash_match']}")
    print(f"  Shape change: {comparison['stats_diff'].get('shape', {})}")
    
    # Rollback example
    print("\n7. Rolling back to cleaned version...")
    data = tracker.rollback(v2)
    print(f"  Loaded data shape: {data.shape}")
    
    # Export provenance
    print("\n8. Exporting provenance...")
    tracker.export_provenance("demo_provenance.json")
    
    print("\n" + "="*80)
    print("DEMO COMPLETED")
    print("="*80)


if __name__ == "__main__":
    # Install required packages:
    # pip install pandas numpy pyarrow
    
    demo()
    
    # Custom usage example:
    # tracker = DatasetProvenanceTracker("./my_datasets")
    # version_id = tracker.create_version(
    #     data=my_dataframe,
    #     name="My Dataset v1",
    #     description="Initial version",
    #     tags=["experiment", "test"]
    # )
    # data = tracker.load_version(version_id)
