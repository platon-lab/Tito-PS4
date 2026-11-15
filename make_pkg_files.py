#!/usr/bin/env python3
# Создаёт pkg/ с param.sfo, icon0.png, eboot.bin и gp4-проектом.
import os
import shutil
import struct

TITLE = "TITO: Golden Bone"
TITLE_ID = "TITO00000"
CONTENT_ID = "IV0000-TITO00000_00-TITOPS4000000000"
VERSION = "01.00"

PKG = "pkg"
SCE = os.path.join(PKG, "sce_sys")

ENTRIES = {
    "CATEGORY":   ("str", "gd", 4),
    "CONTENT_ID": ("str", CONTENT_ID, 0x30),
    "TITLE":      ("str", TITLE, 0x80),
    "TITLE_ID":   ("str", TITLE_ID, 0x10),
    "VERSION":    ("str", VERSION, 0x08),
    "APP_VER":    ("str", VERSION, 0x08),
    "ATTRIBUTE":  ("int", 0, 4),
}


def sfo_bytes(entries):
    keys = sorted(entries)
    key_table = bytearray()
    key_offsets = {}
    for k in keys:
        key_offsets[k] = len(key_table)
        key_table += k.encode() + b"\x00"
    while len(key_table) % 4:
        key_table += b"\x00"

    data_table = bytearray()
    index = bytearray()
    for k in keys:
        kind, value, maxlen = entries[k]
        if kind == "int":
            data = struct.pack("<I", value)
            fmt = 0x0404
            length = 4
            maxlen = 4
        else:
            data = value.encode() + b"\x00"
            fmt = 0x0204
            length = len(data)
            maxlen = max(maxlen, length)
        data_offset = len(data_table)
        data_table += data.ljust(maxlen, b"\x00")
        while len(data_table) % 4:
            data_table += b"\x00"
        index += struct.pack("<HHIII", key_offsets[k], fmt, length, maxlen, data_offset)

    key_table_off = 20 + len(index)
    data_table_off = key_table_off + len(key_table)
    header = b"\x00PSF" + struct.pack("<IIII", 0x101, key_table_off, data_table_off, len(keys))
    return header + bytes(index) + bytes(key_table) + bytes(data_table)


def find_in_toolchain(name):
    tc = os.environ.get("OO_PS4_TOOLCHAIN", "")
    if not tc:
        raise SystemExit("OO_PS4_TOOLCHAIN не задан")
    for root, _dirs, files in os.walk(tc):
        if name in files:
            return os.path.join(root, name)
    raise SystemExit(f"Не нашёл {name} внутри {tc}")


GP4 = """<?xml version="1.0" encoding="UTF-8"?>
<psproject fmt="gp4" version="1000">
<volume>
<volume_type>pkg_ps4_app</volume_type>
<volume_id>PS4VOLUME</volume_id>
<volume_ver>0001</volume_ver>
<system_ver>0000</system_ver>
<package content_id="{cid}" passcode="00000000000000000000000000000000"/>
</volume>
<files img_no="0">
<file targ_path="sce_sys/param.sfo" orig_path="sce_sys/param.sfo" />
<file targ_path="sce_sys/icon0.png" orig_path="sce_sys/icon0.png" />
<file targ_path="eboot.bin" orig_path="eboot.bin" />
<file targ_path="sce_module/libc.prx" orig_path="sce_module/libc.prx" />
<file targ_path="sce_module/libSceFios2.prx" orig_path="sce_module/libSceFios2.prx" />
</files>
<rootdir>
<dir targ_name="sce_sys"/>
<dir targ_name="sce_module"/>
</rootdir>
</psproject>
"""


def main():
    os.makedirs(SCE, exist_ok=True)
    with open(os.path.join(SCE, "param.sfo"), "wb") as f:
        f.write(sfo_bytes(ENTRIES))
    shutil.copy("icon512.png", os.path.join(SCE, "icon0.png"))
    shutil.copy("eboot.bin", os.path.join(PKG, "eboot.bin"))
    os.makedirs(os.path.join(PKG, "sce_module"), exist_ok=True)
    for prx in ("libc.prx", "libSceFios2.prx"):
        shutil.copy(find_in_toolchain(prx), os.path.join(PKG, "sce_module", prx))
    with open(os.path.join(PKG, "pkg.gp4"), "w", encoding="utf-8") as f:
        f.write(GP4.format(cid=CONTENT_ID))
    print("pkg/ prepared")


if __name__ == "__main__":
    main()
