#!/bin/sh
set -e

python -c "
import app
app.ensure_admin()
"

exec "$@"
