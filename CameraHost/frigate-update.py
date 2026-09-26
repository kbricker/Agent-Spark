#!/usr/bin/env python3
# Nightly Frigate update for the camera box.
#
# Frigate publishes fixes only on its newest release, and this box is about
# to be reachable from the internet, so the pinned image has to follow every
# release. A big release migrates config.yml and frigate.db on startup and
# can need a manual change; if that migration does not come up recording,
# the box has stopped doing its only job. This job moves the pin forward,
# and if the new version does not come up recording it puts the previous
# compose file, config and database back and holds that version.
#
# kyle's crontab runs it. See camera-host-setup.md section 13.

import datetime
import difflib
import errno
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

# Paths on the camera box, always with a slash. This process never opens
# FRIGATE_DIR/.env. os.path.join is not used here: on Windows it would
# bake backslashes into the strings the state file is checked against.
FRIGATE_DIR = "/home/kyle/frigate"
COMPOSE_PATH = "/home/kyle/frigate/docker-compose.yml"
CONFIG_DIR = "/home/kyle/frigate/config"
CONFIG_PATH = "/home/kyle/frigate/config/config.yml"
DB_PATH = "/home/kyle/frigate/config/frigate.db"
DB_WAL_PATH = "/home/kyle/frigate/config/frigate.db-wal"
DB_SHM_PATH = "/home/kyle/frigate/config/frigate.db-shm"
LOCK_PATH = "/home/kyle/frigate/.frigate-update.lock"
STATE_PATH = "/home/kyle/frigate/update-state.json"
HOLD_PATH = "/home/kyle/frigate/update-hold.txt"
STATUS_PATH = "/home/kyle/frigate/update-status.json"
BACKUP_ROOT = "/home/kyle/frigate/update-backups"

REGISTRY = "ghcr.io/blakeblackshear/frigate"
STABLE_REF = REGISTRY + ":stable"
CONTAINER = "frigate"
VERSION_PATH = "/opt/frigate/frigate/version.py"
API_CONFIG = "http://127.0.0.1:5000/api/config"
API_STATS = "http://127.0.0.1:5000/api/stats"
CACHE_DIR = "/tmp/cache"
COMPLETE_NAME = "COMPLETE"

# Specified bounds.
TOTAL_BUDGET_S = 60 * 60
ROLLBACK_RESERVE_S = 15 * 60
HEALTH_POLL_S = 10
HEALTH_TIMEOUT_S = 480
HEALTH_SETTLE_S = 60
DISK_HEADROOM = 2
KEEP_BACKUPS = 7
STDERR_CLIP = 200

# Not measured on the box. Each command's timeout is min(its cap, the
# budget still outside the rollback reserve). Rollback steps may spend
# the reserve. Caps below are sized so one stop, one restore and one
# up still fit beside the 9 minute health window inside that reserve.
DOCKER_READY_WAIT_S = 180
DOCKER_READY_POLL_S = 5
INFO_CAP_S = 20
INSPECT_CAP_S = 20
PULL_CAP_S = 20 * 60
RUN_CAT_CAP_S = 60
EXEC_CAP_S = 30
# stop_grace_period is 30s. Two stop attempts and two up attempts, plus the
# copy, still fit beside the 9 minute health window inside the 15 minute reserve.
STOP_CAP_S = 60
STOP_POLL_S = 10
UP_CAP_S = 60
BACKUP_CAP_S = 90
IMAGE_LS_CAP_S = 30
IMAGE_RM_CAP_S = 60
COPY_CHUNK_BYTES = 8 * 1024 * 1024
APPLY_NEED_S = (
    2 * (STOP_CAP_S + STOP_POLL_S)
    + BACKUP_CAP_S
    + 2 * UP_CAP_S
    + HEALTH_TIMEOUT_S
    + HEALTH_SETTLE_S
)

# curl is the verified client for the local API. Listing /tmp/cache uses
# /bin/ls in the image; that binary was not separately checked.
DOCKER = "docker"
CACHE_LIST_ARGV_TAIL = ["/bin/ls", "-1", CACHE_DIR]

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
VERSION_PY_RE = re.compile(r'^VERSION\s*=\s*"(\d+\.\d+\.\d+)(?:-[^"]*)?"$')
EXACT_IMAGE_RE = re.compile(r"^    image: (\S+)\s*$")
IMAGE_KEY_RE = re.compile(r"^image\s*:")
REF_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,255}$")
CACHE_RE = re.compile(r"^(.+)@(\d{14})([+-])(\d{4})\.mp4$")

PHASES = {
    "applying",
    "backed-up",
    "switched",
    "rolling-back",
    "restored",
    "failed",
}
EXIT_CODES = {
    "current": 0,
    "updated": 0,
    "recovered": 0,
    "skipped": 0,
    "held": 1,
    "rolled-back": 1,
    "refused": 1,
    "error": 1,
    "rollback-failed": 2,
    "broken": 2,
}
BACKUP_FILES = ("docker-compose.yml", "config.yml", "frigate.db")
OPTIONAL_DB_FILES = ("frigate.db-wal", "frigate.db-shm")
LIVE_BY_BACKUP_NAME = {
    "docker-compose.yml": COMPOSE_PATH,
    "config.yml": CONFIG_PATH,
    "frigate.db": DB_PATH,
    "frigate.db-wal": DB_WAL_PATH,
    "frigate.db-shm": DB_SHM_PATH,
}

COMPOSE_STOP = [DOCKER, "compose", "--project-directory", FRIGATE_DIR, "stop"]
COMPOSE_UP = [DOCKER, "compose", "--project-directory", FRIGATE_DIR, "up", "-d"]


class Fail(Exception):
    def __init__(self, kind, detail):
        super().__init__(detail)
        self.kind = kind
        self.detail = detail


# Not an Exception. A SIGTERM or SIGINT must not be caught by the
# `except Exception` around stop, backup, rewrite, up, restore or persist
# and then saved as phase "failed".
class Interrupted(BaseException):
    pass


class BudgetExhausted(Exception):
    pass


class CmdTimeout(Exception):
    pass


class CmdFailed(Exception):
    def __init__(self, returncode, err, argv):
        super().__init__(err)
        self.returncode = returncode
        self.err = err
        self.argv = argv


class Run:
    def __init__(self):
        self.dry_run = False
        self.deadline = 0.0
        self.lock_fd = None
        self.stop_issued = False
        self.switched = False
        self.phase_restored = False
        self.target_healthy = False
        self.bringing_back = False
        self.state = None
        self.restart_count = None
        self.baseline_cameras = None
        self.baseline_detectors = None


RUN = Run()


def start_clock():
    RUN.deadline = time.monotonic() + TOTAL_BUDGET_S


def remaining(use_reserve):
    left = RUN.deadline - time.monotonic()
    if not use_reserve:
        left -= ROLLBACK_RESERVE_S
    return left


def log(message):
    now = datetime.datetime.now().astimezone()
    text = " ".join(str(message).split())
    print(f"{now:%Y-%m-%d %H:%M:%S} {text[:500]}", flush=True)


def clip_err(text):
    if not text:
        return ""
    line = " ".join(text.splitlines()[0].split())
    lowered = line.lower()
    if "rtsp://" in lowered or "password" in lowered or ".env" in lowered:
        return "stderr redacted"
    return line[:STDERR_CLIP]


def short(exc):
    return clip_err(str(exc)) or exc.__class__.__name__


def valid_version(value):
    return isinstance(value, str) and VERSION_RE.fullmatch(value) is not None


def version_key(value):
    if not valid_version(value):
        raise ValueError(f"not a plain version: {value!r}")
    return tuple(int(part) for part in value.split("."))


