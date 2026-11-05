"""Allow running the tool with ``python -m a11y_eco``."""

import sys

from a11y_eco.cli import main

if __name__ == "__main__":
    sys.exit(main())
