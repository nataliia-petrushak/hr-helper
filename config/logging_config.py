import logging
import sys


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)8s]: %(message)s",
        handlers=[logging.FileHandler("parser.log"), logging.StreamHandler(sys.stdout)],
    )