def is_newer(candidate, current):
    return version_key(candidate) > version_key(current)


def valid_ref(ref):
    if not isinstance(ref, str) or REF_RE.fullmatch(ref) is None:
        return False
    if ".." in ref:
        return False
    return True


def parse_version_py(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("version.py is empty")
    match = VERSION_PY_RE.fullmatch(lines[-1])
    if match is None:
        raise ValueError("version.py last line is not VERSION = \"X.Y.Z\"")
    return match.group(1)


def parse_hold(text):
    found = set()
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        token = stripped.split()[0]
        rest = stripped[len(token):].strip()
        if rest and not rest.startswith("#"):
            raise ValueError(f"hold line {lineno} is not a version")
        if not valid_version(token):
            raise ValueError(f"hold line {lineno} is not a version")
        found.add(token)
    return found


def _compose_lines(text):
    return text.splitlines(keepends=True)


def image_line_indexes(text):
    indexes = []
    for index, line in enumerate(_compose_lines(text)):
        body = line[:-1] if line.endswith("\n") else line
        if body.endswith("\r"):
            body = body[:-1]
        stripped = body.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if IMAGE_KEY_RE.match(stripped):
            indexes.append(index)
    return indexes


def parse_compose_image(text):
    indexes = image_line_indexes(text)
    if len(indexes) != 1:
        raise ValueError(f"compose has {len(indexes)} image lines")
    lines = _compose_lines(text)
    body = lines[indexes[0]]
    if body.endswith("\n"):
        body = body[:-1]
    if body.endswith("\r"):
        body = body[:-1]
    match = EXACT_IMAGE_RE.fullmatch(body)
    if match is None:
        raise ValueError("compose image line is not four-space 'image: <ref>'")
    ref = match.group(1)
    if not valid_ref(ref):
        raise ValueError("compose image ref is not a plain reference")
    return ref


def rewrite_compose_image(text, new_ref):
    if not valid_ref(new_ref):
        raise ValueError("replacement image ref is not a plain reference")
    indexes = image_line_indexes(text)
    if len(indexes) != 1:
        raise ValueError(f"compose has {len(indexes)} image lines")
    lines = _compose_lines(text)
    body = lines[indexes[0]]
    newline = ""
    if body.endswith("\r\n"):
        newline = "\r\n"
        body = body[:-2]
    elif body.endswith("\n"):
        newline = "\n"
        body = body[:-1]
    if EXACT_IMAGE_RE.fullmatch(body) is None:
        raise ValueError("compose image line is not four-space 'image: <ref>'")
    lines[indexes[0]] = f"    image: {new_ref}{newline}"
    rewritten = "".join(lines)
    if parse_compose_image(rewritten) != new_ref:
        raise ValueError("rewritten compose did not parse")
    return rewritten


def parse_cache_name(name):
    # Cache names carry a second and a numeric offset, e.g.
    # side@20260925192143-0700.mp4. The threshold is floored to that
    # second so a segment opened in the same second up -d returned counts.
    match = CACHE_RE.fullmatch(name)
    if match is None:
        return None
    camera, stamp, sign, offset = match.groups()
    if not camera or "/" in camera or camera in (".", ".."):
        return None
    try:
        wall = datetime.datetime.strptime(stamp, "%Y%m%d%H%M%S")
    except ValueError:
        return None
    hours = int(offset[:2])
    minutes = int(offset[2:])
    if hours > 23 or minutes > 59:
        return None
    delta = datetime.timedelta(hours=hours, minutes=minutes)
    if sign == "-":
        delta = -delta
    return camera, wall.replace(tzinfo=datetime.timezone(delta))


def cache_segment_is_fresh(name, camera, not_before):
    parsed = parse_cache_name(name)
    if parsed is None:
        return False
    got_camera, stamp = parsed
    if got_camera != camera:
        return False
    threshold = not_before.astimezone().replace(microsecond=0)
    return stamp >= threshold


def parse_docker_time(value):
    text = value.strip()
    if not text or text == "<no value>":
        raise ValueError("empty docker time")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if "." in text:
        head, tail = text.split(".", 1)
        split_at = None
        for index, char in enumerate(tail):
            if char in "+-":
                split_at = index
                break
        if split_at is None:
            frac = tail
            tz = ""
        else:
            frac = tail[:split_at]
            tz = tail[split_at:]
        text = f"{head}.{(frac + '000000')[:6]}{tz}"
    parsed = datetime.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed


def line_change_count(before, after):
    # Added plus removed diff lines. One edited line counts as two.
    count = 0
    for line in difflib.ndiff(before.splitlines(), after.splitlines()):
        if line.startswith("+ ") or line.startswith("- "):
            count += 1
    return count


def render_hold(text, version):
    if not valid_version(version):
        raise ValueError("hold version is not X.Y.Z")
    if version in parse_hold(text):
        if text and not text.endswith("\n"):
            return text + "\n"
        return text
    if text and not text.endswith("\n"):
        text += "\n"
    return text + version + "\n"


def _backup_dir_ok(path):
    prefix = BACKUP_ROOT + "/"
    if not isinstance(path, str) or not path.startswith(prefix):
        return False
    name = path[len(prefix):]
    if not name or "/" in name or "\\" in name or name in (".", ".."):
        return False
    if name != os.path.basename(name):
        return False
    return True


def assert_contained_backup(path):
    if not _backup_dir_ok(path):
        raise OSError("backup dir is not under update-backups")
    root = os.path.realpath(BACKUP_ROOT)
    real = os.path.realpath(path)
    if real == root or os.path.commonpath([root, real]) != root:
        raise OSError("backup dir resolves outside update-backups")


NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,128}$")


def _name_list(value):
    if not isinstance(value, list) or not value:
        return None
    names = []
    for item in value:
        if not isinstance(item, str) or NAME_RE.fullmatch(item) is None:
            return None
        names.append(item)
    return names


def encode_state(state):
    payload = {
        "phase": state["phase"],
        "from_ref": state["from_ref"],
        "from_version": state["from_version"],
        "to_ref": state["to_ref"],
        "to_version": state["to_version"],
        "backup_dir": state["backup_dir"],
    }
    if state.get("up_at"):
        payload["up_at"] = state["up_at"]
    payload["cameras"] = list(state["cameras"])
    payload["detectors"] = list(state["detectors"])
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def decode_state(text):
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("state is not an object")
    phase = data.get("phase")
    if phase not in PHASES:
        raise ValueError("state phase is unknown")
    from_ref = data.get("from_ref")
    to_ref = data.get("to_ref")
    if not valid_ref(from_ref) or not valid_ref(to_ref):
        raise ValueError("state image ref is not a plain reference")
    from_version = data.get("from_version")
    to_version = data.get("to_version")
    if not valid_version(from_version) or not valid_version(to_version):
        raise ValueError("state version is not X.Y.Z")
    backup_dir = data.get("backup_dir")
    if not _backup_dir_ok(backup_dir):
        raise ValueError("state backup dir is outside update-backups")
    up_at = data.get("up_at")
    if up_at is not None:
        if not isinstance(up_at, str):
            raise ValueError("state up_at is not a string")
        datetime.datetime.fromisoformat(up_at)
    cameras = _name_list(data.get("cameras"))
    detectors = _name_list(data.get("detectors"))
    if cameras is None or detectors is None:
        raise ValueError("state has no camera or detector baseline")
    return {
        "phase": phase,
        "from_ref": from_ref,
        "from_version": from_version,
        "to_ref": to_ref,
        "to_version": to_version,
        "backup_dir": backup_dir,
        "up_at": up_at,
        "cameras": cameras,
        "detectors": detectors,
    }


