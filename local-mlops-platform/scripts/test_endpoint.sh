#!/usr/bin/env bash
# Send a test inference request to the KServe endpoint for the taxi model.
#
# Defaults assume KServe RawDeployment reached via a port-forward:
#   kubectl port-forward -n mlops svc/taxi-fare-predictor-predictor 8081:80
#
# Override HOST/URL/MODEL as needed. Exits non-zero if inference fails.
set -euo pipefail

MODEL="${MODEL:-taxi-fare-predictor}"
HOST="${HOST:-http://127.0.0.1:8081}"
URL="${URL:-$HOST/v1/models/${MODEL}:predict}"

# One trip: [trip_distance, passenger_count, pickup_hour, dow, pu_id, do_id]
PAYLOAD='{"instances": [[3.2, 1, 8, 2, 100, 230]]}'

echo "POST $URL"
echo "payload: $PAYLOAD"

RESPONSE="$(curl -sS -f -X POST "$URL" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD")" || {
    echo "ERROR: inference request failed against $URL" >&2
    echo "Is the InferenceService ready? Try: kubectl get inferenceservice -n mlops" >&2
    exit 1
  }

echo "response: $RESPONSE"

# Confirm the response actually contains a prediction.
if ! echo "$RESPONSE" | grep -q 'predictions'; then
  echo "ERROR: response did not contain 'predictions'" >&2
  exit 2
fi

echo "OK: inference succeeded"
