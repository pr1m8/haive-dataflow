
:py:mod:`dataflow.utils.logging`
================================

.. py:module:: dataflow.utils.logging

Logging utilities for the Haive Registry System.

This module provides logging utilities for the registry system,
including setup functions for various log types.


.. autolink-examples:: dataflow.utils.logging
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.utils.logging.log_entity_operation
   dataflow.utils.logging.setup_discovery_logger
   dataflow.utils.logging.setup_import_logger
   dataflow.utils.logging.setup_logger
   dataflow.utils.logging.setup_operation_logger

.. py:function:: log_entity_operation(logger: logging.Logger, operation: str, entity_type: str, entity_name: str, entity_id: str | None = None, status: str = 'success', details: dict[str, Any] | None = None, error: Exception | None = None) -> None

   Log an entity operation with standardized format.

   :param logger: Logger to use
   :param operation: Operation being performed (e.g., 'register', 'update')
   :param entity_type: Type of entity
   :param entity_name: Name of entity
   :param entity_id: Optional ID of entity
   :param status: Operation status ('success' or 'failure')
   :param details: Optional additional details
   :param error: Optional exception if operation failed


   .. autolink-examples:: log_entity_operation
      :collapse:

.. py:function:: setup_discovery_logger(subtype: str | None = None) -> logging.Logger

   Set up a logger for discovery operations.

   :param subtype: Optional subtype (e.g., 'agents', 'tools')

   :returns: Configured logger


   .. autolink-examples:: setup_discovery_logger
      :collapse:

.. py:function:: setup_import_logger() -> logging.Logger

   Set up a logger for import operations.

   :returns: Configured logger


   .. autolink-examples:: setup_import_logger
      :collapse:

.. py:function:: setup_logger(name: str, log_file: str | None = None, level: int = logging.INFO, format_str: str | None = None, log_to_console: bool = True) -> logging.Logger

   Set up a logger with file and optional console handlers.

   :param name: Logger name
   :param log_file: Optional path to log file
   :param level: Logging level
   :param format_str: Optional format string for log messages
   :param log_to_console: Whether to log to console

   :returns: Configured logger


   .. autolink-examples:: setup_logger
      :collapse:

.. py:function:: setup_operation_logger() -> logging.Logger

   Set up a logger for registry operations.

   :returns: Configured logger


   .. autolink-examples:: setup_operation_logger
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.utils.logging
   :collapse:
   
.. autolink-skip:: next
