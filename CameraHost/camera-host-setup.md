# Camera host — setup

Build and configuration reference for a local security-camera recorder: 2 ethernet cameras, 2 USB cameras, motion-event recording only, 30-day rotation, browser UI from any machine on the LAN. Nothing leaves the house.

Software is **Frigate** — MIT licensed, free, no per-camera fees, no cloud account. It does motion detection, object detection, event recording, retention rotation, and the web UI.

- Site: https://frigate.video
- Docs: https://docs.frigate.video
- Source: https://github.com/blakeblackshear/frigate

---

## 1. Hardware

| Part | What | Notes |
|---|---|---|
| Host | Dell OptiPlex 7070 SFF — i5-9500, 16 GB, 512 GB SSD | Renewed. i5-9500 **not** the "F" variant — the UHD 630 iGPU does the video decoding and the object detection |
| Outdoor camera | EmpireTech IPC-T54IR-ZE-S3 | 4 MP on a 1/1.8" sensor, 2.7–12 mm motorized, 12 V DC or PoE, IP67 |
| Ethernet camera 2 | existing camera | any ONVIF/RTSP camera works |
| USB cameras ×2 | ELP-USBFHD01M-L36 | already owned; MJPEG only, re-encoded on the iGPU |

Buy links:

- Camera: https://www.amazon.com/EmpireTech-IPC-T5442T-ZE-Vari-Focal-Eyeball-Starlight/dp/B08C77TNY9 · direct: https://empiretech01.com/products/empiretech-ipc-t54ir-ze-s3-1-1-8-cmos-4mp-ir-starlight-vari-focal-turret-security-camera
- Barrel plugs (if the old power cord was cut): search "5.5 x 2.1 mm screw terminal DC barrel plug"

**No second drive.** Motion-only recording across 4 cameras runs 150–450 GB for 30 days. The 512 GB SSD in the host is the storage. Frigate deletes the oldest hour automatically if it ever fills.

### Power — outdoor camera

- **12 V DC**, 6.7 W maximum, so 0.56 A
- Any 12 V DC supply rated 1 A or more
- Plug: 5.5 mm outer / 2.1 mm center pin, **center positive**
- Confirm the existing supply reads **12 V DC**, not 12 V AC or 24 V AC — measure it. AC on a DC camera destroys it on first power-up.

### Physical install notes

- Turret cameras mount to wall or ceiling; the base is a flat plate and the ball pivots. 360° rotation, 0–78° tilt.
- **The pigtail has an RJ45 plug already crimped on and it is fat.** Check the existing wall hole fits it before ordering. Options: enlarge the hole, use a junction box under the camera, or route through the base's side cable notch.
- Mounted at 10 ft, set the zoom from the browser after mounting rather than climbing back up.

### USB camera limits

- USB 2 caps at roughly 5 m of cable — both cameras must be within ~16 ft of the host, or use active repeaters
- Two 720p cameras share one USB 2 bus fine; do not run both at 1080p30
- The ELPs emit MJPEG only, which cannot be recorded directly — the config below re-encodes to H.264 on the iGPU

---

## 2. Network plan

Reserve all three by MAC address in the router's DHCP settings. Reservations, not device-side static IPs — the router stays the single source of truth.

**All three reservations are in place in Google Wifi as of 2026-08-29.**

| Device | Reserved IP | MAC | Frigate name |
|---|---|---|---|
| Camera host (GarageBox, Dell 7070 SFF) | 192.168.86.142 | `a4:bb:6d:aa:6e:ed` | — (NIC is `eno1`) |
| Amcrest IP2M-841B, in the garage | 192.168.86.48 | `9c:8e:cd:09:b9:95` | `side` |
| Sunba IPC_NT98566_N8F, street-facing PTZ | 192.168.86.139 | `00:12:34:cf:64:c9` | `outdoor` |

Frigate UI: **https://192.168.86.142:8971** (self-signed cert, so the browser will warn). Shell: `ssh camhost`.

