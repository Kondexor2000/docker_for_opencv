import numpy as np
import pytest

from app.processor import detect_edges, process_file
from app.crossing_demo import (
    DEMO_BRAKING_DECELERATION_MPS2,
    DEMO_REACTION_TIME_S,
    DEMO_SAFETY_MARGIN_M,
    DEMO_TRAIN_SPEED_KMH,
    FRAME_INTERVAL_S,
    METERS_PER_PIXEL,
    _render_frame,
    estimate_speed_kmh,
    generate_demo,
    train_stopping_distance_m,
)


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


def test_synthetic_frames_estimate_car_speed():
    frames = [_render_frame(40 + 40 * index) for index in range(5)]
    speed = estimate_speed_kmh(frames, FRAME_INTERVAL_S, METERS_PER_PIXEL)
    assert speed == pytest.approx(72.0)


def test_stopping_distance_includes_reaction_and_margin():
    distance = train_stopping_distance_m(
        DEMO_TRAIN_SPEED_KMH,
        DEMO_BRAKING_DECELERATION_MPS2,
        DEMO_REACTION_TIME_S,
        DEMO_SAFETY_MARGIN_M,
    )
    assert distance == pytest.approx(638.27, abs=0.01)


def test_generate_demo_writes_frames_and_advisory_summary(tmp_path):
    summary = generate_demo(tmp_path)
    assert summary["mode"] == "synthetic_demo_only_no_train_control"
    assert summary["vehicle_speed_kmh"] == 72.0
    assert summary["overspeed_advisory"] is True
    assert summary["within_limit_example"]["vehicle_speed_kmh"] == 36.0
    assert summary["within_limit_example"]["overspeed_advisory"] is False
    assert len(list(tmp_path.glob("frame_*.png"))) == 5
    assert len(list((tmp_path / "within_limit").glob("frame_*.png"))) == 5
    assert (tmp_path / "summary.json").is_file()
    assert (tmp_path / "within_limit" / "summary.json").is_file()
