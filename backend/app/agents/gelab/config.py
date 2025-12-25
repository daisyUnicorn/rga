"""
GELab Agent Configuration.

Model parameters optimized for GELab-Zero.
"""

# GELab model configuration (preserved from original)
GELAB_MODEL_CONFIG = {
    "temperature": 0.1,
    "top_p": 0.95,
    "frequency_penalty": 0.0,
    "max_tokens": 4096,
}

# Default maximum steps for GELab agent
GELAB_MAX_STEPS = 60

# Coordinate system: 0-1000 normalized
COORDINATE_MAX = 1000
