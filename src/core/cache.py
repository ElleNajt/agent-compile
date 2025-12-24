#!/usr/bin/env python3
"""Caching for compilation results."""

import hashlib
import json
from pathlib import Path
from typing import Optional

from .module import Module


class AmbiguityCache:
    """Cache ambiguity check results to avoid redundant checks."""
    
    def __init__(self, cache_dir: Path):
        """
        Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = cache_dir / ".ambiguity_cache.json"
        self.cache = self._load_cache()
    
    def _load_cache(self) -> dict:
        """Load cache from disk."""
        if self.cache_file.exists():
            return json.loads(self.cache_file.read_text())
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        self.cache_file.write_text(json.dumps(self.cache, indent=2))
    
    def _hash_module(self, module: Module) -> str:
        """
        Compute hash of module spec.
        
        Only includes fields that affect ambiguity checking:
        - name, purpose, dependencies (names only), tests
        """
        spec_dict = {
            "name": module.name,
            "purpose": module.purpose,
            "dependencies": [d.name for d in module.dependencies],
            "tests": [
                {
                    "inputs": test.inputs,
                    "outputs": test.outputs,
                    "description": test.description
                }
                for test in module.tests
            ]
        }
        
        # Convert to stable JSON string and hash
        spec_json = json.dumps(spec_dict, sort_keys=True)
        return hashlib.sha256(spec_json.encode()).hexdigest()
    
    def get(self, module: Module) -> Optional[list]:
        """
        Get cached ambiguity check result.
        
        Returns:
            List of ambiguities if cached, None otherwise
        """
        module_hash = self._hash_module(module)
        cached = self.cache.get(module_hash)
        
        if cached is not None:
            # Return empty list if no ambiguities, or list of ambiguity dicts
            return cached
        
        return None
    
    def set(self, module: Module, ambiguities: list):
        """
        Cache ambiguity check result.
        
        Args:
            module: The module that was checked
            ambiguities: List of Ambiguity objects (will be serialized)
        """
        module_hash = self._hash_module(module)
        
        # Serialize ambiguities to dict format
        serialized = [
            {
                "module_name": amb.module_name,
                "location": amb.location,
                "issue": amb.issue,
                "severity": amb.severity,
                "suggestions": amb.suggestions
            }
            for amb in ambiguities
        ]
        
        self.cache[module_hash] = serialized
        self._save_cache()
