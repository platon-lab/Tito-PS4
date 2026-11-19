#!/usr/bin/env python3
# Готовит pkg/ для темы PS4: param.sfo (категория theme), иконка, фоновые картинки и gp4.
import os
import shutil
import struct

TITLE = "TITO Theme"
TITLE_ID = "TITOTHM00"
CONTENT_ID = "IV0000-TITOTHM00_00-TITOTHEME0000000"
VERSION = "01.00"
# Тип тома для темы. Если PkgTool скажет, что тип неизвестен, поменяй здесь.
VOLUME_TYPE = "pkg_ps4_theme"

PKG = "pkg"
SCE = os.path.join(PKG, "sce_sys")

ENTRIES = {
    "CATEGORY":   ("str", "th", 4),
    "CONTENT_ID": ("str", CONTENT_ID, 0x30),
    "TITLE":      ("str", TITLE, 0x80),
    "TITLE_ID":   ("str", TITLE_ID, 0x10),
    "VERSION":    ("str", VERSION, 0x08),
    "APP_VER":    ("str", VERSION, 0x08),
    "ATTRIBUTE":  ("int", 0, 4),
    "SYSTEM_VER": ("int", 0, 4),
}

IMAGES = ["icon512.png", "pic0.png", "pic1.png"]


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


def gp4_xml():
    files = [
        "sce_sys/param.sfo",
        "sce_sys/icon0.png",
        "sce_sys/pic0.png",
        "sce_sys/pic1.png",
    ]
    file_lines = "\n".join(f'<file targ_path="{p}" orig_path="{p}" />' for p in files)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<psproject fmt="gp4" version="1000">
<volume>
<volume_type>{VOLUME_TYPE}</volume_type>
<volume_id>PS4VOLUME</volume_id>
<volume_ver>0001</volume_ver>
<volume_ts>2026-11-15 00:00:00</volume_ts>
<system_ver>0000</system_ver>
<package content_id="{CONTENT_ID}" passcode="00000000000000000000000000000000"/>
</volume>
<files img_no="0">
{file_lines}
</files>
<rootdir>
<dir targ_name="sce_sys"/>
</rootdir>
</psproject>
"""


def main():
    os.makedirs(SCE, exist_ok=True)
    with open(os.path.join(SCE, "param.sfo"), "wb") as f:
        f.write(sfo_bytes(ENTRIES))
    shutil.copy("icon512.png", os.path.join(SCE, "icon0.png"))
    shutil.copy("pic0.png", os.path.join(SCE, "pic0.png"))
    shutil.copy("pic1.png", os.path.join(SCE, "pic1.png"))
    with open(os.path.join(PKG, "pkg.gp4"), "w", encoding="utf-8") as f:
        f.write(gp4_xml())
    print("theme pkg/ prepared")


if __name__ == "__main__":
    main()