To re-read any of those MACs later: `ip link show eno1` on the host, and `ip neigh show` on the host for the two cameras — both are on the same segment, so they sit in its ARP table.

### "Local only" — what is actually true

**A DHCP reservation hands the camera a gateway, so it can reach the internet.** Reserving an IP pins the address; it does not isolate the device. And Google Wifi has no per-device firewall rules, so the router cannot be told to block one camera and not another.

That means isolation has to come from the camera itself. What actually works on this network:

- **Turn off P2P / cloud / UPnP on each camera.** This is the one that matters — P2P is the feature that opens an outbound tunnel to the manufacturer so a phone app can reach the camera from anywhere. Off, the camera has no reason to talk to the internet at all. Section 9 covers how to set it without vendor software.
- **Never create a manufacturer cloud account.** No account, nothing to sync to.
- **Never port-forward** anything to a camera or to Frigate. Frigate is the only thing that should be reachable, and only from inside the house.
- **Blank the gateway if you want it airtight.** Set the camera to a static address on the camera side with the gateway and DNS fields left empty. No default route means no internet, full stop, no firewall needed. Costs you the tidiness of a router reservation — pick one or the other, not both.
- **For access from outside the house later**, use a VPN (Tailscale or WireGuard) into the LAN rather than opening a port.

Verify rather than assume — from the host, watch whether a camera is talking outbound:

```bash
sudo tcpdump -n -i any host 192.168.86.60 and not net 192.168.86.0/24
```

Silence means the camera is staying home.

---

## 3. Install the OS

Ubuntu **Desktop** 26.04 LTS — what is actually installed on this box.

The original plan here was Server, and the rest of this doc was written against it. Kyle had already installed Desktop and was not rebuilding, so Desktop is the reality and Server is the road not taken. Two consequences, both handled:

- Desktop does **not** ship `openssh-server`. It was installed by hand after the fact.
- Desktop suspends on an idle timer, which on an NVR means recording stops overnight. All four sleep targets are masked:
  ```bash
  sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
  ```

A rebuild onto Server would still be the cleaner box — no GUI, no idle timer to fight — but nothing here needs it.

- Download: https://ubuntu.com/download/desktop
- During install: skip all snaps; add OpenSSH afterwards with `sudo apt install -y openssh-server`
- After first boot:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ffmpeg v4l-utils tcpdump
```

`v4l-utils` and `ffmpeg` identify the USB cameras in section 5 and test RTSP URLs in section 9; `tcpdump` is for the outbound-traffic check in section 2. Frigate carries its own ffmpeg inside the container — these are for working at the command line.

---

## 4. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

Log out and back in so the group takes effect. Verify:

```bash
docker run --rm hello-world
```

---

## 5. Pin the USB cameras to stable names

**Do this before configuring Frigate.** With two cameras plugged in, Linux assigns `/dev/video0` and `/dev/video1` in whatever order they enumerate at boot. A reboot can swap them, and then the garage recordings are labeled as the other camera. A udev rule pins each camera to a name based on which physical USB port it is in.

### Identify the ports

Plug in **one camera at a time** so you know which is which.

```bash
ls -l /dev/v4l/by-path/
```

Each camera shows several nodes; the capture node is the one ending `-video-index0`. Then get the udev attribute to match on:

```bash
udevadm info -a -n /dev/video0 | grep -m1 'KERNELS=="[0-9]'
```

That prints something like `KERNELS=="1-3.4:1.0"` — the USB port chain. Note it, unplug, plug in the second camera, repeat.

### Write the rule

`/etc/udev/rules.d/99-cameras.rules`:

```
# Garage USB cameras, pinned by physical USB port.
# ATTR{index}=="0" selects the capture node — a UVC camera also exposes a
# metadata node that cannot produce frames.
# Replace the KERNELS values with what udevadm printed for each port.
SUBSYSTEM=="video4linux", KERNELS=="1-3.4:1.0", ATTR{index}=="0", SYMLINK+="cam-garage-a"
SUBSYSTEM=="video4linux", KERNELS=="1-3.3:1.0", ATTR{index}=="0", SYMLINK+="cam-garage-b"
```

Apply and verify:

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
ls -l /dev/cam-garage-*
```

