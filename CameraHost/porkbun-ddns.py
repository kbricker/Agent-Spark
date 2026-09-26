#!/usr/bin/env python3
# Keep one Porkbun A record equal to this house's current public IPv4.
#
# view.kylebricker.com has to follow the residential address. Until this
# script updates that one A record, the name points at whoever still has
# the old one. kyle's crontab runs it every 10 minutes.
# See camera-host-setup.md section 14.
#
# Scope (plan 1055.1). Findings outside this are not defects.
# Inputs: host-secrets.env and the crontab args (ours), plus Porkbun API
# responses over verified TLS (trusted service). Out of scope: a malicious
# Porkbun, a tampered secrets file.
# Helpers and dependencies: Python 3 stdlib, Porkbun API v3.
# Platform: GarageBox (Ubuntu), kyle's cron every 10 minutes.
# Consumers: the public A record for view.kylebricker.com; Kyle, through
# ddns.log and a healthchecks.io check-in.
# Invariants: (1) the Porkbun key and secret never appear in any output;
# (2) the script never writes an A record other than the house's current
# public IPv4.
# Anything outside these lines is not a defect.

import datetime
import errno
import ipaddress
import json
import os
import re
import signal
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Paths on the camera box, always with a slash. This process never opens
# /home/kyle/frigate/.env: compose injects that file into the container.
SECRETS_PATH = "/home/kyle/frigate/host-secrets.env"
LOCK_PATH = "/home/kyle/frigate/.porkbun-ddns.lock"

API_BASE = "https://api.porkbun.com/api/json/v3"
API_IPV4 = "https://api-ipv4.porkbun.com/api/json/v3"
HC_ORIGIN = "https://hc-ping.com"
PORKBUN_HOSTS = {
    API_BASE: "api.porkbun.com",
    API_IPV4: "api-ipv4.porkbun.com",
}

# Porkbun's usual minimum. Sent as a string; their examples are strings.
TTL = "600"
BUDGET_S = 60
REQUEST_CAP_S = 15
BODY_CAP = 64 * 1024
SECRETS_CAP = 64 * 1024
WATCHDOG_SLACK_S = 5
CHECKIN_NEED_S = 12
CHECKIN_CAP_S = 10
READ_CHUNK = 8192

API_KEY_RE = re.compile(r"^pk1_[A-Za-z0-9_]{16,}$")
SECRET_KEY_RE = re.compile(r"^sk1_[A-Za-z0-9_]{16,}$")
PING_KEY_RE = re.compile(r"^[A-Za-z0-9_-]{16,}$")
ENV_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
# One DNS label: 1-63 of [a-z0-9-], no leading or trailing hyphen.
LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
# At least one dot. The last label is letters only.
DOMAIN_RE = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{1,63}$"
)

STARTED = time.monotonic()
_SECRETS = []
_LOCK_FD = None
_OPENER = None


