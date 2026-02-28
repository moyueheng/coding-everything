#!/bin/zsh
set -euo pipefail

CLI="${CLI:-/opt/homebrew/bin/betterdisplaycli}"
TARGET_DISPLAY="${TARGET_DISPLAY:-34C1Q}"
VSCREEN_NAME="${VSCREEN_NAME:-VS3008}"
RES_LIST="${RES_LIST:-2880x1206,3008x1260}"
PREFERRED_MODE="${PREFERRED_MODE:-3008x1260}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

is_desired_state() {
  local connected main ui_ok mirror_ok

  connected="$("$CLI" get --name="$VSCREEN_NAME" --connected 2>/dev/null || true)"
  main="$("$CLI" get --name="$VSCREEN_NAME" --main 2>/dev/null || true)"

  ui_ok=0
  if system_profiler SPDisplaysDataType 2>/dev/null | grep -A8 "${VSCREEN_NAME}:" | grep -q "UI Looks like: ${PREFERRED_MODE/x/ x }"; then
    ui_ok=1
  elif system_profiler SPDisplaysDataType 2>/dev/null | grep -A8 "${VSCREEN_NAME}:" | grep -q "UI Looks like: 3008 x 1260"; then
    ui_ok=1
  fi

  mirror_ok=0
  if system_profiler SPDisplaysDataType 2>/dev/null | grep -A8 "${VSCREEN_NAME}:" | grep -q "Mirror: On" \
    && system_profiler SPDisplaysDataType 2>/dev/null | grep -A8 "${TARGET_DISPLAY}:" | grep -q "Mirror: On"; then
    mirror_ok=1
  fi

  [[ "$connected" == *"on"* && "$main" == "true" && "$ui_ok" -eq 1 && "$mirror_ok" -eq 1 ]]
}

if [[ ! -x "$CLI" ]]; then
  log "betterdisplaycli not found at $CLI"
  exit 1
fi

open -gj -a /Applications/BetterDisplay.app || true

for _ in {1..30}; do
  if "$CLI" get --identifiers >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

seen_target=0
for _ in {1..60}; do
  if "$CLI" get --identifiers 2>/dev/null | /usr/bin/grep -Fq "\"name\" : \"$TARGET_DISPLAY\""; then
    seen_target=1
    break
  fi
  sleep 2
done

if [[ "$seen_target" -ne 1 ]]; then
  log "target display $TARGET_DISPLAY not found; skip this run"
  exit 0
fi

if is_desired_state; then
  log "state already healthy; skip reconfigure"
  exit 0
fi

if ! "$CLI" get --identifiers 2>/dev/null | /usr/bin/grep -Fq "\"name\" : \"$VSCREEN_NAME\""; then
  log "creating virtual screen $VSCREEN_NAME"
  "$CLI" create --type=VirtualScreen --virtualScreenName="$VSCREEN_NAME" --useResolutionList=on --resolutionList="$RES_LIST" --virtualScreenHiDPI=on >/dev/null 2>&1 || true
  sleep 1
fi

"$CLI" set --name="$VSCREEN_NAME" --useResolutionList=on --resolutionList="$RES_LIST" --virtualScreenHiDPI=on >/dev/null 2>&1 || true

log "ensuring $VSCREEN_NAME is connected"
"$CLI" set --name="$VSCREEN_NAME" --connected=on >/dev/null 2>&1 || true
sleep 1

log "setting $VSCREEN_NAME as main display"
"$CLI" set --name="$VSCREEN_NAME" --main=on >/dev/null 2>&1 || true
sleep 1

log "mirroring $VSCREEN_NAME to $TARGET_DISPLAY"
"$CLI" set --name="$VSCREEN_NAME" --mirror=on --specifier="$TARGET_DISPLAY" >/dev/null 2>&1 || true
sleep 1

"$CLI" set --name="$VSCREEN_NAME" --resolution="$PREFERRED_MODE" --hiDPI=on >/dev/null 2>&1 || true

log "done"
