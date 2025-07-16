# app/logging_setup.py
# Sets up rich, JSON, and file-based logging
import logging
import os
import sys
from rich.traceback import install as install_traceback
from rich.logging import RichHandler
from pythonjsonlogger import jsonlogger

def setup_logger(name: str = "app", level=logging.DEBUG) -> logging.Logger:
    install_traceback(show_locals=True, word_wrap=True)

    console_handler = RichHandler(rich_tracebacks=True)
    console_handler.setLevel(level)

    file_handler = logging.FileHandler("/Users/davrondjabborov/Work/haive/haive/packages/haive-dataflow/src/haive/dataflow/api/routes/copilotkit/copilotkit_fastapi_project/logs/copilotkit_verbose.log", mode="w", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))

    json_handler = logging.FileHandler("/Users/davrondjabborov/Work/haive/haive/packages/haive-dataflow/src/haive/dataflow/api/routes/copilotkit/copilotkit_fastapi_project/logs/copilotkit_verbose.json", mode="w", encoding="utf-8")
    json_handler.setFormatter(jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s %(payload)s %(response)s'
    ))

    logging.basicConfig(
        level=level,
        handlers=[console_handler, file_handler, json_handler],
        force=True
    )

    return logging.getLogger(name)
