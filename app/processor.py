"""Image processing helpers used by the CLI and tests."""

from pathlib import Path

import cv2


def read_image(path: str | Path):
    """Load an image in color, raising a useful error if it cannot be read."""
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def detect_edges(image, low_threshold: int = 100, high_threshold: int = 200):
    """Return a Canny edge map for a color or grayscale image."""
    if image is None or image.size == 0:
        raise ValueError("Image must not be empty")
    if low_threshold < 0 or high_threshold <= low_threshold:
        raise ValueError("Thresholds must satisfy 0 <= low_threshold < high_threshold")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    return cv2.Canny(blurred, low_threshold, high_threshold)


def process_file(input_path: str | Path, output_path: str | Path) -> dict:
    """Detect edges, write a PNG-compatible output, and return a small summary."""
    image = read_image(input_path)
    edges = detect_edges(image)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output), edges):
        raise OSError(f"Could not write output image: {output}")
    return {"width": int(edges.shape[1]), "height": int(edges.shape[0]),
            "edge_pixels": int(cv2.countNonZero(edges)), "output": str(output)}
