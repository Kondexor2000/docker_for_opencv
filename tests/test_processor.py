import numpy as np
import pytest

from app.processor import detect_edges, process_file


def test_detect_edges_finds_rectangle_boundaries():
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    image[25:75, 25:75] = 255
    edges = detect_edges(image)
    assert edges.shape == (100, 100)
    assert edges.dtype == np.uint8
    assert np.count_nonzero(edges) > 0


def test_detect_edges_rejects_invalid_thresholds():
    with pytest.raises(ValueError, match="Thresholds"):
        detect_edges(np.zeros((4, 4), dtype=np.uint8), 200, 100)


def test_process_file_writes_edge_map(tmp_path):
    output = tmp_path / "result.png"
    result = process_file("examples/shapes.pgm", output)
    assert output.is_file()
    assert result["width"] == 160
    assert result["height"] == 120
