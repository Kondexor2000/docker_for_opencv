"""CLI: python -m app INPUT --output OUTPUT"""

import argparse
import json

from app.processor import process_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect image edges with OpenCV")
    parser.add_argument("input", help="Path to an input image")
    parser.add_argument("--output", default="output.png", help="Path to save edge map")
    args = parser.parse_args()
    try:
        print(json.dumps(process_file(args.input, args.output)))
    except (ValueError, OSError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
