"""Synthetic level-crossing vision demo; it must not be used for train control."""

import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np

FRAME_COUNT = 5
FRAME_INTERVAL_S = 0.5
METERS_PER_PIXEL = 0.25
CAR_SPEED_LIMIT_KMH = 50.0
DEMO_TRAIN_SPEED_KMH = 80.0
DEMO_BRAKING_DECELERATION_MPS2 = 0.5
DEMO_REACTION_TIME_S = 2.0
DEMO_SAFETY_MARGIN_M = 100.0
CAR_COLOR_LOWER = np.array((200, 0, 0), dtype=np.uint8)
CAR_COLOR_UPPER = np.array((255, 80, 80), dtype=np.uint8)


def _render_frame(car_x: int) -> np.ndarray:
    frame = np.full((280, 400, 3), (75, 125, 65), dtype=np.uint8)
    cv2.rectangle(frame, (0, 135), (399, 245), (65, 65, 65), -1)
    cv2.rectangle(frame, (295, 0), (335, 279), (75, 75, 75), -1)
    for y in range(0, 280, 24):
        cv2.line(frame, (294, y), (336, y), (125, 125, 125), 3)
    cv2.line(frame, (304, 0), (304, 279), (210, 210, 210), 3)
    cv2.line(frame, (326, 0), (326, 279), (210, 210, 210), 3)
    car_body = np.array(
        [
            (car_x, 184),
            (car_x + 5, 177),
            (car_x + 15, 176),
            (car_x + 21, 169),
            (car_x + 36, 169),
            (car_x + 43, 178),
            (car_x + 48, 182),
            (car_x + 47, 196),
            (car_x + 3, 196),
        ],
        dtype=np.int32,
    )
    cv2.fillPoly(frame, [car_body], (255, 0, 0))
    cv2.fillPoly(
        frame,
        [np.array([(car_x + 18, 176), (car_x + 22, 171),
                   (car_x + 34, 171), (car_x + 39, 178)], dtype=np.int32)],
        (220, 220, 220),
    )
    for wheel_x in (car_x + 12, car_x + 38):
        cv2.circle(frame, (wheel_x, 196), 5, (20, 20, 20), -1)
        cv2.circle(frame, (wheel_x, 196), 2, (180, 180, 180), -1)
    cv2.putText(frame, "SYNTHETIC CROSSING", (8, 24), cv2.FONT_HERSHEY_SIMPLEX,
                0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return frame


def _detect_car(frame: np.ndarray) -> tuple[float, float, tuple[int, int, int, int]]:
    mask = cv2.inRange(frame, CAR_COLOR_LOWER, CAR_COLOR_UPPER)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Could not detect the synthetic car in a frame")
    x, y, width, height = cv2.boundingRect(max(contours, key=cv2.contourArea))
    if width * height < 500:
        raise ValueError("Could not detect the synthetic car in a frame")
    return x + width / 2, y + height / 2, (x, y, width, height)


def estimate_speed_kmh(
    frames: list[np.ndarray], frame_interval_s: float, meters_per_pixel: float
) -> float:
    """Estimate speed between the first and last synthetic car detections."""
    if len(frames) < 2:
        raise ValueError("At least two frames are required to estimate speed")
    if frame_interval_s <= 0 or meters_per_pixel <= 0:
        raise ValueError("Frame interval and meters per pixel must be positive")

    centers = [_detect_car(frame)[:2] for frame in frames]
    distance_px = math.dist(centers[0], centers[-1])
    elapsed_s = (len(frames) - 1) * frame_interval_s
    return distance_px * meters_per_pixel / elapsed_s * 3.6


def train_stopping_distance_m(
    speed_kmh: float,
    braking_deceleration_mps2: float,
    reaction_time_s: float,
    safety_margin_m: float,
) -> float:
    """Return a physics-based illustration, not an operational stopping distance."""
    if speed_kmh <= 0:
        raise ValueError("Train speed must be positive")
    if braking_deceleration_mps2 <= 0:
        raise ValueError("Braking deceleration must be positive")
    if reaction_time_s < 0 or safety_margin_m < 0:
        raise ValueError("Reaction time and safety margin must not be negative")

    speed_mps = speed_kmh / 3.6
    return (
        speed_mps * reaction_time_s
        + speed_mps**2 / (2 * braking_deceleration_mps2)
        + safety_margin_m
    )


def _write_scenario(output: Path, step_px: int) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    frames = [_render_frame(40 + step_px * index) for index in range(FRAME_COUNT)]
    speed_kmh = estimate_speed_kmh(frames, FRAME_INTERVAL_S, METERS_PER_PIXEL)
    overspeed = speed_kmh > CAR_SPEED_LIMIT_KMH

    for index, frame in enumerate(frames):
        x, y, width, height = _detect_car(frame)[2]
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"Demo speed: {speed_kmh:.1f} km/h",
            (8, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        if overspeed:
            cv2.putText(
                frame,
                "OVERSPEED ADVISORY - DEMO ONLY",
                (8, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (0, 0, 255),
                1,
                cv2.LINE_AA,
            )
        else:
            cv2.putText(
                frame,
                "WITHIN LIMIT - DEMO ONLY",
                (8, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.48,
                (0, 255, 0),
                1,
                cv2.LINE_AA,
            )
        image_path = output / f"frame_{index:02d}.png"
        if not cv2.imwrite(str(image_path), frame):
            raise OSError(f"Could not write demo image: {image_path}")

    stopping_distance_m = train_stopping_distance_m(
        DEMO_TRAIN_SPEED_KMH,
        DEMO_BRAKING_DECELERATION_MPS2,
        DEMO_REACTION_TIME_S,
        DEMO_SAFETY_MARGIN_M,
    )
    summary = {
        "mode": "synthetic_demo_only_no_train_control",
        "vehicle_speed_kmh": round(speed_kmh, 1),
        "vehicle_speed_limit_kmh": CAR_SPEED_LIMIT_KMH,
        "overspeed_advisory": overspeed,
        "train_stopping_distance_m_illustrative": round(stopping_distance_m, 1),
        "assumptions": {
            "train_speed_kmh": DEMO_TRAIN_SPEED_KMH,
            "braking_deceleration_mps2": DEMO_BRAKING_DECELERATION_MPS2,
            "reaction_time_s": DEMO_REACTION_TIME_S,
            "safety_margin_m": DEMO_SAFETY_MARGIN_M,
        },
        "frames": FRAME_COUNT,
        "output_dir": str(output),
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def generate_demo(output_dir: str | Path) -> dict:
    """Write over-limit and within-limit synthetic examples; neither controls a train."""
    output = Path(output_dir)
    overspeed_summary = _write_scenario(output, step_px=40)
    within_limit_summary = _write_scenario(output / "within_limit", step_px=20)
    overspeed_summary["within_limit_example"] = {
        "vehicle_speed_kmh": within_limit_summary["vehicle_speed_kmh"],
        "overspeed_advisory": within_limit_summary["overspeed_advisory"],
        "output_dir": within_limit_summary["output_dir"],
    }
    (output / "summary.json").write_text(
        json.dumps(overspeed_summary, indent=2) + "\n", encoding="utf-8"
    )
    return overspeed_summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate synthetic crossing frames (demonstration only)"
    )
    parser.add_argument(
        "--output-dir",
        default="work/crossing-demo",
        help="Directory for generated frames and summary",
    )
    args = parser.parse_args()
    print(json.dumps(generate_demo(args.output_dir)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
