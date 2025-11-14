"""
One-time setup script
Creates all necessary folders and files
Run: python setup_folders.py
"""

import os
import json
from datetime import datetime

def setup_folders():
    """Create all necessary folders"""
    
    folders = [
        'models',
        'models/versions',
        'models/v1.0',
        'models/v1.1',
        'utils',
        'monitoring',
        'logs',
        'cache',
        'backups'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created folder: {folder}")
    
    # Create .gitkeep files
    gitkeep_folders = ['models', 'models/versions', 'logs', 'cache']
    for folder in gitkeep_folders:
        gitkeep = os.path.join(folder, '.gitkeep')
        with open(gitkeep, 'w') as f:
            f.write(f"# Keep {folder}/ directory in git\n")
        print(f"✅ Created .gitkeep: {gitkeep}")
    
    # Create initial metadata.json
    metadata = {
        "models": [],
        "last_updated": datetime.now().isoformat(),
        "version": "1.0",
        "description": "Model versioning metadata for DEMIR AI"
    }
    
    metadata_path = 'models/versions/metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✅ Created metadata: {metadata_path}")
    
    # Create README
    readme_path = 'models/README.md'
    with open(readme_path, 'w') as f:
        f.write("""# DEMIR AI - Model Storage

This directory stores all ML models.

See setup documentation for details.
""")
    print(f"✅ Created README: {readme_path}")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run: git add .")
    print("2. Run: git commit -m 'Setup: Created folder structure'")
    print("3. Run: git push origin main")

if __name__ == "__main__":
    setup_folders()
