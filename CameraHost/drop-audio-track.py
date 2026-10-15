#!/usr/bin/env python3
# Drop the silent AAC track from already-saved outdoor recordings.
#
# Frigate 0.18.1 kept its default audio output args on outdoor, which sends
# no sound, so each 10-second chunk holds one 128 ms AAC frame at t=0.
# nginx-vod refuses to join chunks whose track counts differ, and a playback
# range that starts mid-chunk cuts that frame off the first chunk: HTTP 503.
# New chunks will be video-only from the config. This repairs the ones
# already on disk by renaming the audio trak box to free, in place.
#
# Scope (plan 951.3). Findings outside this are not defects.
# Inputs: Frigate 0.18.1 mp4 chunks and the operator's arguments. None hostile.
# Helpers and dependencies: Python 3 stdlib.
# Platform: ext4 on a 5400 rpm HDD; Frigate keeps writing, and nginx-vod may
# read any chunk while this runs.
# Consumers: nginx-vod, ffmpeg/ffprobe, Frigate retention and exports.
# Invariants: (1) the only bytes changed are the 4 type bytes of one
# moov-level box (trak→free on apply, free→trak on revert). (2) stopping at
# any moment leaves every file either untouched or fully converted;
# re-running finishes the job.
# Anything outside these lines is not a defect.

import argparse
import os
import subprocess
import sys
import tempfile

MOOV_MAX = 4 * 1024 * 1024
PROGRESS_EVERY = 10000
UNEXPECTED_REPORT = 10
TYPE_TRAK = b"trak"
TYPE_FREE = b"free"
TYPE_MOOV = b"moov"
TYPE_MDIA = b"mdia"
TYPE_HDLR = b"hdlr"
HANDLER_VIDE = b"vide"
HANDLER_SOUN = b"soun"


class ParseError(Exception):
    pass


def parse_epoch(text):
    try:
        value = float(text)
    except ValueError:
        raise argparse.ArgumentTypeError("EPOCH must be a unix timestamp")
    if value < 0 or value != value:
        raise argparse.ArgumentTypeError("EPOCH must be a unix timestamp")
    return value


def camera_name(text):
    if not text or text in (".", "..") or "/" in text or "\\" in text:
        raise argparse.ArgumentTypeError("invalid camera name")
    return text


def header_fields(size32, largesize, offset, end):
    # size 1: a 64-bit size follows the type. size 0: to the end of the
    # parent, legal only as the last box in that space.
    if size32 == 1:
        if largesize is None:
            raise ParseError("truncated largesize")
        size = largesize
        hdr = 16
        if size < 16:
            raise ParseError("largesize smaller than header")
    elif size32 == 0:
        size = end - offset
        hdr = 8
        if size < 8:
            raise ParseError("zero-size box too small")
    else:
        size = size32
        hdr = 8
        if size < 8:
            raise ParseError("box size smaller than header")
    if size > end - offset:
        raise ParseError("box overruns parent")
    return size, hdr


def header_at(data, offset, end):
    if offset + 8 > end:
        raise ParseError("truncated box header")
    size32 = int.from_bytes(data[offset:offset + 4], "big")
    typ = data[offset + 4:offset + 8]
    largesize = None
    if size32 == 1:
        if offset + 16 > end:
            raise ParseError("truncated largesize")
        largesize = int.from_bytes(data[offset + 8:offset + 16], "big")
    size, hdr = header_fields(size32, largesize, offset, end)
    return size, typ, hdr


def read_header(handle, offset, file_size):
    if offset + 8 > file_size:
        raise ParseError("truncated box header")
    handle.seek(offset)
    head = handle.read(8)
    if len(head) < 8:
        raise ParseError("truncated box header")
    size32 = int.from_bytes(head[:4], "big")
    typ = head[4:8]
    largesize = None
    if size32 == 1:
        if offset + 16 > file_size:
            raise ParseError("truncated largesize")
        extra = handle.read(8)
        if len(extra) < 8:
            raise ParseError("truncated largesize")
        largesize = int.from_bytes(extra, "big")
    size, hdr = header_fields(size32, largesize, offset, file_size)
    return size, typ, hdr


