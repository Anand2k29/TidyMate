"""python -m tidymate  ->  same as the `tidymate` command."""
import sys

from tidymate.cli import main

if __name__ == "__main__":
    sys.exit(main())
