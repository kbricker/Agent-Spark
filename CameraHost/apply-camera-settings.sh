#!/usr/bin/env bash
# Re-apply the camera-side configuration for the Frigate NVR.
#
# Everything here lives in the CAMERA's own flash, not in Frigate. A factory
# reset, a firmware reflash, or a swapped unit wipes all of it - this script
# puts it back in one run instead of an afternoon of clicking.
#
#   CAM_ADMIN_PW='...' ./apply-camera-settings.sh 192.168.86.48
#
# Run it from the camera host, which has network reach to the cameras.
# Credentials come from the environment and are never written to this file.
#
# Optional: set FRIGATE_CAM_PW to also recreate the dedicated viewer account
# that Frigate streams with. On the camera host that value already lives in
# ~/frigate/.env as FRIGATE_CAM48_PASSWORD.

set -euo pipefail

CAM="${1:-192.168.86.48}"
ADMIN_USER="${CAM_ADMIN_USER:-admin}"
ADMIN_PW="${CAM_ADMIN_PW:?set CAM_ADMIN_PW to the camera admin password}"
AUTH="$ADMIN_USER:$ADMIN_PW"

# Two curl flags are mandatory against this firmware (Amcrest IP2M-841B):
#   --basic  it rejects digest auth outright and 401s forever
#   -g       without --globoff, curl eats the [0] in indexed parameters and the
#            request silently does nothing. URL-encoding to %5B0%5D fails too.
CURL=(curl -sg -m 15 --basic -u "$AUTH")

cfg() {
  local desc="$1" params="$2" out
  out=$("${CURL[@]}" "http://$CAM/cgi-bin/configManager.cgi?action=setConfig&$params" 2>/dev/null || true)
  printf '  %-34s %s\n' "$desc" "$(echo "${out:-<no response>}" | tr -d '\r\n')"
}

echo "Applying camera settings to $CAM"

# --- time -------------------------------------------------------------------
# NTP.TimeZone is an INDEX, not an offset, and the table is not the documented
# one. Measured on this firmware: 0=GMT+00:00 rising to 19=GMT+13:00, then
# 20=GMT-01:00 rising to 29=GMT-09:00. 28 is Pacific.
# To re-derive on another model: set a value, then read the unauthenticated
# ONVIF GetSystemDateAndTime at http://<cam>/onvif/device_service and see what
# TZ it reports back.
cfg "NTP on, Pacific" \
  "NTP.Enable=true&NTP.Address=pool.ntp.org&NTP.Port=123&NTP.UpdatePeriod=60&NTP.TimeZone=28"
cfg "US daylight saving rules" \
  "Locales.DSTEnable=true&Locales.DSTStart.Month=3&Locales.DSTStart.Week=2&Locales.DSTStart.Day=0&Locales.DSTStart.Hour=2&Locales.DSTEnd.Month=11&Locales.DSTEnd.Week=1&Locales.DSTEnd.Day=0&Locales.DSTEnd.Hour=2"
printf '  %-34s %s\n' "clock = this host's local time" \
  "$("${CURL[@]}" "http://$CAM/cgi-bin/global.cgi?action=setCurrentTime&time=$(date +%Y-%m-%d%%20%H:%M:%S)" | tr -d '\r\n')"

# --- isolation --------------------------------------------------------------
# T2UServer is the P2P tunnel to p2p.amcrestview.com - the feature that lets a
# phone app reach the camera from anywhere, and the one setting that decides
# whether this camera talks to the internet at all. It ships ON.
cfg "P2P / cloud tunnel OFF" "T2UServer.Enable=false"
cfg "UPnP OFF"               "UPnP.Enable=false"

# --- detection --------------------------------------------------------------
# Frigate does the detection. Two detectors running produces duplicate events.
cfg "on-camera motion detect OFF" "MotionDetect[0].Enable=false"

# --- stream -----------------------------------------------------------------
# 15 fps is plenty for recording and halves both decode load and storage.
# GOP 30 = a keyframe every 2s, which is what Frigate wants for clean segments.
# The substream is deliberately untouched: this model hard-caps it at 640x480
# (4:3 against a 16:9 main), so Frigate detects on the main stream instead.
cfg "main stream 1080p / 15 fps" \
  "Encode[0].MainFormat[0].Video.FPS=15&Encode[0].MainFormat[0].Video.GOP=30"

# --- image ------------------------------------------------------------------
# Ceiling mount, so the sensor hangs inverted. Flip alone is only a VERTICAL
# flip and leaves the picture left-right mirrored - a true 180 needs both.
cfg "180 rotation for ceiling mount" \
  "VideoInOptions[0].Flip=true&VideoInOptions[0].Mirror=true&VideoInOptions[0].NormalOptions.Flip=true&VideoInOptions[0].NormalOptions.Mirror=true&VideoInOptions[0].NightOptions.Flip=true&VideoInOptions[0].NightOptions.Mirror=true"
# DayNightColor: 0 = always colour, 1 = auto by brightness, 2 = always mono.
# Auto is correct - forcing colour keeps the IR cut filter out and leaves the
# garage near black once the light is off.
cfg "colour mode = auto" \
  "VideoInOptions[0].DayNightColor=1&VideoInOptions[0].NormalOptions.DayNightColor=1&VideoInOptions[0].NightOptions.DayNightColor=1"

# --- viewer account ---------------------------------------------------------
# Frigate streams with this rather than admin. Note that ONVIF PTZ still needs
# admin - a user-group account gets "Sender not Authorized" on GetProfiles.
if [ -n "${FRIGATE_CAM_PW:-}" ]; then
  if "${CURL[@]}" "http://$CAM/cgi-bin/userManager.cgi?action=getUserInfoAll" | grep -q 'Name=frigate'; then
    printf '  %-34s %s\n' "viewer account 'frigate'" "already exists, left alone"
  else
    printf '  %-34s %s\n' "viewer account 'frigate'" \
      "$("${CURL[@]}" "http://$CAM/cgi-bin/userManager.cgi?action=addUser&user.Name=frigate&user.Password=$FRIGATE_CAM_PW&user.Group=user&user.Sharable=true&user.Reserved=false&user.Memo=Frigate" | tr -d '\r\n')"
  fi
else
  printf '  %-34s %s\n' "viewer account 'frigate'" "skipped, FRIGATE_CAM_PW not set"
fi

# --- verify -----------------------------------------------------------------
# A setConfig that silently no-ops on a bad parameter looks exactly like one
# that worked, so always read the values back.
echo
echo "Verifying:"
for name in NTP T2UServer UPnP MotionDetect Encode VideoInOptions Locales; do
  "${CURL[@]}" "http://$CAM/cgi-bin/configManager.cgi?action=getConfig&name=$name"
done | grep -iE '^table\.(NTP\.(Enable|Address|TimeZone)|T2UServer\.Enable|UPnP\.Enable|MotionDetect\[0\]\.Enable|Locales\.DSTEnable|Encode\[0\]\.MainFormat\[0\]\.Video\.(FPS|GOP|resolution|Compression)|VideoInOptions\[0\]\.(Flip|Mirror|DayNightColor))=' \
  | sed 's/^/  /'

echo
echo "Camera clock now: $("${CURL[@]}" "http://$CAM/cgi-bin/global.cgi?action=getCurrentTime" | tr -d '\r\n')"
echo "Host clock now:   $(date '+%Y-%m-%d %H:%M:%S')"