Both symlinks should appear, pointing at whichever `/dev/videoN` they currently are.

**Identity is the physical port, by design.** Move a camera to a different USB port and it becomes the other name. Label the ports on the back of the host when you cable it.

### Find the supported capture modes

```bash
ffmpeg -f v4l2 -list_formats all -i /dev/cam-garage-a
```

The ELP boards do MJPEG at 1920×1080, 1280×720 and 640×480. Use **1280×720** in the config below — 720p is 16:9 like the 1080p mode, so framing is consistent, and it keeps both cameras comfortably inside one USB 2 bus.

---

## 6. Frigate — docker-compose.yml

Everything lives in **`~/frigate/`** (`/home/kyle/frigate`), not `/opt`. That is deliberate: the whole stack then runs as `kyle` — who is in the `docker` group — so no day-to-day operation on this box needs root. There is no NOPASSWD grant here, so a `/opt` layout would have meant an interactive sudo for routine work.

Put this in `~/frigate/docker-compose.yml`:

```yaml
services:
  frigate:
    container_name: frigate
    image: ghcr.io/blakeblackshear/frigate:stable
    restart: unless-stopped
    stop_grace_period: 30s
    # Decoded frames live in shared memory. Sized for 4 cameras detecting
    # at 1280x720: (1280*720*1.5*20 + 270480) / 1048576 = ~27 MB each,
    # plus ~40 MB for logs. 256 MB leaves room.
    shm_size: "256mb"
    devices:
      # iGPU — video decode, video encode, and object detection
      - /dev/dri/renderD128:/dev/dri/renderD128
      # USB cameras. The HOST side is the stable udev symlink; the CONTAINER
      # side is a fixed number, so the container's view never shuffles.
      - /dev/cam-garage-a:/dev/video10
      - /dev/cam-garage-b:/dev/video11
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - ./config:/config
      - ./storage:/media/frigate
      - type: tmpfs
        target: /tmp/cache
        tmpfs:
          size: 1000000000
    ports:
      - "8971:8971"      # authenticated web UI — this is the one you browse to
      - "8554:8554"      # RTSP restream (optional, LAN only)
      - "8555:8555/tcp"  # WebRTC
      - "8555:8555/udp"
    environment:
      FRIGATE_RTSP_PASSWORD: "set-a-password-here"
```

**Do not publish port 5000.** That is the unauthenticated internal API. Port 8971 is the authenticated one.

Create the directories:

```bash
mkdir -p ~/frigate/config ~/frigate/storage
```

---

## 7. Frigate — config.yml

`~/frigate/config/config.yml`. Replace the IPs, passwords, and camera names.

