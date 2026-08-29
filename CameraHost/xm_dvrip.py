import socket, struct, json, hashlib


def sofia_hash(pw):
    md5 = hashlib.md5(pw.encode()).digest()
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:"
    return ''.join(chars[(md5[i * 2] + md5[i * 2 + 1]) % 62] for i in range(8))


class DVRIP:
    # XiongMai/Sofia binary protocol on port 34567. The Sunba's ONVIF service
    # exposes streams and PTZ but refuses config writes, so anything that
    # changes the camera has to come through here.
    def __init__(self, host, user="admin", password="", port=34567, timeout=8):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.session = 0
        self.seq = 0
        mid, r = self.send(1000, {"EncryptType": "MD5", "LoginType": "DVRIP-Web",
                                  "PassWord": sofia_hash(password), "UserName": user})
        if not (isinstance(r, dict) and r.get("Ret") == 100):
            raise RuntimeError(f"login failed: {r}")
        self.session = int(r["SessionID"], 16)

    def send(self, msgid, payload):
        data = json.dumps(payload).encode() + b"\x0a\x00"
        head = struct.pack("<BB2xII2xHI", 255, 0, self.session, self.seq, msgid, len(data))
        self.s.sendall(head + data)
        self.seq += 1
        h = self.s.recv(20)
        if len(h) < 20:
            raise RuntimeError("short header")
        _, _, sess, _, rmsgid, ln = struct.unpack("<BB2xII2xHI", h)
        body = b""
        while len(body) < ln:
            chunk = self.s.recv(ln - len(body))
            if not chunk:
                break
            body += chunk
        self.session = sess
        txt = body.rstrip(b"\x00\x0a").decode("utf-8", "replace")
        try:
            return rmsgid, json.loads(txt)
        except Exception:
            return rmsgid, txt

    def sid(self):
        return "0x%08X" % self.session

    def get(self, name):
        mid, r = self.send(1042, {"Name": name, "SessionID": self.sid()})
        return r.get(name) if isinstance(r, dict) else r

    def set(self, name, value):
        # Note: this firmware answers Ret 603 for changes it nonetheless
        # applies, so callers must read the value back rather than trust Ret.
        mid, r = self.send(1040, {"Name": name, "SessionID": self.sid(), name: value})
        return r

    def get_time(self):
        mid, r = self.send(1452, {"Name": "OPTimeQuery", "SessionID": self.sid()})
        return r.get("OPTimeQuery") if isinstance(r, dict) else r

    def set_time(self, when):
        mid, r = self.send(1450, {"Name": "OPTimeSetting", "SessionID": self.sid(),
                                  "OPTimeSetting": when.strftime("%Y-%m-%d %H:%M:%S")})
        return r

    def close(self):
        try:
            self.s.close()
        except Exception:
            pass
