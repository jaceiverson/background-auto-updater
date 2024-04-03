import logging

from rich.logging import RichHandler

logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    handlers=[RichHandler(markup=True)],
)
logger = logging.getLogger("rich")

"""
We like to use rich for logging and for traceback
it provides a nicer output
"""
