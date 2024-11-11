import os
import joblib
import json
from datetime import datetime
from typing import Dict, Optional, Tuple, List

class ModelPersistence:
    def __init__(self, storage_dir: str = "saved_models"):
        """Initialize model storage"""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
    def save_model(self, model_name: str, mapper, metadata: Optional[Dict] = None) -> str:
        """Save model and metadata to disk"""
        # Create timestamps
        timestamp = datetime.now().isoformat()
        
        # Prepare metadata
        full_metadata = {
            "model_name": model_name,
            "created_at": timestamp,
            "last_updated": timestamp,
            "standard_template": mapper.standard_template,
            "training_examples": len(mapper.training_mappings) if hasattr(mapper, 'training_mappings') else 0
        }
        if metadata:
            full_metadata.update(metadata)
            
        # Save model
        model_path = os.path.join(self.storage_dir, f"{model_name}.joblib")
        metadata_path = os.path.join(self.storage_dir, f"{model_name}_metadata.json")
        
        joblib.dump(mapper, model_path)
        with open(metadata_path, 'w') as f:
            json.dump(full_metadata, f)
            
        return model_name
    
    def load_model(self, model_name: str) -> Tuple[object, Dict]:
        """Load model and metadata from disk"""
        model_path = os.path.join(self.storage_dir, f"{model_name}.joblib")
        metadata_path = os.path.join(self.storage_dir, f"{model_name}_metadata.json")
        
        if not (os.path.exists(model_path) and os.path.exists(metadata_path)):
            raise FileNotFoundError(f"Model '{model_name}' not found")
            
        mapper = joblib.load(model_path)
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
            
        return mapper, metadata
    
    def list_models(self) -> List[Dict]:
        """List all saved models"""
        models = []
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('_metadata.json'):
                with open(os.path.join(self.storage_dir, filename), 'r') as f:
                    metadata = json.load(f)
                    models.append(metadata)
        return models
    
    def delete_model(self, model_name: str) -> bool:
        """Delete a saved model"""
        model_path = os.path.join(self.storage_dir, f"{model_name}.joblib")
        metadata_path = os.path.join(self.storage_dir, f"{model_name}_metadata.json")
        
        if os.path.exists(model_path):
            os.remove(model_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            
        return True