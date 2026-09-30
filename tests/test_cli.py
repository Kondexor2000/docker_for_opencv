import subprocess
import sys

import cv2


def test_cli_end_to_end(tmp_path):
    output = tmp_path / "edges.png"
    run = subprocess.run(
        [sys.executable, "-m", "app", "examples/shapes.pgm", "--output", str(output)],
        capture_output=True, text=True, check=False,
    )
    assert run.returncode == 0, run.stderr
    assert '"width": 160' in run.stdout
    edges = cv2.imread(str(output), cv2.IMREAD_GRAYSCALE)
    assert edges is not None and edges.shape == (120, 160)
    assert cv2.countNonZero(edges) > 0


def test_cli_reports_missing_input():
    run = subprocess.run(
        [sys.executable, "-m", "app", "missing-image.png"],
        capture_output=True, text=True, check=False,
    )
    assert run.returncode != 0
    assert "Could not read image" in run.stderr
