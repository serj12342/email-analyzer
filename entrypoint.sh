# entrypoint.sh
#!/bin/bash
set -e

if [[ -z "$1" ]]; then
  echo "Usage: docker run ... --eml file.eml --vt-key YOUR_KEY --cape-url http://... "
  exit 1
fi

python3 main.py "$@"
