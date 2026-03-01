"""
Test and validate the XML catalog configuration.
Checks that all catalog mappings point to existing files.
"""

import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from catalog_utils import CatalogResolver, validate_catalog

def main():
    """Test catalog resolver functionality."""
    
    base_dir = Path(__file__).parent.parent
    catalog_path = base_dir / "catalog-v001.xml"
    
    print("=" * 70)
    print("XML Catalog Validation")
    print("=" * 70)
    print(f"\nCatalog file: {catalog_path}")
    
    if not catalog_path.exists():
        print(f"❌ Catalog file not found: {catalog_path}")
        return 1
    
    # Initialize resolver
    print("\n📚 Loading catalog...")
    try:
        resolver = CatalogResolver(catalog_path)
        print(f"✓ Loaded {len(resolver.get_all_mappings())} URI mappings")
    except Exception as e:
        print(f"❌ Error loading catalog: {e}")
        return 1
    
    # Validate all mappings
    print("\n🔍 Validating catalog mappings...\n")
    validation_results = validate_catalog(catalog_path)
    
    valid_count = 0
    invalid_count = 0
    
    for uri, exists in validation_results.items():
        local_path = resolver.resolve(uri)
        if exists:
            print(f"✓ {uri}")
            print(f"  → {local_path}")
            valid_count += 1
        else:
            print(f"✗ {uri}")
            print(f"  → {local_path} (NOT FOUND)")
            invalid_count += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"✓ Valid mappings:   {valid_count}")
    print(f"✗ Invalid mappings: {invalid_count}")
    
    if invalid_count > 0:
        print("\n⚠️  Some catalog mappings point to non-existent files.")
        print("Run 'python scripts/download_fibo.py' to update FIBO ontologies.")
        return 1
    else:
        print("\n✅ All catalog mappings are valid!")
        return 0

if __name__ == "__main__":
    exit(main())
