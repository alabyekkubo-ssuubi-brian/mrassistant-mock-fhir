#!/usr/bin/env python3
"""Load mock FHIR data into HAPI FHIR server."""

import json
import os
import sys
from pathlib import Path

import httpx


def get_fhir_base_url() -> str:
    """Get FHIR_BASE_URL from environment or use default."""
    return os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")


def load_bundle(bundle_path: Path, fhir_base_url: str) -> None:
    """Load a FHIR Bundle into the server."""
    print(f"Loading bundle from {bundle_path}...")
    
    with open(bundle_path) as f:
        bundle = json.load(f)
    
    # Post the transaction bundle
    response = httpx.post(
        fhir_base_url,
        json=bundle,
        headers={"Content-Type": "application/fhir+json"},
        timeout=60.0
    )
    
    if response.status_code in (200, 201):
        result = response.json()
        entry_count = len(result.get("entry", []))
        print(f"✓ Successfully loaded {entry_count} resources")
        
        # Print summary
        resources = {}
        for entry in result.get("entry", []):
            resource_type = entry.get("response", {}).get("location", "").split("/")[0]
            resources[resource_type] = resources.get(resource_type, 0) + 1
        
        print("\nLoaded resources:")
        for resource_type, count in sorted(resources.items()):
            if resource_type:
                print(f"  - {resource_type}: {count}")
    else:
        print(f"✗ Error loading bundle: {response.status_code}")
        print(response.text)
        sys.exit(1)


def verify_server(fhir_base_url: str) -> bool:
    """Check if HAPI FHIR server is running."""
    try:
        response = httpx.get(f"{fhir_base_url}/metadata", timeout=10.0)
        return response.status_code == 200
    except Exception:
        return False


def main():
    """Main entry point."""
    fhir_base_url = get_fhir_base_url()
    
    print("Hospital FHIR MCP - Mock Data Loader")
    print("=" * 40)
    
    # Check server is running
    print(f"\nChecking FHIR server at {fhir_base_url}...")
    if not verify_server(fhir_base_url):
        print("✗ FHIR server is not running!")
        print("\nStart it with: docker-compose up -d")
        sys.exit(1)
    print("✓ FHIR server is running")
    
    # Load mock data
    bundle_path = Path(__file__).parent.parent / "data" / "mock_bundle.json"
    if not bundle_path.exists():
        print(f"✗ Bundle file not found: {bundle_path}")
        sys.exit(1)
    
    load_bundle(bundle_path, fhir_base_url)
    
    print("\n" + "=" * 40)
    print("Mock data loaded successfully!")
    print("\nTest queries:")
    print(f"  curl {fhir_base_url}/Patient")
    print(f"  curl {fhir_base_url}/Practitioner")
    print(f"  curl '{fhir_base_url}/Slot?status=free'")


if __name__ == "__main__":
    main()
