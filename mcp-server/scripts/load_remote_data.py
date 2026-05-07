#!/usr/bin/env python3
"""Load mock FHIR data into a remote FHIR server.

Usage:
    python load_remote_data.py <FHIR_BASE_URL>
    
Example:
    python load_remote_data.py https://affinidi-fhir-xxxxxxxxxx.us-central1.run.app/fhir
"""

import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from load_mock_data import main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: FHIR_BASE_URL required")
        print("")
        print("Usage: python load_remote_data.py <FHIR_BASE_URL>")
        print("")
        print("Example:")
        print("  python load_remote_data.py https://your-fhir-service/fhir")
        sys.exit(1)
    
    fhir_url = sys.argv[1]
    os.environ["FHIR_BASE_URL"] = fhir_url
    
    print(f"Loading mock data into: {fhir_url}")
    main()