def iter_boxes(data, start, end):
    offset = start
    while offset < end:
        size, typ, hdr = header_at(data, offset, end)
        yield offset, size, typ, hdr
        offset += size


def iter_top_level(handle, file_size):
    offset = 0
    while offset < file_size:
        size, typ, hdr = read_header(handle, offset, file_size)
        yield offset, size, typ, hdr
        offset += size


def track_handler(data, box_off, box_size, box_hdr):
    start = box_off + box_hdr
    end = box_off + box_size
    mdia = None
    for off, size, typ, hdr in iter_boxes(data, start, end):
        if typ == TYPE_MDIA:
            mdia = (off, size, hdr)
            break
    if mdia is None:
        return None
    m_off, m_size, m_hdr = mdia
    for off, size, typ, hdr in iter_boxes(data, m_off + m_hdr, m_off + m_size):
        if typ != TYPE_HDLR:
            continue
        # handler_type starts 8 bytes after the hdlr header
        # (version+flags, pre_defined).
        ht = off + hdr + 8
        if ht + 4 > off + size:
            return None
        return data[ht:ht + 4]
    return None


def classify_moov(data, moov_file_off, moov_size, moov_hdr):
    v = s = x = fcount = 0
    s_off = f_off = None
    for off, size, typ, hdr in iter_boxes(data, moov_hdr, moov_size):
        type_pos = moov_file_off + off + 4
        if typ == TYPE_TRAK:
            try:
                handler = track_handler(data, off, size, hdr)
            except ParseError:
                x += 1
                continue
            if handler == HANDLER_VIDE:
                v += 1
            elif handler == HANDLER_SOUN:
                s += 1
                s_off = type_pos
            else:
                x += 1
        elif typ == TYPE_FREE:
            try:
                handler = track_handler(data, off, size, hdr)
            except ParseError:
                continue
            if handler == HANDLER_SOUN:
                fcount += 1
                f_off = type_pos
    if x == 0 and v == 1 and s == 1 and fcount == 0:
        return "convertible", "", s_off
    if x == 0 and v == 1 and s == 0 and fcount == 1:
        return "converted", "", f_off
    if x == 0 and v == 1 and s == 0 and fcount == 0:
        return "video-only", "", None
    return "unexpected", f"V={v} S={s} X={x} F={fcount}", None


def classify_open(handle):
    file_size = os.fstat(handle.fileno()).st_size
    moov = None
    for off, size, typ, hdr in iter_top_level(handle, file_size):
        if typ != TYPE_MOOV:
            continue
        if moov is not None:
            raise ParseError("multiple moov")
        moov = (off, size, hdr)
    if moov is None:
        raise ParseError("no moov")
    off, size, hdr = moov
    if size > MOOV_MAX:
        raise ParseError("moov exceeds 4 MiB")
    handle.seek(off)
    data = handle.read(size)
    if len(data) != size:
        raise ParseError("truncated moov")
    return classify_moov(data, off, size, hdr)


def patch_type(handle, offset, old, new):
    handle.seek(offset)
    got = handle.read(4)
    if got != old:
        return False
    handle.seek(offset)
    wrote = handle.write(new)
    return wrote == 4


def process_file(path, mode):
    writing = mode in ("apply", "revert")
    try:
        handle = open(path, "r+b" if writing else "rb")
    except FileNotFoundError:
        return "gone", "", None
    except OSError as exc:
        return "unexpected", exc.__class__.__name__, None
    try:
        try:
            kind, reason, patch_off = classify_open(handle)
        except ParseError as exc:
            return "unexpected", str(exc), None
        if writing and mode == "apply" and kind == "convertible":
            if not patch_type(handle, patch_off, TYPE_TRAK, TYPE_FREE):
                return "unexpected", "type bytes were not trak", None
            return kind, reason, patch_off
        if writing and mode == "revert" and kind == "converted":
            if not patch_type(handle, patch_off, TYPE_FREE, TYPE_TRAK):
                return "unexpected", "type bytes were not free", None
            return kind, reason, patch_off
        return kind, reason, None
    except OSError as exc:
        return "unexpected", exc.__class__.__name__, None
    finally:
        handle.close()