class Fail(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def remaining():
    return BUDGET_S - (time.monotonic() - STARTED)


def one_line(text):
    return " ".join(str(text).split())


def remember_secret(value):
    # Only a value that already passed its shape check is remembered.
    # Those values contain pk1_ or sk1_, or are a long ping token, so
    # redaction cannot eat a fixed word of the output.
    if value and value not in _SECRETS:
        _SECRETS.append(value)


def redact(text):
    if not isinstance(text, str):
        text = str(text)
    for secret in sorted(_SECRETS, key=len, reverse=True):
        forms = {
            secret,
            urllib.parse.quote(secret, safe=""),
            urllib.parse.quote_plus(secret),
            json.dumps(secret),
            json.dumps(secret)[1:-1],
        }
        for form in sorted(forms, key=len, reverse=True):
            if form:
                text = text.replace(form, "[redacted]")
    return text


class Boundary:
    # Last step before a byte leaves the process.
    def __init__(self, raw):
        self.raw = raw

    def write(self, text):
        if not text:
            return 0
        self.raw.write(redact(text))
        return len(text)

    def flush(self):
        self.raw.flush()

    def fileno(self):
        return self.raw.fileno()


def install_boundary():
    sys.stdout = Boundary(sys.__stdout__)
    sys.stderr = Boundary(sys.__stderr__)


def stamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def say(message):
    print(f"{stamp()} {one_line(message)}", flush=True)


def on_budget(_signum, _frame):
    try:
        line = redact(f"{stamp()} ERROR budget exceeded\n")
        sys.__stdout__.write(line)
        sys.__stdout__.flush()
    finally:
        os._exit(1)


def arm_watchdog():
    signal.signal(signal.SIGALRM, on_budget)
    signal.alarm(BUDGET_S + WATCHDOG_SLACK_S)


def parse_args(argv):
    domain = None
    name = None
    dry = False
    seen = set()
    args = list(argv[1:])
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--dry-run":
            key = arg
            value = True
        elif arg == "--domain" or arg == "--name":
            key = arg
            index += 1
            if index >= len(args):
                raise Fail(f"missing value for {arg}")
            value = args[index]
        elif arg.startswith("--domain=") or arg.startswith("--name="):
            key, value = arg.split("=", 1)
        else:
            raise Fail("unknown argument")
        if key in seen:
            raise Fail(f"repeated {key}")
        seen.add(key)
        if key == "--dry-run":
            dry = True
        elif key == "--domain":
            domain = value
        else:
            name = value
        index += 1
    if domain is None or name is None:
        raise Fail("--domain and --name are required")
    if DOMAIN_RE.fullmatch(domain) is None:
        raise Fail("--domain is not a lowercase hostname")
    if LABEL_RE.fullmatch(name) is None:
        raise Fail("--name is not a single DNS label")
    return domain, name, dry


def unquote_value(raw):
    if raw[:1] in ("'", '"'):
        if len(raw) < 2 or raw[-1] != raw[0]:
            raise Fail("unmatched quotes")
        return raw[1:-1]
    if raw[-1:] in ("'", '"'):
        raise Fail("unmatched quotes")
    return raw


def parse_secrets(text):
    if not isinstance(text, str):
        raise Fail("secrets file is not text")
    if text.startswith("\ufeff"):
        text = text[1:]
    found = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        body = line.strip()
        if not body or body.startswith("#"):
            continue
        if "=" not in body:
            raise Fail(f"secrets line {lineno} is not KEY=VALUE")
        key, raw = body.split("=", 1)
        key = key.strip()
        if ENV_KEY_RE.fullmatch(key) is None:
            raise Fail(f"secrets line {lineno} has a bad key name")
        try:
            value = unquote_value(raw.strip())
        except Fail:
            raise Fail(f"secrets line {lineno} has unmatched quotes")
        if key in found:
            raise Fail(f"secrets file repeats {key}")
        found[key] = value
    return found


def _take_key(found, name, pattern, shape):
    if name not in found:
        raise Fail(f"{name} is missing")
    value = found.pop(name)
    if value == "":
        raise Fail(f"{name} is empty")
    if pattern.fullmatch(value) is None:
        raise Fail(f"{name} does not have the {shape}")
    return value


def load_keys(text):
    found = parse_secrets(text)
    try:
        api = _take_key(found, "PORKBUN_API_KEY", API_KEY_RE, "pk1_ key shape")
        secret = _take_key(found, "PORKBUN_SECRET_API_KEY", SECRET_KEY_RE, "sk1_ key shape")
        if "HEALTHCHECKS_PING_KEY" not in found:
            ping = None
        else:
            ping = _take_key(
                found, "HEALTHCHECKS_PING_KEY", PING_KEY_RE, "ping key shape"
            )
    finally:
        found.clear()
    return api, secret, ping


def stat_problem(is_link, is_reg, mode, uid, owner, size):
    if is_link:
        return "secrets file is a symlink"
    if not is_reg:
        return "secrets file is not a regular file"
    if uid != owner:
        return "secrets file is not owned by the running user"
    if mode & 0o077:
        return "secrets file is readable by group or other"
    if size > SECRETS_CAP:
        return "secrets file is larger than 64KB"
    return ""


def read_secrets_file():
    import stat as statmod

    try:
        st = os.lstat(SECRETS_PATH)
    except FileNotFoundError:
        raise Fail("secrets file is missing")
    except OSError:
        raise Fail("secrets file is unreadable")
    problem = stat_problem(
        statmod.S_ISLNK(st.st_mode),
        statmod.S_ISREG(st.st_mode),
        statmod.S_IMODE(st.st_mode),
        st.st_uid,
        os.getuid(),
        st.st_size,
    )
    if problem:
        raise Fail(problem)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(SECRETS_PATH, flags)
    except OSError:
        raise Fail("secrets file is unreadable")
    try:
        blob = b""
        while len(blob) <= SECRETS_CAP:
            chunk = os.read(fd, SECRETS_CAP + 1 - len(blob))
            if not chunk:
                break
            blob += chunk
    finally:
        os.close(fd)
    if len(blob) > SECRETS_CAP:
        raise Fail("secrets file is larger than 64KB")
    try:
        return blob.decode("utf-8")
    except UnicodeDecodeError:
        raise Fail("secrets file is not utf-8")


def valid_public_ipv4(value):
    if not isinstance(value, str):
        return False
    try:
        addr = ipaddress.IPv4Address(value)
    except (ipaddress.AddressValueError, ValueError):
        return False
    if not addr.is_global:
        return False
    if addr.is_multicast:
        return False
    return True


def canonical_ipv4(value):
    try:
        return str(ipaddress.IPv4Address(value))
    except (ipaddress.AddressValueError, ValueError):
        return None


def decide_records(contents, ip):
    # Returns action, the value to print as the current record, and a reason.
    # action is no-op, edit, create, or error. error changes nothing.
    if not isinstance(contents, list):
        return "error", "none", "records are not a list"
    if len(contents) > 1:
        return "error", "none", "more than one A record"
    if len(contents) == 0:
        return "create", "none", ""
    only = contents[0]
    if not isinstance(only, str) or only == "":
        return "error", "none", "A record content is missing"
    current = canonical_ipv4(only)
    if current is not None and current == ip:
        return "no-op", current, ""
    shown = one_line(only)
    if len(shown) > 80 or any(ch.isspace() for ch in only):
        return "error", "none", "A record content is malformed"
    return "edit", shown, ""


def hold_lock():
    global _LOCK_FD
    import fcntl

    fd = os.open(LOCK_PATH, os.O_RDWR | os.O_CREAT, 0o644)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as exc:
        os.close(fd)
        if exc.errno in (errno.EAGAIN, errno.EACCES, errno.EWOULDBLOCK):
            raise SystemExit(0)
        raise Fail("could not lock the ddns run")
    _LOCK_FD = fd


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Fail("refusing a redirect")


def make_opener():
    # An empty proxy map ignores http_proxy. A redirect would carry the
    # request, and for the check-in the key is in the URL, off this host.
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        NoRedirect(),
    )


