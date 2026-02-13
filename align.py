#!/usr/bin/env python3

import sys
import json
import subprocess

cfg = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "config.json"))

anchor_input = cfg["anchor"]["input"]
anchor_cp = cfg["anchor"]["control_points"]
remap_input = cfg["remap"]["input"]
remap_output = cfg["remap"]["output"]
remap_cp = cfg["remap"]["control_points"]
output_format = {"tif": "TIFF", "png": "PNG", "jpg": "JPEG"}[remap_output.split(".")[-1]]

subprocess.run(["pto_gen", "-o", "project.pto", "-p", "0", "-f", "10", "-s", "1", anchor_input, remap_input], check=True)

with open("project.pto") as f:
    imgline = next(l for l in f if l.startswith("i"))
    i, w, h, *_ = imgline.split()
    assert i == "i" and w.startswith("w") and h.startswith("h")
    width = int(w.removeprefix("w"))
    height = int(h.removeprefix("h"))

subprocess.run(["pto_var", "-o", "project.pto", "--anchor=0", "--opt=y1,p1,r1,Tpy1,Tpp1,v1,d1,e1,g1,t1", "project.pto"], check=True)

with open("project.pto", "a") as f:
    for (x0, y0), (x1, y1) in zip(anchor_cp, remap_cp):
        print(f"c n0 N1 x{x0} y{y0} X{x1} Y{y1} t0", file=f)

subprocess.run(["autooptimiser", "-o", "project.pto", "-n", "project.pto"], check=True)

subprocess.run(["pano_modify", "-o", "project.pto", "-p", "0", "--fov=10", f"--canvas={width}x{height}", "--output-type=REMAPORIG", "project.pto"], check=True)

subprocess.run(["nona", "-v", "-o", remap_output, "-i", "1", "-m", output_format, "project.pto"], check=True)