def _plain_dir(entry):
    return (not entry.is_symlink()) and entry.is_dir(follow_symlinks=False)


def _plain_mp4(entry):
    return (
        (not entry.is_symlink())
        and entry.is_file(follow_symlinks=False)
        and entry.name.endswith(".mp4")
    )


def _sorted_entries(path):
    try:
        with os.scandir(path) as it:
            return sorted(it, key=lambda e: e.name)
    except FileNotFoundError:
        return []


def iter_mp4s(root, camera):
    for date_ent in _sorted_entries(root):
        if not _plain_dir(date_ent):
            continue
        for hour_ent in _sorted_entries(date_ent.path):
            if not _plain_dir(hour_ent):
                continue
            cam_path = os.path.join(hour_ent.path, camera)
            if os.path.islink(cam_path) or not os.path.isdir(cam_path):
                continue
            for file_ent in _sorted_entries(cam_path):
                if not _plain_mp4(file_ent):
                    continue
                yield file_ent.path


def process_tree(root, camera, mode, since, stdout, stderr):
    counts = {
        "convertible": 0,
        "converted": 0,
        "video-only": 0,
        "unexpected": 0,
        "gone": 0,
    }
    changed = 0
    unexpected_list = []
    n = 0
    for path in iter_mp4s(root, camera):
        if since is not None:
            try:
                mtime = os.lstat(path).st_mtime
            except FileNotFoundError:
                n += 1
                counts["gone"] += 1
                if n % PROGRESS_EVERY == 0:
                    print(f"progress {n}", file=stderr, flush=True)
                continue
            if mtime < since:
                continue
        n += 1
        if n % PROGRESS_EVERY == 0:
            print(f"progress {n}", file=stderr, flush=True)
        try:
            kind, reason, patch_off = process_file(path, mode)
        except Exception as exc:
            kind, reason, patch_off = "unexpected", exc.__class__.__name__, None
        counts[kind] += 1
        if kind == "unexpected":
            unexpected_list.append((path, reason))
        if patch_off is not None:
            changed += 1
            action = "changed" if mode == "apply" else "reverted"
            print(f"{action}\t{path}\t{patch_off}", file=stdout, flush=True)
    if mode in ("apply", "revert") and hasattr(os, "sync"):
        os.sync()
    print(
        f"convertible={counts['convertible']} converted={counts['converted']} "
        f"video-only={counts['video-only']} unexpected={counts['unexpected']} "
        f"gone={counts['gone']} changed={changed}",
        file=stderr,
        flush=True,
    )
    for path, reason in unexpected_list[:UNEXPECTED_REPORT]:
        print(f"unexpected\t{path}\t{reason}", file=stderr, flush=True)
    return 1 if counts["unexpected"] else 0


def _box(typ, payload):
    size = 8 + len(payload)
    return size.to_bytes(4, "big") + typ + payload


def _box64(typ, payload):
    size = 16 + len(payload)
    return (1).to_bytes(4, "big") + typ + size.to_bytes(8, "big") + payload


def _hdlr(handler):
    payload = b"\x00" * 8 + handler + b"\x00" * 12 + b"\x00" * 13
    return _box(b"hdlr", payload)


def _mdia(handler, total):
    mdhd = _box(b"mdhd", b"\x00" * 24)
    hdlr = _hdlr(handler)
    filled = 8 + len(mdhd) + len(hdlr)
    minf_size = total - filled
    minf = _box(b"minf", b"\x00" * (minf_size - 8))
    return _box(b"mdia", mdhd + hdlr + minf)


def _trak(handler, total):
    tkhd = _box(b"tkhd", b"\x00" * 76)
    edts = _box(b"edts", _box(b"elst", b"\x00" * 20))
    filled = 8 + len(tkhd) + len(edts)
    mdia = _mdia(handler, total - filled)
    return _box(b"trak", tkhd + edts + mdia)


