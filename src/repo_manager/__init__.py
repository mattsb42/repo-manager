"""repo-manager: Manage your GitHub repository with source control."""
import argparse
import logging
from typing import Sequence

from ._groups import apply_config, parse_config
from ._util import load_context, load_inputs

__all__ = ("__version__",)
__version__ = "1.1.0"
_LOGGER = logging.getLogger(__name__)


def _arguments() -> argparse.ArgumentParser:
    """Prepare the argument parser."""
    args = argparse.ArgumentParser(description="")
    args.add_argument("--version", action="version", version=__version__)
    args.add_argument(
        "-v", dest="verbosity", action="count", help="Enables logging and sets detail level.",
    )

    return args


def _setup_logger(verbosity: int, debug: bool):
    """Set up logging."""
    formatter = logging.Formatter(
        "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logging_level = logging.DEBUG if verbosity or debug else logging.INFO
    logger.setLevel(logging_level)
    logger.addHandler(handler)


def cli(raw_args: Sequence[str] = None):
    """CLI entry point."""

    parser = _arguments()
    parsed = parser.parse_args(args=raw_args)

    input_values = load_inputs()

    _setup_logger(parsed.verbosity, input_values.debug)
    if parsed.verbosity:
        _LOGGER.debug("Debug logging enabled via CLI.")
    if input_values.debug:
        _LOGGER.debug("Debug logging enabled via environment variable.")

    context = load_context()
    prepped_config = parse_config(input_values, context)
    apply_config(prepped_config)
