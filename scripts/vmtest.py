#!/usr/bin/env python3
"""Drive a QEMU VM for automated Tei OS tests: start, type, click, screenshot (QMP)."""
import json
import os
import socket
import subprocess
import sys
import time

QMP = os.environ.get("QMP_SOCK", "/tmp/teios-qmp.sock")

KEYMAP = {
    " ": "spc", "\n": "ret", "\t": "tab", "-": "minus", "=": "equal", ".": "dot", ",": "comma", "/": "slash",
    ";": "semicolon", "'": "apostrophe", "[": "bracket_left", "]": "bracket_right", "\\": "backslash", "`": "grave_accent",
}
SHIFTED = {"_": "minus", "+": "equal", ":": "semicolon", "\"": "apostrophe", "?": "slash", ">": "dot", "<": "comma",
           "!": "1", "@": "2", "#": "3", "$": "4", "%": "5", "^": "6", "&": "7", "*": "8", "(": "9", ")": "0"}


class Qmp:
    def __init__(self, path=QMP):
        self.s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.s.connect(path)
        self.f = self.s.makefile("rw")
        self._read()
        self.cmd("qmp_capabilities")

    def _read(self):
        while True:
            line = self.f.readline()
            if not line:
                raise RuntimeError("QMP closed")
            msg = json.loads(line)
            if "event" in msg:
                continue
            return msg

    def cmd(self, name, **args):
        self.f.write(json.dumps({"execute": name, "arguments": args} if args else {"execute": name}) + "\n")
        self.f.flush()
        r = self._read()
        if "error" in r:
            raise RuntimeError(f"{name}: {r['error']}")
        return r.get("return")

    def shot(self, path):
        tmp = path + ".ppm"
        self.cmd("screendump", filename=tmp)
        subprocess.run(["convert", tmp, path], check=True)
        os.remove(tmp)
        return path

    def key(self, *keys, hold=5):
        self.cmd("send-key", keys=[{"type": "qcode", "data": k} for k in keys], **{"hold-time": hold})

    def type(self, text, delay=0.05):
        for ch in text:
            if ch.isalpha():
                if ch.isupper():
                    self.key("shift", ch.lower())
                else:
                    self.key(ch)
            elif ch.isdigit():
                self.key(ch)
            elif ch in KEYMAP:
                self.key(KEYMAP[ch])
            elif ch in SHIFTED:
                self.key("shift", SHIFTED[ch])
            time.sleep(delay)

    def move(self, x, y, w=None, h=None):
        w = w or int(os.environ.get("VM_W", "1280"))
        h = h or int(os.environ.get("VM_H", "800"))
        ax, ay = int(x * 32767 / (w - 1)), int(y * 32767 / (h - 1))
        self.cmd("input-send-event", events=[{"type": "abs", "data": {"axis": "x", "value": ax}},
                                             {"type": "abs", "data": {"axis": "y", "value": ay}}])

    def click(self, x, y, w=None, h=None, button="left", double=False):
        self.move(x, y, w, h)
        time.sleep(0.15)
        for _ in range(2 if double else 1):
            self.cmd("input-send-event", events=[{"type": "btn", "data": {"down": True, "button": button}}])
            time.sleep(0.08)
            self.cmd("input-send-event", events=[{"type": "btn", "data": {"down": False, "button": button}}])
            time.sleep(0.12)


def start(iso=None, disk=None, fw="bios", mem=3584, boot="d", extra=()):
    if os.path.exists(QMP):
        os.remove(QMP)
    args = ["qemu-system-x86_64", "-accel", "tcg,thread=multi", "-cpu", "max", "-smp", "2", "-m", str(mem),
            "-device", "qemu-xhci", "-device", "usb-tablet", "-vga", "none", "-device", "VGA,xres=1280,yres=800,edid=on",
            "-display", "none", "-qmp", f"unix:{QMP},server=on,wait=off",
            "-netdev", "user,id=n0", "-device", "virtio-net-pci,netdev=n0",
            "-serial", "file:/tmp/teios-serial.log"]
    if fw == "bios":
        args += ["-machine", "q35"]
    else:
        code = "/usr/share/OVMF/OVMF_CODE_4M.ms.fd" if fw == "uefi-sb" else "/usr/share/OVMF/OVMF_CODE_4M.fd"
        vars_src = "/usr/share/OVMF/OVMF_VARS_4M.ms.fd" if fw == "uefi-sb" else "/usr/share/OVMF/OVMF_VARS_4M.fd"
        vars_dst = f"/home/claude/build/vm/ovmf-vars-{fw}.fd"
        if not os.path.exists(vars_dst):
            subprocess.run(["cp", vars_src, vars_dst], check=True)
        args += ["-machine", "q35,smm=on" if fw == "uefi-sb" else "q35",
                 "-drive", f"if=pflash,format=raw,readonly=on,file={code}",
                 "-drive", f"if=pflash,format=raw,file={vars_dst}"]
        if fw == "uefi-sb":
            args += ["-global", "driver=cfi.pflash01,property=secure,value=on"]
    if disk:
        args += ["-drive", f"file={disk},if=virtio,format=qcow2"]
    if iso:
        args += ["-drive", f"file={iso},media=cdrom,if=none,id=cd0", "-device", "ide-cd,drive=cd0,bus=ide.1"]
    args += ["-boot", boot]
    args += list(extra)
    log = open("/tmp/teios-qemu.log", "w")
    p = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    for _ in range(50):
        if os.path.exists(QMP):
            break
        time.sleep(0.2)
    return p.pid


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "start":
        # vmtest.py start <fw> <iso|-> <disk|-> [boot]
        fw, iso, disk = sys.argv[2], sys.argv[3], sys.argv[4]
        boot = sys.argv[5] if len(sys.argv) > 5 else ("d" if iso != "-" else "c")
        print(start(None if iso == "-" else iso, None if disk == "-" else disk, fw, boot=boot))
    else:
        q = Qmp()
        if cmd == "shot":
            print(q.shot(sys.argv[2]))
        elif cmd == "key":
            q.key(*sys.argv[2:])
        elif cmd == "type":
            q.type(sys.argv[2])
        elif cmd == "click":
            q.click(int(sys.argv[2]), int(sys.argv[3]), double=len(sys.argv) > 4 and sys.argv[4] == "double")
        elif cmd == "rclick":
            q.click(int(sys.argv[2]), int(sys.argv[3]), button="right")
        elif cmd == "move":
            q.move(int(sys.argv[2]), int(sys.argv[3]))
        elif cmd == "quit":
            q.cmd("quit")
        elif cmd == "status":
            print(q.cmd("query-status"))