def _real_chunk(mdat64=False, mdat_payload=b"\x00" * 64):
    ftyp = _box(b"ftyp", b"isom" + b"\x00" * 4 + b"isomiso2mp41mp42")
    mvhd = _box(b"mvhd", b"\x00" * 100)
    vide = _trak(HANDLER_VIDE, 1007)
    soun = _trak(HANDLER_SOUN, 561)
    udta = _box(b"udta", b"\x00" * 127)
    moov = _box(b"moov", mvhd + vide + soun + udta)
    free = _box(TYPE_FREE, b"")
    mdat = _box64(b"mdat", mdat_payload) if mdat64 else _box(b"mdat", mdat_payload)
    return ftyp + moov + free + mdat


def _simple_chunk(handlers, mdat64=False):
    ftyp = _box(b"ftyp", b"isom" + b"\x00" * 4 + b"mp41")
    mvhd = _box(b"mvhd", b"\x00" * 100)
    traks = b"".join(_trak(h, 256) for h in handlers)
    udta = _box(b"udta", b"\x00" * 8)
    moov = _box(b"moov", mvhd + traks + udta)
    free = _box(TYPE_FREE, b"")
    payload = b"\x00" * 16
    mdat = _box64(b"mdat", payload) if mdat64 else _box(b"mdat", payload)
    return ftyp + moov + free + mdat


def _overrun_chunk():
    ftyp = _box(b"ftyp", b"isom" + b"\x00" * 4 + b"isomiso2mp41mp42")
    child = (100).to_bytes(4, "big") + TYPE_TRAK + b"\x00" * 24
    moov = (40).to_bytes(4, "big") + TYPE_MOOV + child
    return ftyp + moov


def _no_moov_chunk():
    return _box(b"ftyp", b"isom" + b"\x00" * 4 + b"mp41") + _box(b"mdat", b"\x00" * 16)


def _slurp(path):
    with open(path, "rb") as handle:
        return handle.read()


def _put(directory, name, data):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, name)
    with open(path, "wb") as handle:
        handle.write(data)
    return path


def _parse_summary(stderr):
    for line in stderr.splitlines():
        if not line.startswith("convertible="):
            continue
        out = {}
        for part in line.split():
            key, _, value = part.partition("=")
            out[key] = int(value)
        return out
    return None


def _parse_actions(stdout):
    rows = []
    for line in stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            return None
        rows.append((parts[0], parts[1], int(parts[2])))
    return rows


def _only_type_bytes(old, new, offset, old_type, new_type):
    # trak and free share an 'r', so only some of the four type bytes change.
    if len(old) != len(new):
        return False
    if old[offset:offset + 4] != old_type or new[offset:offset + 4] != new_type:
        return False
    for i, (a, b) in enumerate(zip(old, new)):
        if a != b and not (offset <= i < offset + 4):
            return False
    return True