def opener():
    global _OPENER
    if _OPENER is None:
        _OPENER = make_opener()
    return _OPENER


def assert_https(url, host):
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or parts.hostname != host:
        raise Fail("refusing an unpinned origin")
    if parts.username or parts.password:
        raise Fail("refusing credentials in a url")
    return url


def porkbun_url(base, suffix):
    host = PORKBUN_HOSTS.get(base)
    if host is None:
        raise Fail("refusing an unpinned origin")
    if not suffix.startswith("/") or ".." in suffix or "\\" in suffix:
        raise Fail("refusing a bad porkbun path")
    return assert_https(base + suffix, host)


def checkin_url(ping):
    if PING_KEY_RE.fullmatch(ping) is None:
        raise Fail("HEALTHCHECKS_PING_KEY does not have the ping key shape")
    url = HC_ORIGIN + "/" + ping + "/ddns?create=1"
    return assert_https(url, "hc-ping.com")


def request_timeout(cap):
    left = remaining()
    if left <= 0:
        raise Fail("no time left")
    return min(float(cap), left)


def read_limited(resp):
    header = getattr(resp, "headers", None)
    if header is not None:
        declared = header.get("Content-Length")
        if declared and declared.isdigit() and int(declared) > BODY_CAP:
            raise Fail("response is larger than 64KB")
    parts = []
    total = 0
    while True:
        if remaining() <= 0:
            raise Fail("no time left")
        try:
            block = resp.read(READ_CHUNK)
        except (TimeoutError, socket.timeout):
            raise Fail("request timed out")
        if not block:
            break
        total += len(block)
        if total > BODY_CAP:
            raise Fail("response is larger than 64KB")
        parts.append(block)
    return b"".join(parts)


def perform(req, timeout):
    http_code = None
    try:
        resp = opener().open(req, timeout=timeout)
    except Fail:
        raise
    except urllib.error.HTTPError as exc:
        resp = exc
        http_code = exc.code
    except (TimeoutError, socket.timeout):
        raise Fail("request timed out")
    except urllib.error.URLError:
        raise Fail("request failed")
    try:
        return read_limited(resp), http_code
    finally:
        close = getattr(resp, "close", None)
        if close is not None:
            close()


def interpret(raw):
    if len(raw) > BODY_CAP:
        raise Fail("response is larger than 64KB")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise Fail("response is not json")
    if not isinstance(data, dict) or data.get("status") != "SUCCESS":
        code = ""
        if isinstance(data, dict) and data.get("code") is not None:
            code = one_line(data.get("code"))[:40]
        if code:
            raise Fail(f"porkbun returned an error ({code})")
        raise Fail("porkbun returned an error")
    return data


