"""Poll HAPI FHIR until /metadata responds or attempts are exhausted."""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request

URL = "http://localhost:8080/fhir/metadata"
MAX_ATTEMPTS = 10
INTERVAL_SEC = 3


def main() -> int:
    for i in range(MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(URL, timeout=5) as resp:
                if resp.status == 200:
                    print("✓ FHIR server is ready")
                    return 0
        except (urllib.error.URLError, OSError, TimeoutError):
            pass
        print(f"  Waiting... ({i + 1}/{MAX_ATTEMPTS})")
        if i < MAX_ATTEMPTS - 1:
            time.sleep(INTERVAL_SEC)
    print("✗ FHIR server failed to start")
    return 1


if __name__ == "__main__":
    sys.exit(main())
