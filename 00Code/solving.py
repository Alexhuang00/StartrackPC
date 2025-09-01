import subprocess
from pathlib import Path
import os
import numpy as np


def solve_field(wsl_input, new_output, corr_output, objs_output):

    img_new_name = Path(wsl_input).name.replace(".jpg", ".new")
    img_corr_name = Path(wsl_input).name.replace(".jpg", ".corr")
    img_objs_name = Path(wsl_input).name.replace(".jpg", "-objs.png")
    wsl_img_path = wsl_input

    print(f"🔭 Solving {Path(wsl_input).name} ...")
    subprocess.run(["cp", wsl_img_path, "/home/alex/astrometry.net-0.97/demo/"], check=True)

    cmd = (
        "source activate && "
        "conda activate StarTracker && "
        f"solve-field --config /home/alex/astrometry.net-0.97/etc/astrometry.cfg /home/alex/astrometry.net-0.97/demo/{Path(wsl_input).name} --overwrite"
    )

    subprocess.run(["bash", "-c", cmd], check=True)

    subprocess.run(["cp", f"/home/alex/astrometry.net-0.97/demo/{img_new_name}", new_output])
    subprocess.run(["cp", f"/home/alex/astrometry.net-0.97/demo/{img_corr_name}", corr_output])
    subprocess.run(["cp", f"/home/alex/astrometry.net-0.97/demo/{img_objs_name}", objs_output])