```yaml
mqtt:
  enabled: false

# Object detection on the Intel iGPU. No accelerator card needed —
# OpenVINO supports 6th gen Intel and newer.
detectors:
  ov:
    type: openvino
    device: GPU

model:
  width: 300
  height: 300
  input_tensor: nhwc
  input_pixel_format: bgr
  path: /openvino-model/ssdlite_mobilenet_v2.xml
  labelmap_path: /openvino-model/coco_91cl_bkgr.txt

# Hardware video decode. preset-vaapi covers Intel gen 8 through gen 12,
# which includes the 9th gen UHD 630 in this host.
ffmpeg:
  hwaccel_args: preset-vaapi

# ---------- defaults every camera inherits ----------

detect:
  enabled: true
  fps: 5

objects:
  track:
    - person
    - car
    - dog
    - cat

# Motion-only retention. continuous: 0 means no 24/7 recording at all.
record:
  enabled: true
  continuous:
    days: 0
  motion:
    days: 30
  alerts:
    retain:
      days: 30
  detections:
    retain:
      days: 30

snapshots:
  enabled: true
  retain:
    default: 30

# ---------- streams ----------

go2rtc:
  streams:
    # --- ethernet cameras ---
    # Dahua / Amcrest URL form. subtype=0 is the main stream (recording),
    # subtype=1 is the substream (detection).
    driveway:
      - rtsp://viewer:PASSWORD@192.168.86.60:554/cam/realmonitor?channel=1&subtype=0
    driveway_sub:
      - rtsp://viewer:PASSWORD@192.168.86.60:554/cam/realmonitor?channel=1&subtype=1
    side:
      - rtsp://viewer:PASSWORD@192.168.86.61:554/cam/realmonitor?channel=1&subtype=0
    side_sub:
      - rtsp://viewer:PASSWORD@192.168.86.61:554/cam/realmonitor?channel=1&subtype=1

    # --- USB cameras ---
    # These emit MJPEG, which cannot be recorded. #video=h264 encodes to
    # H.264 and #hardware puts that encode on the iGPU.
    garage_a:
      - "ffmpeg:device?video=/dev/video10&input_format=mjpeg&video_size=1280x720&framerate=10#video=h264#hardware"
    garage_b:
      - "ffmpeg:device?video=/dev/video11&input_format=mjpeg&video_size=1280x720&framerate=10#video=h264#hardware"

# ---------- cameras ----------

cameras:

  driveway:
    ffmpeg:
      inputs:
        - path: rtsp://127.0.0.1:8554/driveway
          input_args: preset-rtsp-restream
          roles:
            - record
        - path: rtsp://127.0.0.1:8554/driveway_sub
          input_args: preset-rtsp-restream
          roles:
            - detect
    detect:
      width: 1280
      height: 720
    motion:
      # Outdoors. Less sensitive than the default so headlights, rain and
      # branches do not each become an event.
      threshold: 30
      contour_area: 30
      improve_contrast: true
      # mask: draw this in the UI once you see what actually triggers.

  side:
    ffmpeg:
      inputs:
        - path: rtsp://127.0.0.1:8554/side
          input_args: preset-rtsp-restream
          roles:
            - record
        - path: rtsp://127.0.0.1:8554/side_sub
          input_args: preset-rtsp-restream
          roles:
            - detect
    detect:
      width: 1280
      height: 720
    motion:
      threshold: 30
      contour_area: 30

  garage_a:
    ffmpeg:
      inputs:
        # One stream serves both roles — a USB camera has no substream.
        - path: rtsp://127.0.0.1:8554/garage_a
          input_args: preset-rtsp-restream
          roles:
            - record
            - detect
    detect:
      width: 1280
      height: 720
    motion:
      # Indoors and controlled — safe to run more sensitive.
      threshold: 25
      contour_area: 10

  garage_b:
    ffmpeg:
      inputs:
        - path: rtsp://127.0.0.1:8554/garage_b
          input_args: preset-rtsp-restream
          roles:
            - record
            - detect
    detect:
      width: 1280
      height: 720
    motion:
      threshold: 25
      contour_area: 10
```

Start it:

```bash
cd ~/frigate && docker compose up -d
docker logs -f frigate
```

---

## 8. First login

- Browse to `https://<host-ip>:8971` from any machine on the LAN
- Frigate creates an **admin** user on first start and prints the generated password in the startup log — `docker logs frigate | grep -i password`
- Change it immediately in Settings → Users
- The certificate is self-signed, so the browser will warn once. Accept it.

---

## 9. Camera-side configuration — without vendor software

### What has to be set on the camera

Frigate consumes streams; it does not configure the camera that produces them. These settings live on the camera and have to be set there once.