def fsync_dir(path):
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    fd = os.open(path, flags)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def refuse_write(what):
    if RUN.dry_run:
        raise RuntimeError(f"dry-run tried to write {what}")


def atomic_write(path, data, use_reserve=None):
    refuse_write(path)
    directory = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".frigate-update-", suffix=".tmp")
    tmp_left = tmp
    try:
        if use_reserve is not None and remaining(use_reserve) <= 0:
            raise BudgetExhausted("write")
        os.write(fd, data)
        if use_reserve is not None and remaining(use_reserve) <= 0:
            raise BudgetExhausted("write")
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
        tmp_left = None
        fsync_dir(directory)
    finally:
        if fd >= 0:
            os.close(fd)
        if tmp_left is not None:
            try:
                os.unlink(tmp_left)
            except FileNotFoundError:
                pass


def atomic_write_text(path, text, use_reserve=None):
    atomic_write(path, text.encode("utf-8"), use_reserve=use_reserve)


def durable_unlink(path):
    refuse_write(path)
    if not os.path.lexists(path):
        return
    os.unlink(path)
    fsync_dir(os.path.dirname(path))


def ensure_dir(path):
    refuse_write(path)
    if os.path.isdir(path):
        return
    os.mkdir(path)
    fsync_dir(os.path.dirname(path))


def _read_chunk(handle, size):
    return handle.read(size)


def _copy_chunks(src_f, write_chunk, sync, use_reserve):
    # frigate.db is about 155 MB. One read of the whole file can run past
    # the forward budget into the time reserved for starting Frigate again.
    while True:
        if remaining(use_reserve) <= 0:
            raise BudgetExhausted("copy")
        chunk = _read_chunk(src_f, COPY_CHUNK_BYTES)
        if not chunk:
            break
        write_chunk(chunk)
    if remaining(use_reserve) <= 0:
        raise BudgetExhausted("copy")
    sync()


def copy_durable(src, dst, use_reserve):
    refuse_write(dst)
    size = os.path.getsize(src)
    with open(src, "rb") as src_f, open(dst, "wb") as dst_f:
        _copy_chunks(src_f, dst_f.write, lambda: (dst_f.flush(), os.fsync(dst_f.fileno())), use_reserve)
    if os.path.getsize(dst) != size or os.path.getsize(src) != size:
        raise OSError(f"size changed while copying {os.path.basename(src)}")
    os.chmod(dst, 0o644)


def restore_durable(src, dst, use_reserve):
    # Temp file in the destination directory, then replace. frigate.db is
    # root-owned and mode 0644, so kyle can unlink it but cannot write it
    # in place. A power cut leaves either the old file or the new one.
    refuse_write(dst)
    directory = os.path.dirname(dst)
    size = os.path.getsize(src)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".frigate-restore-", suffix=".tmp")
    tmp_left = tmp
    try:
        with open(src, "rb") as src_f:
            def write_chunk(chunk, dest=fd):
                os.write(dest, chunk)

            def sync(dest=fd):
                os.fsync(dest)

            _copy_chunks(src_f, write_chunk, sync, use_reserve)
        os.close(fd)
        fd = -1
        os.chmod(tmp, 0o644)
        os.replace(tmp, dst)
        tmp_left = None
        fsync_dir(directory)
    finally:
        if fd >= 0:
            os.close(fd)
        if tmp_left is not None:
            try:
                os.unlink(tmp_left)
            except FileNotFoundError:
                pass
    if os.path.getsize(dst) != size:
        raise OSError(f"restored {os.path.basename(dst)} size does not match the backup")


def assert_cmd_allowed(argv):
    if not RUN.dry_run:
        return
    if len(argv) >= 2 and argv[0] == DOCKER and argv[1] == "compose":
        raise RuntimeError("dry-run issued docker compose")
    if len(argv) >= 3 and argv[0] == DOCKER and argv[1] == "image" and argv[2] == "rm":
        raise RuntimeError("dry-run issued docker image rm")


def run_cmd(argv, cap, use_reserve, check=True):
    assert_cmd_allowed(argv)
    for arg in argv:
        if not isinstance(arg, str) or "\n" in arg or "\x00" in arg:
            raise Fail("error", "refusing a command argument that is not a single line")
    budget = remaining(use_reserve)
    timeout = min(float(cap), budget)
    if timeout <= 0:
        raise BudgetExhausted(" ".join(argv[:3]))
    shown = " ".join(argv)
    log(f"run {shown[:300]} (timeout {timeout:.0f}s)")
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            timeout=timeout,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
        )
    except subprocess.TimeoutExpired:
        # The docker CLI is dead. The daemon may still be finishing the
        # same stop or up, so the caller inspects instead of assuming.
        log(f"timed out {argv[0]} {argv[1] if len(argv) > 1 else ''}")
        raise CmdTimeout()
    if check and proc.returncode != 0:
        err = clip_err(proc.stderr)
        log(f"rc={proc.returncode} {argv[0]} {argv[1] if len(argv) > 1 else ''}: {err}")
        raise CmdFailed(proc.returncode, err, argv)
    return proc


def finish(kind, detail):
    if kind not in EXIT_CODES:
        kind = "broken"
        detail = "internal: unknown outcome"
    detail = " ".join(detail.split())
    if not detail:
        detail = kind
    if RUN.dry_run and "(dry-run)" not in detail:
        detail = detail + " (dry-run)"
    if not RUN.dry_run and kind != "skipped":
        try:
            notify(kind, detail)
        except Exception as exc:
            log(f"notify failed: {short(exc)}")
    print(f"OUTCOME {kind} {detail}", flush=True)
    raise SystemExit(EXIT_CODES[kind])