def post_porkbun(url, body, cap):
    # Credentials ride in the JSON body only. The URL is a pinned path.
    payload = json.dumps(body).encode("utf-8")
    if len(payload) > BODY_CAP:
        raise Fail("request is larger than 64KB")
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    raw, _http_code = perform(req, request_timeout(cap))
    return interpret(raw)


def auth_body(api, secret):
    return {"apikey": api, "secretapikey": secret}


def ping_ip(api, secret):
    data = post_porkbun(
        porkbun_url(API_IPV4, "/ping"),
        auth_body(api, secret),
        REQUEST_CAP_S,
    )
    if data.get("credentialsValid") is not True:
        raise Fail("porkbun credentials were not accepted")
    your_ip = data.get("yourIp")
    if not valid_public_ipv4(your_ip):
        raise Fail("yourIp is not a public IPv4 address")
    return str(ipaddress.IPv4Address(your_ip))


def record_contents(data):
    records = data.get("records")
    if not isinstance(records, list):
        raise Fail("retrieve response has no records")
    contents = []
    for rec in records:
        if not isinstance(rec, dict):
            raise Fail("A record is malformed")
        rec_type = rec.get("type")
        if rec_type not in (None, "A"):
            raise Fail("retrieve returned a non-A record")
        content = rec.get("content")
        if not isinstance(content, str):
            raise Fail("A record content is missing")
        contents.append(content)
    return contents


def retrieve(domain, name, api, secret):
    data = post_porkbun(
        porkbun_url(API_BASE, f"/dns/retrieveByNameType/{domain}/A/{name}"),
        auth_body(api, secret),
        REQUEST_CAP_S,
    )
    return record_contents(data)


def write_record(action, domain, name, ip, api, secret):
    if not valid_public_ipv4(ip):
        raise Fail("refusing to write an address that is not a public IPv4")
    body = auth_body(api, secret)
    body["content"] = ip
    body["ttl"] = TTL
    if action == "edit":
        url = porkbun_url(API_BASE, f"/dns/editByNameType/{domain}/A/{name}")
    elif action == "create":
        url = porkbun_url(API_BASE, f"/dns/create/{domain}")
        body["name"] = name
        body["type"] = "A"
    else:
        raise Fail("refusing a write that is not edit or create")
    post_porkbun(url, body, REQUEST_CAP_S)


def read_back(domain, name, ip, api, secret):
    action, _shown, reason = decide_records(retrieve(domain, name, api, secret), ip)
    if action != "no-op" or reason:
        raise Fail("read-back did not show the new address")


def get_checkin(ping):
    url = checkin_url(ping)
    req = urllib.request.Request(url, method="GET", headers={"Accept": "text/plain"})
    _raw, http_code = perform(req, request_timeout(CHECKIN_CAP_S))
    if http_code is not None and not 200 <= http_code < 300:
        raise Fail(f"http {http_code}")


def maybe_checkin(ping):
    if not ping:
        return
    if remaining() < CHECKIN_NEED_S:
        say("check-in failed: no budget left")
        return
    try:
        get_checkin(ping)
    except Fail as exc:
        say("check-in failed: " + exc.reason)
    except Exception as exc:
        say("check-in failed: " + exc.__class__.__name__)


def run(argv):
    domain, name, dry = parse_args(argv)
    if not dry:
        hold_lock()
    api, secret, ping = load_keys(read_secrets_file())
    remember_secret(api)
    remember_secret(secret)
    if ping:
        remember_secret(ping)
    ip = ping_ip(api, secret)
    action, shown, reason = decide_records(retrieve(domain, name, api, secret), ip)
    fqdn = f"{name}.{domain}"
    if action == "error":
        raise Fail(reason or "could not decide the A record")
    if dry:
        say(f"DRY-RUN {action} {fqdn} A {shown} -> {ip}")
        return 0
    if action == "no-op":
        maybe_checkin(ping)
        return 0
    say(f"updating {fqdn} A {shown} -> {ip}")
    write_record(action, domain, name, ip, api, secret)
    read_back(domain, name, ip, api, secret)
    say(f"verified {fqdn} A {ip}")
    maybe_checkin(ping)
    return 0


def main(argv):
    install_boundary()
    try:
        try:
            arm_watchdog()
        except AttributeError:
            raise Fail("no interval timer")
        return run(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        return code if isinstance(code, int) else 1
    except Fail as exc:
        say("ERROR " + exc.reason)
        return 1
    except BaseException as exc:
        say(f"ERROR {exc.__class__.__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
