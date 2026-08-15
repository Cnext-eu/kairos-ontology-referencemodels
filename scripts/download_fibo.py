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
FIBO_DIR = BASE_DIR / "kairos_ontology_referencemodels" / "ontology-reference-models" / "authoritative-ontologies" / "FIBO"
TARGET_DIR = FIBO_DIR / "current"
ARCHIVE_DIR = FIBO_DIR / "archive"

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
    
STABLE_FIBO_FOLDER = "fibo"


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

    # Rename the version-specific top-level folder to a stable name so that
    # catalog-v001.xml paths remain valid across FIBO upgrades.
    _rename_to_stable_folder(extract_to)

    return len(ontology_files)


def _rename_to_stable_folder(extract_to):
    """Rename the extracted top-level folder (e.g. edmcouncil-fibo-574a831) to a stable name."""
    extract_path = Path(extract_to)
    stable_path = extract_path / STABLE_FIBO_FOLDER

    # Find the version-specific folder (the only directory that isn't our stable name)
    candidates = [
        d for d in extract_path.iterdir()
        if d.is_dir() and d.name != STABLE_FIBO_FOLDER
    ]

    if len(candidates) == 1:
        source = candidates[0]
        if stable_path.exists():
            shutil.rmtree(stable_path)
        source.rename(stable_path)
        print(f"Renamed {source.name}/ → {STABLE_FIBO_FOLDER}/")
    elif not stable_path.exists():
        print("Warning: Could not identify extracted folder to rename.")

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


def archive_current(target_dir, archive_dir):
    """Archive the current FIBO version before downloading a new one."""
    metadata_file = target_dir / "METADATA.txt"
    if not metadata_file.is_file():
        print("No existing FIBO to archive (fresh install).")
        return

    # Read old version from METADATA.txt
    old_version = None
    with open(metadata_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith("version:"):
                old_version = line.split(":", 1)[1].strip()
                break

    if not old_version:
        print("Warning: Could not determine old version, skipping archive.")
        return

    archive_dest = archive_dir / old_version
    if archive_dest.is_dir():
        print(f"Archive for {old_version} already exists, skipping.")
        return

    print(f"Archiving current FIBO ({old_version}) → archive/{old_version}/")
    archive_dest.mkdir(parents=True, exist_ok=True)

    for item in target_dir.iterdir():
        dest = archive_dest / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # Clear current/ for fresh download
    for item in target_dir.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    print(f"Archived and cleared current/ for new download.")

def main():
    """Main download process."""
    try:
        # Ensure directories exist
        FIBO_DIR.mkdir(parents=True, exist_ok=True)
        TARGET_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Target directory: {TARGET_DIR}")
        
        # Get latest release info
        release_info = get_latest_release()
        version = release_info.get("tag_name", "unknown")
        print(f"\nLatest FIBO version: {version}")
        print(f"Release name: {release_info.get('name', 'N/A')}")
        
        # Archive existing version before downloading new one
        archive_current(TARGET_DIR, ARCHIVE_DIR)
        
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