- **A dedicated viewer account** for Frigate rather than reusing admin
- **Main stream:** H.264, full resolution, 15 fps. Prefer H.264 over H.265 — browser playback of H.265 is inconsistent
- **Substream:** H.264, 1280×720, 5 fps, low bitrate. Same aspect ratio as the main stream, or Frigate's detection boxes land in the wrong place
- **Time:** NTP on, timezone matching the host, or event timestamps disagree with the recordings
- **P2P / cloud / UPnP: off.** See section 2 — this is the setting that decides whether the camera talks to the internet
- **On-camera "smart" detection: off.** Frigate does the detection; two detectors fighting produces duplicate events
- **Timestamp overlay: leave it on**, then mask it in Frigate so a ticking clock is not motion

### Four ways to set it, and what each can actually reach

**Frigate — no.** Worth stating plainly so it is not a surprise: Frigate's only outbound control of a camera is ONVIF PTZ. It never pushes encoder settings, time, or accounts. Nothing in the config file changes anything on the camera.

**The camera's own web page — yes, and it is not vendor software.** No download, no installer, no account, no phone app. The camera runs a web server; you point a browser at `http://<camera-ip>` and it serves you a settings page. It is the same category of thing as a router's admin page. This is the shortest path for one-time setup, and it reaches every setting including the vendor-specific ones.

**ONVIF — yes, vendor-neutral, partial coverage.** The open standard every one of these cameras speaks. Reaches video encoder configuration (codec, resolution, fps, bitrate), system time, users, and PTZ. Does **not** reach vendor-specific toggles — P2P and cloud are not in the ONVIF spec, so they cannot be turned off this way.

- ONVIF Device Manager, Windows, open source, does the job from a GUI: https://sourceforge.net/projects/onvifdm/
- Scriptable from Python: https://github.com/FalkTannhaeuser/python-onvif-zeep

```python
from onvif import ONVIFCamera
cam = ONVIFCamera('192.168.86.60', 80, 'admin', 'PASSWORD')
media = cam.create_media_service()
for profile in media.GetProfiles():
    print(profile.Name, profile.VideoEncoderConfiguration.Resolution)
```

**The HTTP CGI API — yes, full coverage, fully scriptable.** Dahua-built cameras (EmpireTech, Amcrest, and most white-label rebadges) expose their entire configuration tree over plain HTTP with digest auth. Everything the web page can do, curl can do, including P2P. This is the route if you want the camera config in version control rather than in someone's memory of which checkbox they clicked.

Spec: https://wiki.dno-it.ru/wp-content/uploads/2023/06/dahua_http_api_for_ipcsd-v1.40.pdf

### The CGI recipe — discover, then set

Parameter names vary by model and firmware, so do not guess them. Dump the tree and search it.

```bash
CAM=192.168.86.60
AUTH='admin:PASSWORD'

# Dump the entire config to a file, once, then grep it at leisure.
curl -s --digest -u "$AUTH" \
  "http://$CAM/cgi-bin/configManager.cgi?action=getConfig&name=all" > cam-config.txt

grep -i p2p    cam-config.txt
grep -i ntp    cam-config.txt
grep -i encode cam-config.txt
```

Read one subtree at a time:

```bash
curl -s --digest -u "$AUTH" \
  "http://$CAM/cgi-bin/configManager.cgi?action=getConfig&name=Encode"
```

Set a value — the parameter name is exactly what `getConfig` printed, left of the `=`:

```bash
curl -s --digest -u "$AUTH" \
  "http://$CAM/cgi-bin/configManager.cgi?action=setConfig&Encode[0].MainFormat[0].Video.FPS=15"
```

Confirm it took by reading it back. A `setConfig` that silently no-ops on a misspelled parameter looks identical to one that worked.

```bash
# Device identity, useful for confirming you are talking to the right camera
curl -s --digest -u "$AUTH" "http://$CAM/cgi-bin/magicBox.cgi?action=getDeviceType"
```

Worth doing once the settings are right: keep the `setConfig` calls in a shell script in this folder. Then a camera swap or a factory reset is a script run, not an afternoon of clicking.

### RTSP URLs