def notify(kind, detail):
    # Single alerting seam. A later monitoring ping belongs in this
    # function; callers keep passing kind and detail only.
    version = None
    try:
        version = read_running_version(use_reserve=True)
    except Exception:
        version = None
    payload = {
        "time": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "kind": kind,
        "detail": detail,
        "version": version,
    }
    atomic_write_text(STATUS_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def read_running_version(use_reserve):
    proc = run_cmd(
        [DOCKER, "exec", CONTAINER, "cat", VERSION_PATH],
        EXEC_CAP_S,
        use_reserve,
    )
    if len(proc.stdout) > 64 * 1024:
        raise ValueError("running version.py is too large")
    return parse_version_py(proc.stdout)


def image_version(ref, use_reserve):
    if not valid_ref(ref):
        raise Fail("error", "image ref is not a plain reference")
    proc = run_cmd(
        [DOCKER, "run", "--rm", "--entrypoint", "cat", ref, VERSION_PATH],
        RUN_CAT_CAP_S,
        use_reserve,
    )
    if len(proc.stdout) > 64 * 1024:
        raise Fail("error", f"version.py from {ref} is too large")
    try:
        return parse_version_py(proc.stdout)
    except ValueError as exc:
        raise Fail("error", f"version.py from {ref}: {exc}") from exc


def image_id(ref, use_reserve):
    if not valid_ref(ref):
        raise Fail("error", "image ref is not a plain reference")
    proc = run_cmd(
        [DOCKER, "image", "inspect", "-f", "{{.Id}}", ref],
        INSPECT_CAP_S,
        use_reserve,
    )
    value = proc.stdout.strip()
    if not value or "\n" in value:
        raise Fail("error", f"no image id for {ref}")
    return value


def inspect_format(template, use_reserve):
    try:
        proc = run_cmd(
            [DOCKER, "inspect", "-f", template, CONTAINER],
            INSPECT_CAP_S,
            use_reserve,
        )
    except (CmdFailed, CmdTimeout, BudgetExhausted):
        return None
    value = proc.stdout.strip()
    if not value or value == "<no value>":
        return None
    return value


def inspect_status(use_reserve):
    return inspect_format("{{.State.Status}}", use_reserve)


def inspect_health(use_reserve):
    return inspect_format("{{.State.Health.Status}}", use_reserve)


def inspect_restart_count(use_reserve):
    raw = inspect_format("{{.RestartCount}}", use_reserve)
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def inspect_started_at(use_reserve):
    raw = inspect_format("{{.State.StartedAt}}", use_reserve)
    if raw is None:
        return None
    try:
        return parse_docker_time(raw)
    except ValueError:
        return None


def stopped_status(status):
    return status in {"exited", "dead", "created", "removing", "removed"}


def compose_stop(use_reserve):
    refuse_write("compose stop")
    try:
        run_cmd(COMPOSE_STOP, STOP_CAP_S, use_reserve)
    except CmdTimeout:
        # The CLI is gone. The daemon may still be stopping the container.
        log("compose stop timed out; inspecting the container")
        return True
    except CmdFailed:
        log("compose stop returned non-zero; inspecting the container")
    return False


def poll_stopped(use_reserve, seconds):
    deadline = time.monotonic() + seconds
    while True:
        status = inspect_status(use_reserve)
        log(f"frigate status after stop: {status}")
        if stopped_status(status):
            return True
        if time.monotonic() >= deadline:
            return False
        pause = min(2.0, deadline - time.monotonic())
        if pause <= 0 or not sleep_for(pause, use_reserve):
            return stopped_status(inspect_status(use_reserve))


def compose_up(use_reserve):
    refuse_write("compose up")
    try:
        run_cmd(COMPOSE_UP, UP_CAP_S, use_reserve)
        return True
    except CmdTimeout:
        log("compose up timed out; inspecting the container")
    except CmdFailed:
        log("compose up returned non-zero; inspecting the container")
    return False


def ensure_stopped(use_reserve):
    for attempt in (1, 2):
        timed_out = compose_stop(use_reserve)
        # After a timeout the daemon can still be stopping. Wait before
        # deciding the container is still up, or a late stop leaves Frigate down.
        if poll_stopped(use_reserve, STOP_POLL_S if timed_out else 2):
            return True
        if attempt == 1 and remaining(use_reserve) > STOP_CAP_S:
            continue
        return False
    return False


def read_text(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def read_compose_image():
    try:
        text = read_text(COMPOSE_PATH)
    except OSError as exc:
        kind = "broken" if os.path.exists(STATE_PATH) else "error"
        raise Fail(kind, f"cannot read compose: {exc.strerror or exc.__class__.__name__}")
    try:
        return parse_compose_image(text)
    except ValueError as exc:
        kind = "broken" if os.path.exists(STATE_PATH) else "error"
        raise Fail(kind, f"compose image line: {exc}")


def load_state():
    if not os.path.exists(STATE_PATH):
        return None
    try:
        text = read_text(STATE_PATH)
    except OSError as exc:
        raise Fail("broken", f"cannot read state file: {exc.strerror or exc.__class__.__name__}")
    try:
        return decode_state(text)
    except ValueError as exc:
        raise Fail("broken", f"state file is malformed: {exc}")


def persist(state):
    if state["phase"] not in PHASES:
        raise Fail("broken", "refusing to persist an unknown phase")
    encoded = encode_state(state)
    decode_state(encoded)
    atomic_write_text(STATE_PATH, encoded)
    RUN.state = dict(state)
    if state["phase"] == "switched":
        RUN.switched = True
    if state["phase"] == "restored":
        RUN.phase_restored = True
        RUN.switched = True
    if state["phase"] == "rolling-back":
        RUN.switched = True


def clear_state():
    durable_unlink(STATE_PATH)
    RUN.state = None


def persist_failed(state):
    failed = dict(state)
    failed["phase"] = "failed"
    try:
        persist(failed)
    except Exception as exc:
        log(f"could not persist phase failed: {short(exc)}")


def load_hold():
    if not os.path.exists(HOLD_PATH):
        return set()
    try:
        text = read_text(HOLD_PATH)
    except OSError as exc:
        raise Fail("error", f"cannot read hold file: {exc.strerror or exc.__class__.__name__}")
    try:
        return parse_hold(text)
    except ValueError as exc:
        raise Fail("error", f"hold file is malformed: {exc}")


def append_hold(version):
    if os.path.exists(HOLD_PATH):
        text = read_text(HOLD_PATH)
    else:
        text = ""
    updated = render_hold(text, version)
    if updated == text:
        return
    atomic_write_text(HOLD_PATH, updated)


def api_json(url, use_reserve):
    proc = run_cmd(
        [DOCKER, "exec", CONTAINER, "curl", "-s", url],
        EXEC_CAP_S,
        use_reserve,
    )
    if len(proc.stdout) > 2 * 1024 * 1024:
        raise ValueError("api json is too large")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("api json is malformed") from exc
    if not isinstance(data, dict):
        raise ValueError("api json is not an object")
    return data


def enabled_cameras(config):
    cameras = config.get("cameras")
    if not isinstance(cameras, dict):
        raise ValueError("api config has no cameras object")
    names = []
    for name, body in cameras.items():
        if not isinstance(name, str) or not isinstance(body, dict):
            raise ValueError("api config camera entry is malformed")
        if body.get("enabled", True) is False:
            continue
        names.append(name)
    return names


def detector_names(stats):
    detectors = stats.get("detectors")
    if not isinstance(detectors, dict):
        raise ValueError("api stats is missing detectors")
    names = []
    for name, body in detectors.items():
        if not isinstance(name, str) or not isinstance(body, dict):
            raise ValueError("api stats detector entry is malformed")
        names.append(name)
    return names


def recording_gap(config, stats, cameras, detectors):
    # Healthy means the cameras and detectors that were recording before
    # the update are still recording. An empty list is not a pass.
    if not cameras:
        return "no enabled cameras"
    if not detectors:
        return "no detectors"
    configured = config.get("cameras")
    if not isinstance(configured, dict):
        raise ValueError("api config has no cameras object")
    cam_stats = stats.get("cameras")
    det_stats = stats.get("detectors")
    if not isinstance(cam_stats, dict) or not isinstance(det_stats, dict):
        raise ValueError("api stats is missing cameras or detectors")
    for name in cameras:
        cam = configured.get(name)
        if not isinstance(cam, dict):
            return f"camera {name} is missing from config"
        if cam.get("enabled", True) is False:
            return f"camera {name} is disabled"
        body = cam_stats.get(name)
        if not isinstance(body, dict):
            return f"camera {name} is missing from stats"
        fps = body.get("camera_fps")
        if isinstance(fps, bool) or not isinstance(fps, (int, float)) or fps <= 0:
            return f"camera {name} camera_fps is {fps}"
    for name in detectors:
        body = det_stats.get(name)
        if not isinstance(body, dict):
            return f"detector {name} is missing"
        speed = body.get("inference_speed")
        if isinstance(speed, bool) or not isinstance(speed, (int, float)) or speed <= 0:
            return f"detector {name} inference_speed is {speed}"
    return ""


def cache_names(use_reserve):
    proc = run_cmd(
        [DOCKER, "exec", CONTAINER, *CACHE_LIST_ARGV_TAIL],
        EXEC_CAP_S,
        use_reserve,
        check=False,
    )
    if proc.returncode != 0:
        log(f"cache list rc={proc.returncode}: {clip_err(proc.stderr)}")
        return []
    return [line for line in proc.stdout.splitlines() if line]


def health_snapshot(target_version, up_at, require_cache, use_reserve, strict, baseline):
    status = inspect_status(use_reserve)
    if status != "running":
        return f"container status is {status}"
    health = inspect_health(use_reserve)
    if health != "healthy":
        return f"health is {health}"
    try:
        running = read_running_version(use_reserve)
    except (CmdFailed, CmdTimeout, BudgetExhausted, ValueError) as exc:
        if strict and isinstance(exc, ValueError):
            raise Fail("error", f"running version.py: {exc}")
        return "running version.py is unreadable"
    if running != target_version:
        return f"running {running} != target {target_version}"
    try:
        config = api_json(API_CONFIG, use_reserve)
        stats = api_json(API_STATS, use_reserve)
        if baseline is None:
            cameras = enabled_cameras(config)
            detectors = detector_names(stats)
        else:
            cameras, detectors = baseline
        reason = recording_gap(config, stats, cameras, detectors)
    except (CmdFailed, CmdTimeout, BudgetExhausted) as exc:
        return f"api unreachable ({exc.__class__.__name__})"
    except ValueError as exc:
        if strict:
            raise Fail("error", str(exc))
        return str(exc)
    if reason:
        return reason
    if baseline is None:
        RUN.baseline_cameras = list(cameras)
        RUN.baseline_detectors = list(detectors)
    restarts = inspect_restart_count(use_reserve)
    if restarts is None:
        return "restart count is unreadable"
    RUN.restart_count = restarts
    if not require_cache:
        return ""
    if up_at is None:
        return "no start time for the cache check"
    try:
        names = cache_names(use_reserve)
    except (CmdFailed, CmdTimeout, BudgetExhausted):
        return "cache list failed"
    for camera in cameras:
        if not any(cache_segment_is_fresh(name, camera, up_at) for name in names):
            return f"camera {camera} has no new cache segment"
    return ""


def sleep_for(seconds, use_reserve):
    if remaining(use_reserve) < seconds:
        return False
    time.sleep(seconds)
    return remaining(use_reserve) >= 0


def wait_healthy(target_version, up_at, require_cache, use_reserve, strict, fast_version, baseline):
    deadline = time.monotonic() + min(HEALTH_TIMEOUT_S, max(0.0, remaining(use_reserve)))
    last = "health check did not run"
    restarts = None
    captured = baseline
    while True:
        if time.monotonic() >= deadline:
            return last
        last = health_snapshot(
            target_version, up_at, require_cache, use_reserve, strict, captured
        )
        if last == "":
            if captured is None:
                captured = (list(RUN.baseline_cameras), list(RUN.baseline_detectors))
            restarts = RUN.restart_count
            break
        if captured is None and last in ("no enabled cameras", "no detectors"):
            return last
        if fast_version and last.startswith("running ") and " != target " in last:
            return last
        log(f"health: {last}")
        pause = min(HEALTH_POLL_S, deadline - time.monotonic())
        if pause <= 0:
            return last
        if not sleep_for(pause, use_reserve):
            return last
    if not sleep_for(HEALTH_SETTLE_S, use_reserve):
        return "budget ran out before the 60s settle re-check"
    last = health_snapshot(
        target_version, up_at, require_cache=False, use_reserve=use_reserve, strict=strict,
        baseline=captured,
    )
    if last:
        return f"settle re-check failed: {last}"
    if RUN.restart_count != restarts:
        return f"restart count changed from {restarts} to {RUN.restart_count}"
    return ""


def require_already_healthy(version):
    status = inspect_status(use_reserve=False)
    if status != "running":
        raise Fail("refused", f"frigate is not running (status {status})")
    reason = wait_healthy(
        version,
        up_at=None,
        require_cache=False,
        use_reserve=False,
        strict=True,
        fast_version=True,
        baseline=None,
    )
    if reason:
        raise Fail("refused", f"frigate is not healthy: {reason}")
    if not RUN.baseline_cameras or not RUN.baseline_detectors:
        raise Fail("refused", "frigate has no enabled cameras or detectors")


def disk_need():
    total = 0
    for path in (COMPOSE_PATH, CONFIG_PATH, DB_PATH):
        if not os.path.isfile(path):
            raise Fail("error", f"missing {path}")
        size = os.path.getsize(path)
        if size <= 0:
            raise Fail("error", f"{path} is empty")
        total += size
    for path in (DB_WAL_PATH, DB_SHM_PATH):
        if os.path.isfile(path):
            total += os.path.getsize(path)
    return DISK_HEADROOM * total


def require_room(from_version, to_version):
    need = disk_need()
    free = shutil.disk_usage(FRIGATE_DIR).free
    if free < need:
        raise Fail(
            "refused",
            f"free space {free} bytes is under {need} bytes for apply and rollback",
        )
    left = remaining(use_reserve=True)
    # remaining(True) is the whole clock, including the reserve.
    if left < APPLY_NEED_S + ROLLBACK_RESERVE_S:
        raise Fail(
            "refused",
            f"time left {left:.0f}s cannot cover apply ({APPLY_NEED_S}s) and rollback reserve ({ROLLBACK_RESERVE_S}s) for {from_version} -> {to_version}",
        )


def pull(ref):
    if not valid_ref(ref):
        raise Fail("error", "image ref is not a plain reference")
    try:
        run_cmd([DOCKER, "pull", ref], PULL_CAP_S, use_reserve=False)
    except CmdTimeout:
        raise Fail("error", f"pull timed out for {ref}")
    except CmdFailed as exc:
        raise Fail("error", f"pull failed for {ref}: rc={exc.returncode} {exc.err}")
    except BudgetExhausted:
        raise Fail("error", f"no time left to pull {ref}")


def evaluate(candidate):
    from_ref = read_compose_image()
    try:
        from_version = image_version(from_ref, use_reserve=False)
    except (CmdFailed, CmdTimeout, BudgetExhausted) as exc:
        raise Fail("error", f"cannot read the running image version: {short(exc)}")
    if not valid_version(from_version):
        raise Fail("error", f"running image version {from_version!r} is not X.Y.Z")
    require_already_healthy(from_version)
    held = load_hold()
    if candidate is not None:
        to_ref = candidate
        try:
            to_version = image_version(candidate, use_reserve=False)
        except (CmdFailed, CmdTimeout, BudgetExhausted) as exc:
            raise Fail("error", f"cannot read the candidate version: {short(exc)}")
    else:
        pull(STABLE_REF)
        try:
            stable_id = image_id(STABLE_REF, use_reserve=False)
            to_version = image_version(STABLE_REF, use_reserve=False)
        except (CmdFailed, CmdTimeout, BudgetExhausted) as exc:
            raise Fail("error", f"cannot read stable: {short(exc)}")
        if not valid_version(to_version):
            raise Fail("error", f"stable version {to_version!r} is not X.Y.Z")
        to_ref = f"{REGISTRY}:{to_version}"
        if not is_newer(to_version, from_version):
            raise Fail("current", f"running {from_version}; stable is {to_version}")
        if to_version in held:
            raise Fail("held", f"{to_version} is in the hold file")
        pull(to_ref)
        try:
            tagged_id = image_id(to_ref, use_reserve=False)
        except (CmdFailed, CmdTimeout, BudgetExhausted) as exc:
            raise Fail("error", f"cannot read image id for {to_ref}: {short(exc)}")
        if tagged_id != stable_id:
            raise Fail("error", f"tag mismatch: stable image id does not match {to_ref}")
        require_room(from_version, to_version)
        return from_ref, from_version, to_ref, to_version
    if not valid_version(to_version):
        raise Fail("error", f"candidate version {to_version!r} is not X.Y.Z")
    if not is_newer(to_version, from_version):
        raise Fail("current", f"running {from_version}; candidate is {to_version}")
    if to_version in held:
        raise Fail("held", f"{to_version} is in the hold file")
    require_room(from_version, to_version)
    return from_ref, from_version, to_ref, to_version


def backup_name(from_version, to_version):
    stamp = datetime.datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    base = f"{stamp}-{from_version}-to-{to_version}"
    for suffix in ("", "-2", "-3", "-4"):
        path = BACKUP_ROOT + "/" + base + suffix
        if _backup_dir_ok(path) and not os.path.exists(path):
            return path
    raise Fail("error", "could not allocate a backup directory")


def source_for(name):
    return LIVE_BY_BACKUP_NAME[name]


def make_backup(backup_dir, from_ref):
    # Frigate checkpoints its WAL into frigate.db while stopping. The copy
    # has to be taken after that stop, from the quiet files.
    started = time.monotonic()
    ensure_dir(BACKUP_ROOT)
    ensure_dir(backup_dir)
    assert_contained_backup(backup_dir)
    names = list(BACKUP_FILES)
    for name in OPTIONAL_DB_FILES:
        if os.path.isfile(source_for(name)):
            names.append(name)
    for name in names:
        if time.monotonic() - started > BACKUP_CAP_S or remaining(False) <= 0:
            raise BudgetExhausted("backup")
        copy_durable(source_for(name), os.path.join(backup_dir, name), False)
        if os.path.getsize(os.path.join(backup_dir, name)) != os.path.getsize(source_for(name)):
            raise OSError(f"backup size mismatch for {name}")
        fsync_dir(backup_dir)
    if parse_compose_image(read_text(os.path.join(backup_dir, "docker-compose.yml"))) != from_ref:
        raise OSError("backup compose does not hold the from-ref")
    # COMPLETE is the last directory entry. A crash before it leaves a
    # backup that recovery will not restore from.
    atomic_write_text(os.path.join(backup_dir, COMPLETE_NAME), "ok\n")
    fsync_dir(backup_dir)
    fsync_dir(BACKUP_ROOT)


def backup_is_complete(state):
    backup_dir = state["backup_dir"]
    try:
        assert_contained_backup(backup_dir)
    except (OSError, ValueError):
        return False
    marker = os.path.join(backup_dir, COMPLETE_NAME)
    if not os.path.isfile(marker) or os.path.getsize(marker) <= 0:
        return False
    for name in BACKUP_FILES:
        path = os.path.join(backup_dir, name)
        if not os.path.isfile(path) or os.path.getsize(path) <= 0:
            return False
    try:
        backed = parse_compose_image(read_text(os.path.join(backup_dir, "docker-compose.yml")))
    except (OSError, ValueError):
        return False
    return backed == state["from_ref"]


def restore_backup(state):
    if not backup_is_complete(state):
        raise OSError("backup is incomplete")
    backup_dir = state["backup_dir"]
    # Drop wal/shm the backup does not have before putting the db back,
    # so a crash cannot pair the new db with a newer wal.
    for name in OPTIONAL_DB_FILES:
        live = source_for(name)
        backed = os.path.join(backup_dir, name)
        if not os.path.isfile(backed) and os.path.lexists(live):
            durable_unlink(live)
    for name in BACKUP_FILES:
        restore_durable(os.path.join(backup_dir, name), source_for(name), True)
    for name in OPTIONAL_DB_FILES:
        backed = os.path.join(backup_dir, name)
        if os.path.isfile(backed):
            restore_durable(backed, source_for(name), True)
    if read_compose_image() != state["from_ref"]:
        raise OSError("compose ref after restore is not the from-ref")


def prune_backups():
    if not os.path.isdir(BACKUP_ROOT):
        return
    rows = []
    for name in os.listdir(BACKUP_ROOT):
        path = os.path.join(BACKUP_ROOT, name)
        if os.path.islink(path) or not os.path.isdir(path):
            continue
        if not _backup_dir_ok(BACKUP_ROOT + "/" + name):
            continue
        complete = os.path.isfile(os.path.join(path, COMPLETE_NAME))
        rows.append((name, path, complete))
    rows.sort()
    complete_paths = [path for _, path, complete in rows if complete]
    keep = set(complete_paths[-KEEP_BACKUPS:])
    for _, path, _complete in rows:
        if path in keep:
            continue
        # Incomplete directories are not among the seven kept.
        shutil.rmtree(path)
    fsync_dir(BACKUP_ROOT)


def prune_images(keep_versions):
    try:
        proc = run_cmd(
            [DOCKER, "image", "ls", "--format", "{{.Repository}}:{{.Tag}}", REGISTRY],
            IMAGE_LS_CAP_S,
            use_reserve=True,
        )
    except (CmdFailed, CmdTimeout, BudgetExhausted) as exc:
        log(f"image list failed: {short(exc)}")
        return
    prefix = REGISTRY + ":"
    for line in proc.stdout.splitlines():
        ref = line.strip()
        if not ref.startswith(prefix):
            continue
        tag = ref[len(prefix):]
        if not valid_version(tag) or tag in keep_versions:
            continue
        if not valid_ref(ref):
            continue
        try:
            run_cmd([DOCKER, "image", "rm", ref], IMAGE_RM_CAP_S, use_reserve=True)
            log(f"removed image {ref}")
        except (CmdFailed, CmdTimeout, BudgetExhausted) as exc:
            log(f"could not remove {ref}: {short(exc)}")


def config_change_detail(backup_dir):
    try:
        before = read_text(os.path.join(backup_dir, "config.yml"))
        after = read_text(CONFIG_PATH)
    except OSError as exc:
        return f"; config comparison failed ({exc.__class__.__name__})"
    if before.splitlines() == after.splitlines():
        return ""
    changed = line_change_count(before, after)
    return f"; config rewritten, {changed} lines changed, backup {backup_dir}"


def finalize_success(state):
    clear_state()
    try:
        prune_backups()
    except Exception as exc:
        log(f"backup prune failed: {short(exc)}")
    try:
        prune_images({state["from_version"], state["to_version"]})
    except Exception as exc:
        log(f"image prune failed: {short(exc)}")
    detail = f"{state['from_version']} -> {state['to_version']}"
    detail += config_change_detail(state["backup_dir"])
    finish("updated", detail)


def pick_up_at(state, before, after):
    now = datetime.datetime.now().astimezone().replace(microsecond=0)
    same = (
        before is not None
        and after is not None
        and abs((after - before).total_seconds()) < 1
    )
    if same:
        if state.get("up_at"):
            try:
                return datetime.datetime.fromisoformat(state["up_at"])
            except ValueError:
                return before
        return before
    return now


def expected_ref(state, version):
    if version == state["to_version"]:
        return state["to_ref"]
    if version == state["from_version"]:
        return state["from_ref"]
    return None


def try_up_and_health(state, version, use_reserve):
    try:
        want = expected_ref(state, version)
        if want is None or read_compose_image() != want:
            log(f"compose ref is not the ref for {version}")
            return False
        before = inspect_started_at(use_reserve)
        compose_up(use_reserve)
        after = inspect_started_at(use_reserve)
        status = inspect_status(use_reserve)
        if status != "running":
            compose_up(use_reserve)
            after = inspect_started_at(use_reserve)
        up_at = pick_up_at(state, before, after)
        state["up_at"] = up_at.isoformat(timespec="seconds")
        if state.get("phase") in PHASES and state["phase"] != "failed":
            try:
                persist(state)
            except Exception as exc:
                log(f"could not persist up_at: {short(exc)}")
        reason = wait_healthy(
            version,
            up_at,
            require_cache=True,
            use_reserve=use_reserve,
            strict=False,
            fast_version=False,
            baseline=(state["cameras"], state["detectors"]),
        )
        if reason:
            log(f"health failed for {version}: {reason}")
            return False
        return True
    except Exception as exc:
        log(f"start of {version} failed: {short(exc)}")
        return False


def abort_back_to_from(state, detail):
    if RUN.bringing_back:
        finish("rollback-failed", detail + "; nested abort")
    RUN.bringing_back = True
    try:
        ref = read_compose_image()
    except Fail as exc:
        persist_failed(state)
        finish("rollback-failed", detail + f"; compose unreadable: {exc.detail}")
    if ref != state["from_ref"]:
        RUN.switched = True
        RUN.bringing_back = False
        rollback(state, detail + "; compose was already on the new ref")
        return
    if try_up_and_health(state, state["from_version"], use_reserve=True):
        try:
            clear_state()
        except Exception as exc:
            log(f"could not clear state after abort: {short(exc)}")
        finish("error", detail + f"; {state['from_version']} is healthy")
    persist_failed(state)
    finish(
        "rollback-failed",
        detail + f"; {state['from_version']} did not come back healthy",
    )


def rollback(state, detail):
    # Once phase is restored the from-version may record. Recovery must
    # not copy the backup over that database again.
    if RUN.bringing_back and state.get("phase") == "failed":
        finish("rollback-failed", detail + "; nested rollback")
    RUN.bringing_back = True
    RUN.phase_restored = False
    if not backup_is_complete(state):
        persist_failed(state)
        finish("rollback-failed", detail + "; backup incomplete, nothing restored")
    rolling = dict(state)
    rolling["phase"] = "rolling-back"
    rolling["up_at"] = None
    persist(rolling)
    if not ensure_stopped(use_reserve=True):
        persist_failed(rolling)
        finish("rollback-failed", detail + "; could not stop frigate to restore")
    try:
        restore_backup(rolling)
    except BudgetExhausted as exc:
        # Stay on rolling-back so the next run redoes the restore. Marking
        # failed here would leave a half-copied database with no retry.
        finish("rollback-failed", detail + f"; restore ran out of time ({short(exc)}); phase left rolling-back")
    except Exception as exc:
        persist_failed(rolling)
        finish("rollback-failed", detail + f"; restore failed: {short(exc)}")
    restored = dict(rolling)
    restored["phase"] = "restored"
    persist(restored)
    if not try_up_and_health(restored, restored["from_version"], use_reserve=True):
        persist_failed(restored)
        finish(
            "rollback-failed",
            detail + f"; files restored but {restored['from_version']} is not healthy",
        )
    try:
        append_hold(restored["to_version"])
    except Exception as exc:
        finish(
            "error",
            detail
            + f"; restored {restored['from_version']} but the hold file was not updated: {short(exc)}",
        )
    try:
        clear_state()
    except Exception as exc:
        log(f"could not clear state after rollback: {short(exc)}")
    finish(
        "rolled-back",
        f"{restored['to_version']} failed health; restored {restored['from_version']} and held {restored['to_version']}",
    )


def finish_rollback_success(state):
    try:
        append_hold(state["to_version"])
    except Exception as exc:
        finish(
            "error",
            f"restored {state['from_version']} but the hold file was not updated: {short(exc)}",
        )
    try:
        clear_state()
    except Exception as exc:
        log(f"could not clear state: {short(exc)}")
    finish(
        "rolled-back",
        f"restored {state['from_version']} and held {state['to_version']}",
    )


def rewrite_to(ref):
    refuse_write("compose")
    if not valid_ref(ref):
        raise Fail("error", "candidate ref is not a plain reference")
    if remaining(False) <= 0:
        raise BudgetExhausted("compose rewrite")
    text = read_text(COMPOSE_PATH)
    rewritten = rewrite_compose_image(text, ref)
    atomic_write_text(COMPOSE_PATH, rewritten, use_reserve=False)
    RUN.switched = True
    if read_compose_image() != ref:
        raise OSError("compose image line did not update")


def apply(from_ref, from_version, to_ref, to_version):
    if not RUN.baseline_cameras or not RUN.baseline_detectors:
        raise Fail("refused", "no enabled cameras or detectors were recorded")
    backup_dir = backup_name(from_version, to_version)
    state = {
        "phase": "applying",
        "from_ref": from_ref,
        "from_version": from_version,
        "to_ref": to_ref,
        "to_version": to_version,
        "backup_dir": backup_dir,
        "up_at": None,
        "cameras": list(RUN.baseline_cameras),
        "detectors": list(RUN.baseline_detectors),
    }
    # Phase hits disk before stop. A kill here leaves compose untouched.
    persist(state)
    RUN.stop_issued = True
    try:
        if not ensure_stopped(use_reserve=False):
            # up -d again, including when stop timed out and the container
            # still looked running. A late stop must not be the last word.
            abort_back_to_from(state, "could not stop frigate")
            return
        try:
            make_backup(backup_dir, from_ref)
        except Exception as exc:
            abort_back_to_from(state, f"backup failed: {short(exc)}")
            return
        state["phase"] = "backed-up"
        persist(state)
        try:
            rewrite_to(to_ref)
        except Exception as exc:
            switched = RUN.switched
            if not switched:
                try:
                    switched = read_compose_image() == to_ref
                except Fail:
                    switched = False
            if switched:
                RUN.switched = True
                rollback(state, f"compose switched but was not confirmed: {short(exc)}")
                return
            abort_back_to_from(state, f"compose rewrite failed: {short(exc)}")
            return
        state["phase"] = "switched"
        persist(state)
        if not try_up_and_health(state, to_version, use_reserve=False):
            rollback(state, f"{to_version} failed health")
            return
        RUN.target_healthy = True
        finalize_success(state)
    except (SystemExit, Fail):
        raise
    except Exception as exc:
        safety_net(exc)


def recover_from_side(state):
    ref = read_compose_image()
    if ref != state["from_ref"]:
        persist_failed(state)
        finish(
            "broken",
            f"phase {state['phase']} but compose is {ref}, expected {state['from_ref']}",
        )
    if try_up_and_health(state, state["from_version"], use_reserve=True):
        try:
            clear_state()
        except Exception as exc:
            log(f"could not clear state after recovery: {short(exc)}")
        finish("recovered", f"phase {state['phase']}; {state['from_version']} is healthy")
    persist_failed(state)
    finish("broken", f"phase {state['phase']}; {state['from_version']} did not come up healthy")


def recover_to_side(state):
    ref = read_compose_image()
    if ref != state["to_ref"] and state["phase"] == "switched":
        log(f"phase switched but compose is {ref}; health-check will decide")
    if try_up_and_health(state, state["to_version"], use_reserve=False):
        RUN.target_healthy = True
        finalize_success(state)
        return
    rollback(state, f"recovery of {state['to_version']} failed health")


def recover(state):
    phase = state["phase"]
    log(f"recovering phase {phase} backup {state['backup_dir']}")
    RUN.state = dict(state)
    if phase == "failed":
        finish("broken", "phase failed; leaving frigate untouched and alerting again")
    # A previous run may already have stopped Frigate. From here on, an
    # unexpected exit has to start a version again or alert.
    RUN.stop_issued = True
    if phase in {"switched", "rolling-back", "restored"}:
        RUN.switched = True
    if phase == "restored":
        RUN.phase_restored = True
    if phase == "applying":
        recover_from_side(state)
        return
    if phase == "backed-up":
        ref = read_compose_image()
        if ref == state["from_ref"]:
            recover_from_side(state)
            return
        if ref == state["to_ref"]:
            RUN.switched = True
            recover_to_side(state)
            return
        persist_failed(state)
        finish("broken", f"phase backed-up but compose is {ref}")
    if phase == "switched":
        RUN.switched = True
        recover_to_side(state)
        return
    if phase == "rolling-back":
        rollback(state, f"redoing an interrupted restore of {state['from_version']}")
        return
    if phase == "restored":
        RUN.phase_restored = True
        RUN.switched = True
        RUN.bringing_back = True
        if read_compose_image() != state["from_ref"]:
            persist_failed(state)
            finish(
                "broken",
                f"phase restored but compose is not {state['from_ref']}; not restoring again",
            )
        if try_up_and_health(state, state["from_version"], use_reserve=True):
            finish_rollback_success(state)
            return
        persist_failed(state)
        finish(
            "rollback-failed",
            f"phase restored; {state['from_version']} did not come up healthy",
        )
    persist_failed(state)
    finish("broken", f"phase {phase} is not recoverable")


def describe_recovery(state):
    phase = state["phase"]
    if phase == "failed":
        return "broken", "phase failed; a real run would alert again and change nothing"
    try:
        ref = read_compose_image()
    except Fail as exc:
        return "broken", f"phase {phase}; {exc.detail}"
    if phase == "applying" and ref != state["from_ref"]:
        return "broken", f"phase applying but compose is {ref}, expected {state['from_ref']}"
    if phase == "applying" or (phase == "backed-up" and ref == state["from_ref"]):
        return (
            "recovered",
            f"phase {phase}; a real run would start {state['from_version']} and clear the state",
        )
    if phase == "switched" or (phase == "backed-up" and ref == state["to_ref"]):
        return (
            "updated",
            f"phase {phase}; a real run would health-check {state['to_version']} or roll back to {state['from_version']}",
        )
    if phase == "backed-up":
        return "broken", f"phase backed-up but compose is {ref}"
    if phase == "rolling-back":
        return (
            "rolled-back",
            f"phase rolling-back; a real run would restore {state['from_version']} and finish the rollback",
        )
    if phase == "restored":
        return (
            "rolled-back",
            f"phase restored; a real run would start {state['from_version']} and hold {state['to_version']}",
        )
    return "broken", f"phase {phase} is unknown"


def acquire_lock():
    import fcntl

    if RUN.dry_run and not os.path.exists(LOCK_PATH):
        log("no lock file; dry-run will not create one")
        return
    flags = os.O_RDWR
    if not RUN.dry_run:
        flags |= os.O_CREAT
    fd = os.open(LOCK_PATH, flags, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        os.close(fd)
        if exc.errno in (errno.EAGAIN, errno.EACCES, errno.EWOULDBLOCK):
            finish("skipped", "lock is held")
        raise
    RUN.lock_fd = fd


def wait_for_docker():
    # This wait stays outside the rollback reserve so a slow daemon cannot
    # spend the time a later restore needs.
    deadline = time.monotonic() + min(DOCKER_READY_WAIT_S, max(0.0, remaining(False)))
    last = "docker info has not succeeded"
    while True:
        try:
            run_cmd(
                [DOCKER, "info", "--format", "{{.ServerVersion}}"],
                INFO_CAP_S,
                use_reserve=False,
            )
            return
        except (CmdFailed, CmdTimeout, BudgetExhausted) as exc:
            last = short(exc)
        if time.monotonic() >= deadline:
            kind = "broken" if os.path.exists(STATE_PATH) else "error"
            raise Fail(kind, f"docker did not become ready: {last}")
        pause = min(DOCKER_READY_POLL_S, max(0.0, deadline - time.monotonic()))
        if pause <= 0:
            kind = "broken" if os.path.exists(STATE_PATH) else "error"
            raise Fail(kind, f"docker did not become ready: {last}")
        time.sleep(pause)


def run_recover_mode():
    acquire_lock()
    if RUN.dry_run:
        state = load_state()
        if state is None:
            finish("skipped", "no interrupted run")
        kind, detail = describe_recovery(state)
        finish(kind, detail)
    wait_for_docker()
    state = load_state()
    if state is None:
        finish("skipped", "no interrupted run")
    recover(state)


def run_nightly(candidate):
    acquire_lock()
    state = load_state()
    if state is not None:
        if RUN.dry_run:
            kind, detail = describe_recovery(state)
            finish(kind, detail)
        recover(state)
        return
    from_ref, from_version, to_ref, to_version = evaluate(candidate)
    if RUN.dry_run:
        finish("updated", f"would apply {from_version} -> {to_version} ({to_ref})")
    log(f"applying {from_version} -> {to_version}")
    apply(from_ref, from_version, to_ref, to_version)


def safety_net(exc):
    if isinstance(exc, (Interrupted, KeyboardInterrupt)):
        raise exc
    detail = f"unexpected {exc.__class__.__name__}: {short(exc)}"
    log(detail)
    state = RUN.state
    if RUN.bringing_back:
        # The phase already on disk is the resume point. Overwriting it
        # with failed would skip the restore the next run is supposed to finish.
        finish("rollback-failed", detail + "; did not finish bringing Frigate back")
    if RUN.target_healthy and state is not None:
        try:
            finalize_success(state)
        except SystemExit:
            raise
        except Exception as inner:
            finish("updated", f"{state['from_version']} -> {state['to_version']}; finalize hit {short(inner)}")
    if not RUN.stop_issued or state is None:
        finish("error", detail)
    if RUN.phase_restored:
        RUN.bringing_back = True
        if try_up_and_health(state, state["from_version"], use_reserve=True):
            finish_rollback_success(state)
        persist_failed(state)
        finish("rollback-failed", detail + f"; {state['from_version']} did not come back healthy")
    if RUN.switched:
        rollback(state, detail)
        return
    abort_back_to_from(state, detail)


def parse_args(argv):
    dry_run = False
    recover = False
    candidate = None
    args = argv[1:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--dry-run":
            dry_run = True
        elif arg == "--recover":
            recover = True
        elif arg == "--candidate":
            index += 1
            if index >= len(args):
                raise Fail("error", "--candidate needs an image ref")
            candidate = args[index]
        elif arg.startswith("--candidate="):
            candidate = arg.split("=", 1)[1]
        else:
            raise Fail("error", f"unknown argument {arg}")
        index += 1
    if candidate is not None and not valid_ref(candidate):
        raise Fail("error", "candidate ref is not a plain image reference")
    if recover and candidate is not None:
        raise Fail("error", "--recover cannot be combined with --candidate")
    return dry_run, recover, candidate


def install_signals():
    def handle(signum, _frame):
        raise Interrupted()

    try:
        signal.signal(signal.SIGTERM, handle)
    except (ValueError, OSError):
        return


def report_interrupted():
    # Read the phase. Do not write it, and do not call notify: an
    # interrupted run must not replace the last real status.
    phase = None
    try:
        if os.path.exists(STATE_PATH):
            phase = decode_state(read_text(STATE_PATH))["phase"]
    except (OSError, ValueError):
        phase = None
    if phase is None and isinstance(RUN.state, dict) and RUN.state.get("phase") in PHASES:
        phase = RUN.state["phase"]
    if phase is None:
        phase = "none"
    print(f"OUTCOME error interrupted at phase {phase}; the next run resumes", flush=True)
    raise SystemExit(EXIT_CODES["error"])


def main(argv):
    start_clock()
    RUN.dry_run = "--dry-run" in argv
    install_signals()
    try:
        dry_run, recover_mode, candidate = parse_args(argv)
        RUN.dry_run = dry_run
        if recover_mode:
            run_recover_mode()
        else:
            run_nightly(candidate)
        finish("error", "run ended without an outcome")
    except (Interrupted, KeyboardInterrupt):
        report_interrupted()
    except Fail as exc:
        finish(exc.kind, exc.detail)
    except SystemExit:
        raise
    except Exception as exc:
        safety_net(exc)


if __name__ == "__main__":
    main(sys.argv)
