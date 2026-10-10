#!/usr/bin/env bash
# End-to-end smoke test against a running `wrangler dev` (local D1).
# Usage: BASE=http://127.0.0.1:8787 BOOT=<BOOTSTRAP_INVITE_CODE from .dev.vars> bash test/smoke.sh
# Flow: bootstrap register -> login -> upload 3 attempts -> resend (ignored=3) -> snapshot -> logout -> 401
set -u
BASE="${BASE:-http://127.0.0.1:8787}"
BOOT="${BOOT:-$(grep '^BOOTSTRAP_INVITE_CODE' "$(dirname "$0")/../.dev.vars" 2>/dev/null | cut -d= -f2 | tr -d '" ')}"
ORIGIN="${ORIGIN:-http://localhost:8777}"
USER_NAME="smoke.$(date +%s)"
PASS="smoke-password-123"
fail=0
BODY="$(printf '%s' "${TEMP:-/tmp}" | sed 's#\\#/#g')/rex-smoke-body.json"

check() { # label expected actual
  if [ "$2" = "$3" ]; then echo "PASS $1 ($3)"; else echo "FAIL $1 expected=$2 actual=$3"; fail=1; fi
}
req() { # method path [token] [body]
  local method="$1" path="$2" token="${3:-}" body="${4:-}"
  local args=(-s -o "$BODY" -w '%{http_code}' -X "$method" -H "Origin: $ORIGIN")
  [ -n "$token" ] && args+=(-H "Authorization: Bearer $token")
  [ -n "$body" ] && args+=(-H 'Content-Type: application/json' --data "$body")
  curl "${args[@]}" "$BASE$path"
}
jsonval() { python -c "import json,sys;d=json.load(open(sys.argv[2],encoding='utf-8'));print(eval('d'+sys.argv[1]))" "$1" "$BODY" 2>/dev/null; }

code=$(req GET /health); check "health" 200 "$code"
code=$(curl -s -o /dev/null -w '%{http_code}' -X OPTIONS -H "Origin: $ORIGIN" -H 'Access-Control-Request-Method: POST' "$BASE/auth/login"); check "preflight" 204 "$code"

if [ -z "$BOOT" ]; then echo "SKIP bootstrap: no BOOT code (set BOOT=... or .dev.vars)"; exit 1; fi
code=$(req POST /auth/register "" "{\"username\":\"$USER_NAME\",\"password\":\"$PASS\",\"inviteCode\":\"$BOOT\"}")
if [ "$code" = "201" ]; then echo "PASS bootstrap register (201)"; TOKEN=$(jsonval "['token']");
else
  echo "INFO users table not empty (register=$code); logging in with SMOKE_USER/SMOKE_PASS instead"
  USER_NAME="${SMOKE_USER:-$USER_NAME}"; PASS="${SMOKE_PASS:-$PASS}"
  code=$(req POST /auth/login "" "{\"username\":\"$USER_NAME\",\"password\":\"$PASS\"}"); check "login" 200 "$code"; TOKEN=$(jsonval "['token']")
fi
code=$(req POST /auth/login "" "{\"username\":\"$USER_NAME\",\"password\":\"$PASS\"}"); check "login" 200 "$code"
TOKEN=$(jsonval "['token']")
code=$(req POST /auth/login "" "{\"username\":\"$USER_NAME\",\"password\":\"wrong-password\"}"); check "wrong password" 401 "$code"
code=$(req GET /auth/me "$TOKEN"); check "me" 200 "$code"

ITEMS='{"items":[{"clientId":"smoke-1","questionId":"2020-100","chosen":"A","isCorrect":false,"source":"card","elapsedMs":2500,"confidence":3,"sourceSha256":"sha","clientTs":1700000000001},{"clientId":"smoke-2","questionId":"2019-521","chosen":"B","isCorrect":true,"source":"card","elapsedMs":9000,"confidence":null,"sourceSha256":"sha","clientTs":1700000000002},{"clientId":"smoke-3","questionId":"2021-334","chosen":"D","isCorrect":true,"source":"exam","elapsedMs":null,"confidence":null,"sourceSha256":null,"clientTs":1700000000003}]}'
code=$(req POST /sync/attempts "$TOKEN" "$ITEMS"); check "upload attempts" 200 "$code"; check "accepted" 3 "$(jsonval "['accepted']")"
code=$(req POST /sync/attempts "$TOKEN" "$ITEMS"); check "resend attempts" 200 "$code"; check "ignored" 3 "$(jsonval "['ignored']")"
code=$(req POST /sync/attempts "$TOKEN" '{"items":[{"clientId":"bad","questionId":"x","chosen":"F","isCorrect":false,"source":"card","clientTs":1}]}'); check "invalid item" 400 "$code"
code=$(req POST /sync/bookmarks "$TOKEN" '{"items":[{"questionId":"2020-100","starred":true,"updatedAt":1700000000005}]}'); check "bookmark" 200 "$code"
code=$(req GET "/sync/snapshot" "$TOKEN"); check "snapshot" 200 "$code"; check "snapshot attempts" 3 "$(jsonval "['attempts'].__len__()")"
code=$(req POST /auth/logout "$TOKEN"); check "logout" 200 "$code"
code=$(req GET /auth/me "$TOKEN"); check "after logout" 401 "$code"
code=$(req GET /sync/snapshot "$TOKEN"); check "snapshot after logout" 401 "$code"

if [ "$fail" = "0" ]; then echo "SMOKE PASS"; else echo "SMOKE FAIL"; exit 1; fi