def _self_test():
    failed = 0

    def check(name, cond, detail=""):
        nonlocal failed
        if cond:
            print(f"ok {name}", flush=True)
        else:
            failed += 1
            extra = f" {detail}" if detail else ""
            print(f"FAIL {name}{extra}", flush=True)

    script = os.path.abspath(__file__)

    def run_tool(*args):
        return subprocess.run(
            [sys.executable, script, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    chunk = _real_chunk()
    check(
        "layout",
        int.from_bytes(chunk[0:4], "big") == 32
        and chunk[4:8] == b"ftyp"
        and int.from_bytes(chunk[32:36], "big") == 1819
        and chunk[36:40] == TYPE_MOOV
        and int.from_bytes(chunk[40:44], "big") == 108
        and int.from_bytes(chunk[148:152], "big") == 1007
        and int.from_bytes(chunk[1155:1159], "big") == 561
        and chunk[1159:1163] == TYPE_TRAK
        and int.from_bytes(chunk[1716:1720], "big") == 135
        and int.from_bytes(chunk[1851:1855], "big") == 8
        and chunk[1855:1859] == TYPE_FREE,
    )

    r = run_tool()
    check("args-root", r.returncode == 2)
    r = run_tool("--apply", "--revert")
    check("args-mode", r.returncode == 2)
    r = run_tool(".", "--since", "nope")
    check("args-since", r.returncode == 2)

    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, "rec")
        outdoor = os.path.join(root, "2026-01-15", "00", "outdoor")
        indoor = os.path.join(root, "2026-01-15", "00", "indoor")
        p_conv = _put(outdoor, "00.00.mp4", chunk)
        p_vo = _put(outdoor, "00.10.mp4", _simple_chunk([HANDLER_VIDE]))
        p_trunc = _put(outdoor, "00.20.mp4", chunk[:200])
        p_over = _put(outdoor, "00.30.mp4", _overrun_chunk())
        p_two = _put(
            outdoor, "00.40.mp4",
            _simple_chunk([HANDLER_VIDE, HANDLER_SOUN, HANDLER_SOUN]),
        )
        p_nomoov = _put(outdoor, "00.50.mp4", _no_moov_chunk())
        p_m64 = _put(outdoor, "01.00.mp4", _real_chunk(mdat64=True))
        p_old = _put(outdoor, "01.10.mp4", _real_chunk())
        p_in = _put(indoor, "00.00.mp4", _real_chunk())
        os.utime(p_old, (1_600_000_000, 1_600_000_000))
        originals = {
            p_conv: _slurp(p_conv),
            p_vo: _slurp(p_vo),
            p_trunc: _slurp(p_trunc),
            p_over: _slurp(p_over),
            p_two: _slurp(p_two),
            p_nomoov: _slurp(p_nomoov),
            p_m64: _slurp(p_m64),
            p_old: _slurp(p_old),
            p_in: _slurp(p_in),
        }
        bad = (p_trunc, p_over, p_two, p_nomoov)

        def same_as_original(*paths):
            return all(_slurp(p) == originals[p] for p in paths)

        r = run_tool(root)
        s = _parse_summary(r.stderr)
        check("dry-run-exit", r.returncode == 1)
        check("dry-run-stdout", r.stdout == "")
        check(
            "dry-run-counts",
            s == {
                "convertible": 3,
                "converted": 0,
                "video-only": 1,
                "unexpected": 4,
                "gone": 0,
                "changed": 0,
            },
            repr(s),
        )
        check("dry-run-bytes", same_as_original(*originals))
        unexp = [
            line for line in r.stderr.splitlines() if line.startswith("unexpected\t")
        ]
        check("unexpected-report", len(unexp) == 4, str(len(unexp)))

        r = run_tool(root, "--camera", "indoor")
        s = _parse_summary(r.stderr)
        check("exit-clean", r.returncode == 0)
        check("exit-clean-stdout", r.stdout == "")
        check(
            "exit-clean-counts",
            s == {
                "convertible": 1,
                "converted": 0,
                "video-only": 0,
                "unexpected": 0,
                "gone": 0,
                "changed": 0,
            },
            repr(s),
        )

        r = run_tool(root, "--since", "9999999999")
        s = _parse_summary(r.stderr)
        check("since-skip-all", r.returncode == 0 and r.stdout == "")
        check(
            "since-skip-counts",
            s == {
                "convertible": 0,
                "converted": 0,
                "video-only": 0,
                "unexpected": 0,
                "gone": 0,
                "changed": 0,
            },
            repr(s),
        )
        check("since-skip-bytes", same_as_original(*originals))

        r = run_tool(root, "--apply", "--since", "1600000100")
        rows = _parse_actions(r.stdout)
        s = _parse_summary(r.stderr)
        check("apply-since-exit", r.returncode == 1)
        check(
            "apply-since-counts",
            s == {
                "convertible": 2,
                "converted": 0,
                "video-only": 1,
                "unexpected": 4,
                "gone": 0,
                "changed": 2,
            },
            repr(s),
        )
        check(
            "apply-since-stdout",
            rows is not None
            and len(rows) == 2
            and all(a == "changed" and off == 1159 for a, _p, off in rows),
            repr(rows),
        )
        check(
            "bytes-apply",
            _only_type_bytes(originals[p_conv], _slurp(p_conv), 1159, TYPE_TRAK, TYPE_FREE)
            and _only_type_bytes(originals[p_m64], _slurp(p_m64), 1159, TYPE_TRAK, TYPE_FREE),
        )
        check(
            "input-untouched",
            same_as_original(p_vo, p_old, p_in, *bad),
        )

        after_since = {p: _slurp(p) for p in originals}
        r = run_tool(root, "--apply", "--since", "1600000100")
        s = _parse_summary(r.stderr)
        check("idempotent-apply-since-stdout", r.stdout == "")
        check(
            "idempotent-apply-since",
            s is not None and s["changed"] == 0 and s["converted"] == 2 and s["convertible"] == 0,
            repr(s),
        )
        check(
            "idempotent-apply-since-bytes",
            all(_slurp(p) == after_since[p] for p in originals),
        )

        r = run_tool(root, "--apply")
        rows = _parse_actions(r.stdout)
        s = _parse_summary(r.stderr)
        check(
            "apply-old",
            r.returncode == 1
            and s is not None
            and s["changed"] == 1
            and s["convertible"] == 1
            and s["converted"] == 2
            and rows is not None
            and len(rows) == 1
            and rows[0][0] == "changed"
            and rows[0][2] == 1159
            and os.path.basename(rows[0][1]) == "01.10.mp4",
            repr((s, rows)),
        )
        check(
            "bytes-apply-old",
            _only_type_bytes(originals[p_old], _slurp(p_old), 1159, TYPE_TRAK, TYPE_FREE),
        )
        check("indoor-untouched", _slurp(p_in) == originals[p_in])
        check("unexpected-bytes", same_as_original(*bad, p_vo))

        after_apply = {p: _slurp(p) for p in originals}
        r = run_tool(root, "--apply")
        s = _parse_summary(r.stderr)
        check("idempotent-apply-stdout", r.stdout == "")
        check(
            "idempotent-apply",
            s is not None and s["changed"] == 0 and s["converted"] == 3,
            repr(s),
        )
        check(
            "idempotent-apply-bytes",
            all(_slurp(p) == after_apply[p] for p in originals),
        )

        r = run_tool(root, "--revert")
        rows = _parse_actions(r.stdout)
        s = _parse_summary(r.stderr)
        check("revert-exit", r.returncode == 1)
        check(
            "revert-counts",
            s == {
                "convertible": 0,
                "converted": 3,
                "video-only": 1,
                "unexpected": 4,
                "gone": 0,
                "changed": 3,
            },
            repr(s),
        )
        check(
            "revert-stdout",
            rows is not None
            and len(rows) == 3
            and all(a == "reverted" and off == 1159 for a, _p, off in rows),
            repr(rows),
        )
        check(
            "bytes-revert",
            same_as_original(p_conv, p_m64, p_old, p_vo, p_in, *bad),
        )

        after_revert = {p: _slurp(p) for p in originals}
        r = run_tool(root, "--revert")
        s = _parse_summary(r.stderr)
        check("idempotent-revert-stdout", r.stdout == "")
        check(
            "idempotent-revert",
            s is not None and s["changed"] == 0 and s["convertible"] == 3,
            repr(s),
        )
        check(
            "idempotent-revert-bytes",
            all(_slurp(p) == after_revert[p] for p in originals),
        )

        r = run_tool("/no/such/drop-audio-root-dir")
        check("missing-root", r.returncode == 2)

    return failed == 0


def self_test():
    try:
        return _self_test()
    except Exception as exc:
        print(f"FAIL exception {exc.__class__.__name__}: {exc}", flush=True)
        return False


def main(argv):
    parser = argparse.ArgumentParser(prog="drop-audio-track.py")
    parser.add_argument("root", nargs="?")
    parser.add_argument("--camera", default="outdoor", type=camera_name)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true")
    group.add_argument("--revert", action="store_true")
    parser.add_argument("--since", type=parse_epoch, metavar="EPOCH")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv[1:])
    if args.self_test:
        return 0 if self_test() else 1
    if not args.root:
        parser.error("ROOT is required")
    if not os.path.isdir(args.root):
        parser.error("ROOT is not a directory")
    mode = "dry"
    if args.apply:
        mode = "apply"
    elif args.revert:
        mode = "revert"
    return process_tree(
        args.root, args.camera, mode, args.since, sys.stdout, sys.stderr
    )


if __name__ == "__main__":
    sys.exit(main(sys.argv))
