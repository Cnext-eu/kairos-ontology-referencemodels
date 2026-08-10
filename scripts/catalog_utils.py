"""
XML Catalog utilities for resolving FIBO ontology imports.

Provides functions to:
- Parse XML catalog files
- Resolve URIs to local file paths
- Load imported ontologies from local files
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

from rdflib import Graph


class CatalogResolver:
    """Resolves ontology URIs to local files using XML catalog."""
    
    CATALOG_NS = "{urn:oasis:names:tc:entity:xmlns:xml:catalog}"
    
    #: File suffixes tried when a rewritten prefix lands on a document rather than a
    #: directory. FIBO publishes ontology IRIs ending in "/" while the file on disk is
    #: "<name>.rdf" one level up, so the bare rewrite result never exists as-is.
    REWRITE_SUFFIXES = (".rdf", ".ttl", ".owl")

    def __init__(self, catalog_path: Path):
        """
        Initialize resolver with catalog file.

        Args:
            catalog_path: Path to catalog-v001.xml file
        """
        self.catalog_path = catalog_path
        self.mappings: Dict[str, Path] = {}
        #: (uriStartString, rewritePrefix) pairs, longest prefix first (OASIS rule).
        self.rewrites: list[tuple[str, Path]] = []
        self._load_catalog()

    def _load_catalog(self):
        """Parse XML catalog and build URI → local path mappings."""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")

        tree = ET.parse(self.catalog_path)
        root = tree.getroot()
        catalog_dir = self.catalog_path.parent

        # Parse all <uri> elements
        for uri_elem in root.findall(f"{self.CATALOG_NS}uri"):
            uri_name = uri_elem.get("name")
            uri_path = uri_elem.get("uri")

            if uri_name and uri_path:
                # Resolve relative path from catalog directory
                local_path = (catalog_dir / uri_path).resolve()

                # Normalize URI (strip trailing # and / for consistent lookup)
                base_uri = uri_name.rstrip('#').rstrip('/')
                self.mappings[base_uri] = local_path
                self.mappings[base_uri + '/'] = local_path
                self.mappings[base_uri + '#'] = local_path

        # Parse all <rewriteURI> elements. Without these the catalog's only FIBO rule —
        # one prefix rewrite covering 300+ files — is invisible to this resolver, so
        # every FIBO import silently resolves to None while validate_catalog() still
        # reports "all mappings valid" because it only inspects <uri> entries.
        for rw in root.findall(f"{self.CATALOG_NS}rewriteURI"):
            start = rw.get("uriStartString")
            prefix = rw.get("rewritePrefix")
            if start and prefix is not None:
                self.rewrites.append((start, (catalog_dir / prefix).resolve()))
        # Longest uriStartString wins, per the OASIS catalog specification.
        self.rewrites.sort(key=lambda item: len(item[0]), reverse=True)

    def _resolve_rewrite(self, uri: str) -> Optional[Path]:
        """Apply the longest matching ``rewriteURI`` rule, if any."""
        for start, prefix in self.rewrites:
            if not uri.startswith(start):
                continue
            remainder = uri[len(start):]
            candidate = prefix / remainder if remainder else prefix
            if candidate.is_file():
                return candidate
            # FIBO convention: the ontology IRI ends in "/" but the document is a
            # sibling file, e.g. ".../FND/Agreements/Contracts/" -> "Contracts.rdf".
            stem = candidate if remainder else None
            if stem is not None:
                for suffix in self.REWRITE_SUFFIXES:
                    sibling = stem.with_name(stem.name + suffix)
                    if sibling.is_file():
                        return sibling
        return None

    def resolve(self, uri: str) -> Optional[Path]:
        """
        Resolve an ontology URI to a local file path.
        
        Args:
            uri: Ontology URI (e.g., https://spec.edmcouncil.org/fibo/...)
            
        Returns:
            Local file path if mapping exists, None otherwise
        """
        # Try exact match first
        if uri in self.mappings:
            return self.mappings[uri]
        
        # Normalize: strip trailing # and / then try variants
        base_uri = uri.rstrip('#').rstrip('/')
        if base_uri in self.mappings:
            return self.mappings[base_uri]
        
        if base_uri + '/' in self.mappings:
            return self.mappings[base_uri + '/']
        
        if base_uri + '#' in self.mappings:
            return self.mappings[base_uri + '#']

        # Explicit <uri> entries win over prefix rewrites; fall back to rewriteURI.
        return self._resolve_rewrite(uri) or self._resolve_rewrite(base_uri + '/')
    
    def rewrite_target(self, uri: str) -> Optional[Path]:
        """Return the raw ``rewriteURI`` target for *uri*, file **or** directory.

        :meth:`resolve` intentionally yields only documents, because its callers parse
        the result. Some catalogued IRIs name a module *group* rather than a document —
        FIBO's ``.../ontology/FND/`` is a directory of ontologies — and those are still
        legitimately "in the catalog". Use this when existence, not parseability, is
        the question.
        """
        for start, prefix in self.rewrites:
            if not uri.startswith(start):
                continue
            remainder = uri[len(start):]
            candidate = prefix / remainder if remainder else prefix
            if candidate.exists():
                return candidate
        return None

    def is_mapped(self, uri: str) -> bool:
        """Check if URI has a catalog mapping (document or module group)."""
        return self.resolve(uri) is not None or self.rewrite_target(uri) is not None
    
    def get_all_mappings(self) -> Dict[str, Path]:
        """Get all URI → path mappings."""
        return self.mappings.copy()


def load_graph_with_catalog(ontology_path: Path, catalog_path: Path) -> Graph:
    """
    Load an RDF graph and resolve owl:imports using XML catalog.
    
    Args:
        ontology_path: Path to main ontology file
        catalog_path: Path to catalog-v001.xml
        
    Returns:
        RDF graph with all imports loaded
    """
    from rdflib import OWL, URIRef
    
    # Initialize resolver
    resolver = CatalogResolver(catalog_path)
    
    # Load main graph
    graph = Graph()
    graph.parse(ontology_path, format='turtle')
    
    # Find all owl:imports statements
    imports = list(graph.objects(predicate=OWL.imports))
    
    loaded_count = 0
    for import_uri in imports:
        import_str = str(import_uri)
        
        # Check if it's a file:// URI (old pattern - skip)
        if import_str.startswith('file://'):
            print(f"⚠️  Skipping file:// import (use catalog instead): {import_str}")
            continue
        
        # Resolve via catalog
        local_path = resolver.resolve(import_str)
        
        if local_path and local_path.exists():
            try:
                # Parse RDF/XML (FIBO uses .rdf files)
                graph.parse(local_path, format='xml')
                loaded_count += 1
                print(f"✓ Loaded import: {import_str}")
                print(f"  → {local_path}")
            except Exception as e:
                print(f"✗ Error loading {local_path}: {e}")
        else:
            print(f"⚠️  No catalog mapping for: {import_str}")
    
    print(f"\n📦 Loaded {loaded_count}/{len(imports)} imports via catalog")
    
    return graph


def validate_catalog(catalog_path: Path) -> Dict[str, bool]:
    """
    Validate that all catalog mappings point to existing files.
    
    Args:
        catalog_path: Path to catalog file
        
    Returns:
        Dict mapping URI → file_exists (bool)
    """
    resolver = CatalogResolver(catalog_path)
    results = {}
    
    for uri, path in resolver.get_all_mappings().items():
        results[uri] = path.exists()
    
    return results