| Brand | Main stream | Substream |
|---|---|---|
| Dahua / Amcrest / EmpireTech | `/cam/realmonitor?channel=1&subtype=0` | `...subtype=1` |
| Hikvision | `/Streaming/Channels/101` | `/Streaming/Channels/102` |
| Reolink | `/h264Preview_01_main` | `/h264Preview_01_sub` |

For an unknown camera, ask it over ONVIF rather than guessing — `GetStreamUri` returns the real URLs. ONVIF Device Manager shows them in its GUI; the Python snippet above reaches the same call.

Test any candidate URL before putting it in the config:

```bash
ffprobe "rtsp://viewer:PASSWORD@192.168.86.60:554/cam/realmonitor?channel=1&subtype=0"
```

That prints the codec, resolution and frame rate — which also confirms the substream's aspect ratio matches the main.

---

## 10. Tuning — the first week

Do not tune sensitivity in the config file by guessing. Frigate has a live tuner.

- **Settings → Motion Tuner** in the UI shows motion boxes drawn on the live image while you move the sliders. Adjust until real activity registers and wind does not.
- `threshold` (default 30, range 1–255) — how much a pixel must change. **Higher = less sensitive.**
- `contour_area` (default 10) — how large a blob must be. **Higher = ignores smaller movement.** 10 is high sensitivity, 30 medium, 50 low.
- `improve_contrast` — helps at night; turn it off if it is causing noise events.
- **Masks** — draw over anything that moves constantly and is not interesting: a tree line, a road, the timestamp overlay. This kills more false events than any threshold change.
- **Zones** — draw the areas you care about, so a person in the driveway alerts and a person on the sidewalk does not.

Check what storage is actually doing after a week:

```bash
du -sh ~/frigate/storage
```

Multiply by four for a 30-day estimate. If it is far under budget, consider turning on a few days of continuous recording as well:

```yaml
record:
  continuous:
    days: 3
```

---

## 11. Gotchas

