"""
Download latest FIBO ontologies from EDM Council GitHub repository.
Places files in the Authoritative Ontologies folder.
"""

import os
import requests
import zipfile
import shutil
from pathlib import Path
from datetime import datetime

# Configuration
FIBO_GITHUB_API = "https://api.github.com/repos/edmcouncil/fibo/releases/latest"
BASE_DIR = Path(__file__).parent.parent
TARGET_DIR = BASE_DIR / "ontology-reference-models" / "Authoritative Ontologies" / "FIBO"

def get_latest_release():
    """Get the latest FIBO release information from GitHub."""
    print("Fetching latest FIBO release information...")
    response = requests.get(FIBO_GITHUB_API)
    response.raise_for_status()
    return response.json()

def download_file(url, dest_path):
    """Download a file with progress indication."""
    print(f"Downloading from {url}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(dest_path, 'wb') as f:
        if total_size == 0:
            f.write(response.content)
        else:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                percent = (downloaded / total_size) * 100
                print(f"\rProgress: {percent:.1f}%", end='')
    print()  # New line after progress
    
def extract_ontologies(zip_path, extract_to):
    """Extract RDF/TTL/OWL files from the zip archive."""
    print(f"Extracting ontologies to {extract_to}...")
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Get all ontology files
        ontology_extensions = ('.rdf', '.ttl', '.owl', '.n3', '.jsonld')
        ontology_files = [f for f in zip_ref.namelist() 
                         if f.lower().endswith(ontology_extensions)]
        
        print(f"Found {len(ontology_files)} ontology files")
        
        for file in ontology_files:
            # Extract preserving directory structure
            zip_ref.extract(file, extract_to)
    
    print(f"Extracted {len(ontology_files)} files")
    return len(ontology_files)

def create_metadata(target_dir, release_info):
    """Create metadata file with download information."""
    metadata = {
        "source": "FIBO - Financial Industry Business Ontology",
        "publisher": "EDM Council",
        "download_date": datetime.now().isoformat(),
        "version": release_info.get("tag_name", "unknown"),
        "release_name": release_info.get("name", ""),
        "release_url": release_info.get("html_url", ""),
        "license": "MIT License",
        "homepage": "https://spec.edmcouncil.org/fibo/"
    }
    
    metadata_file = target_dir / "METADATA.txt"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        f.write("FIBO Ontologies - Download Information\n")
        f.write("=" * 50 + "\n\n")
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    print(f"Created metadata file: {metadata_file}")

def main():
    """Main download process."""
    try:
        # Create target directory
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Target directory: {TARGET_DIR}")
        
        # Get latest release info
        release_info = get_latest_release()
        version = release_info.get("tag_name", "unknown")
        print(f"\nLatest FIBO version: {version}")
        print(f"Release name: {release_info.get('name', 'N/A')}")
        
        # Find the zipball/tarball download URL
        # FIBO typically has assets, but we can use the source code download
        zipball_url = release_info.get("zipball_url")
        
        if not zipball_url:
            print("Warning: No zipball URL found, checking assets...")
            assets = release_info.get("assets", [])
            for asset in assets:
                if asset.get("name", "").lower().endswith(".zip"):
                    zipball_url = asset.get("browser_download_url")
                    break
        
        if not zipball_url:
            zipball_url = release_info.get("zipball_url")
            
        if not zipball_url:
            raise Exception("Could not find download URL for FIBO release")
        
        # Download the release
        temp_zip = TARGET_DIR / f"fibo_{version}.zip"
        download_file(zipball_url, temp_zip)
        
        # Extract ontologies
        file_count = extract_ontologies(temp_zip, TARGET_DIR)
        
        # Create metadata
        create_metadata(TARGET_DIR, release_info)
        
        # Cleanup temp file
        temp_zip.unlink()
        print(f"\nCleaned up temporary files")
        
        print(f"\n[OK] Successfully downloaded FIBO {version}")
        print(f"[OK] {file_count} ontology files extracted")
        print(f"[OK] Location: {TARGET_DIR}")
        
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Error downloading FIBO: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
