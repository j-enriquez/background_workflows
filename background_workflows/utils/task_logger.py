"""
Task Logger Configuration

This module configures the application's logging based on settings defined in AppConstants.
"""

import logging
from background_workflows.constants.app_constants import AppConstants

# Configure logging using settings from AppConstants.
logging.basicConfig(
    level=AppConstants.Logging.LEVEL,  # e.g., logging.DEBUG or logging.INFO
    format=AppConstants.Logging.FORMAT,
)

logger = logging.getLogger(AppConstants.Logging.LOGGER_NAME)