- **`/dev/videoN` shuffles across reboots.** Handled by the udev rule in step 5. Do it before you build the config, not after the first confusing reboot.
- **Never publish port 5000** and never port-forward anything. 8971 is the authenticated port; use a VPN for outside access.
- **The ELP cameras emit MJPEG only.** They must be encoded to H.264 to be recorded. `#video=h264#hardware` in the go2rtc line does this on the iGPU.
- **Motion-only saves disk, not CPU.** Frigate decodes and analyzes every frame around the clock regardless of what it keeps.
- **An unlit indoor camera is in IR mode at noon, and `improve_contrast` will fill your disk.** A dark scene keeps the camera in night mode permanently; contrast-stretching that grainy IR frame turns sensor noise into motion, and motion-only recording then records continuously. The tell is a camera whose hourly storage is flat across the whole day — the same at 03:00 as at 12:00. The garage camera here wrote 1.2 GB/hour of an empty garage until `improve_contrast: false` was set on it (2026-08-29, plan #951). Outdoor cameras that actually see daylight can keep it on.
- **`contour_area` is resolution-INDEPENDENT — do not scale it per camera.** Frigate resizes every motion frame to `motion.frame_height` (default 100 rows, aspect preserved) and measures contour area on *that*; the resize factor is only used to map boxes back to full-res coordinates. So `contour_area: 30` means the same thing on a 1920x1080 detect stream as on an 800x448 one. It is tempting to "correct" the value for a larger stream; that would desensitise the camera by roughly the area ratio for no reason.
- **Bytes on disk = bitrate x hours recorded. Resolution is not a lever.** These streams are VBR under a bitrate cap, so dropping 4K to 1440p at the same cap saves nothing — it just spends the same bits on fewer pixels. To cut storage you either lower the cap or record fewer hours (masks, zones, sensitivity).
- **`storage/recordings/` is named in UTC** while the host clock is local. Off-by-eight when you go looking for last night's footage.
- **`unattended-upgrades` is on by default** in Ubuntu. Packages move on their own, and a service restarting mid-week is worth checking before blaming a config change.
- **Pure motion does not appear in the Review page.** The scrollable event list is built on object detection — that is why detection is enabled here rather than motion alone. Motion-only segments still show on the recordings timeline.
- **Aspect ratio mismatch between main and sub stream** makes Frigate's boxes land in the wrong place. A 16:9 main pairs with a 16:9 sub.
- **XiongMai/Sofia account message IDs** (confirmed against the sofiactl reference client, whose 1472/1473 users pair matched the Sunba exactly): 1470 full authority list, 1472 users get, 1474 groups, 1482 add user, 1484 modify user, 1486 delete user, **1488 modify password** (response 1489). Request N answers on N+1.
- **The 1488 password payload is flat**, shaped like the login packet rather than the `Name`-plus-same-named-key convention every config op uses: `{"Name": "", "SessionID": sid, "EncryptType": "MD5", "NewPassWord": <hash of new>, "PassWord": <hash of old>, "UserName": "admin"}`. Both passwords go through `sofia_hash()`.
- **Changing a XiongMai password breaks its RTSP URLs**, because the URL embeds a hash of the password rather than the password. Regenerate both the main and sub URLs in the same change or the streams go dark. Keep the hash in `.env` and reference it as `{VAR}` from the go2rtc block.
- **1488 updates `Password` but leaves `PasswordV2` stale.** That looks alarming and is not: DVRIP login validates the former, and the old password is correctly refused afterwards. Do not try to hand-write a V2 blob.
- **Do not assume a camera's ONVIF authenticates.** The Sunba accepts `GetDeviceInformation` with *any* password - blank, correct, or garbage. Verify with a deliberately wrong password before believing a camera's ONVIF is protected; on this board the real access control is DVRIP on 34567, not ONVIF on 8899.
- **Frigate self-protects on a full disk** by deleting the oldest hour, ahead of the retention policy.
- **This box's BIOS cannot be updated from the OS.** `fwupdmgr` stages the Dell capsule correctly and the firmware silently ignores it — no error, no ESRT attempt recorded, version unchanged after reboot. Check `/sys/firmware/efi/esrt/entries/entry0/last_attempt_status`: `0` alongside `last_attempt_version: 0` means the firmware never tried, which is a different failure from a flash that failed. Use a FAT32 USB stick and F12 -> BIOS Flash Update instead. The Secure Boot db and dbx updates in the same batch DID apply from the OS, so a partial success here is normal.
- **Dell BIOS settings are reachable from Linux** via `dell-wmi-sysman` under `/sys/class/firmware-attributes/`, readable and writable as root when no BIOS admin password is set. `AcPwrRcvry` is the one that matters for an NVR — set `On` so the box returns by itself after a power cut. Re-check it after any BIOS update.
- **`docker compose stop` survives a reboot.** It marks the container stopped, which overrides the restart policy, so Frigate stays down until an explicit `up -d`. Stopping it cleanly before a reboot is right; just remember to start it after.

---

## 12. Links

| What | Where |
|---|---|
| Frigate docs | https://docs.frigate.video |
| Installation | https://docs.frigate.video/frigate/installation |
| Recording & retention | https://docs.frigate.video/configuration/record |
| Motion detection | https://docs.frigate.video/configuration/motion_detection |
| Object detectors (OpenVINO) | https://docs.frigate.video/configuration/object_detectors |
| Hardware acceleration | https://docs.frigate.video/configuration/hardware_acceleration_video |
| Camera-specific config (USB cameras) | https://docs.frigate.video/configuration/camera_specific/ |
| Ubuntu Desktop download | https://ubuntu.com/download/desktop |
| Docker install | https://get.docker.com |
| ONVIF Device Manager | https://sourceforge.net/projects/onvifdm/ |
| python-onvif-zeep | https://github.com/FalkTannhaeuser/python-onvif-zeep |
| Dahua HTTP API spec | https://wiki.dno-it.ru/wp-content/uploads/2023/06/dahua_http_api_for_ipcsd-v1.40.pdf |
