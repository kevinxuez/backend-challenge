"""
Validation utilities for the Flask club review application.
Provides comprehensive input validation and sanitization functions.
"""
import re
import html
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_string(value, name, min_length=1, max_length=None, required=True):
    """Validate string inputs with length constraints."""
    try:
        if not required and (value is None or value == ""):
            return True
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string")
        if not value or not value.strip():
            raise ValueError(f"{name} cannot be empty")
        if len(value.strip()) < min_length:
            raise ValueError(f"{name} must be at least {min_length} characters")
        if max_length and len(value) > max_length:
            raise ValueError(f"{name} cannot exceed {max_length} characters")
        return True
    except (ValueError, TypeError) as e:
        logger.warning(f"Validation failed for {name}: {str(e)}")
        raise


def validate_integer(value, name, min_val=None, max_val=None, required=True):
    """Validate integer inputs with range constraints."""
    try:
        if not required and value is None:
            return True
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if min_val is not None and value < min_val:
            raise ValueError(f"{name} must be at least {min_val}")
        if max_val is not None and value > max_val:
            raise ValueError(f"{name} cannot exceed {max_val}")
        return True
    except (ValueError, TypeError) as e:
        logger.warning(f"Validation failed for {name}: {str(e)}")
        raise


def validate_boolean(value, name, required=True):
    """Validate boolean inputs."""
    try:
        if not required and value is None:
            return True
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be a boolean")
        return True
    except (ValueError, TypeError) as e:
        logger.warning(f"Validation failed for {name}: {str(e)}")
        raise


def validate_email(email):
    """Validate email format using regex."""
    try:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        return True
    except ValueError as e:
        logger.warning(f"Email validation failed: {str(e)}")
        raise


def validate_club_code(code):
    """Validate club code format."""
    try:
        if not isinstance(code, str):
            raise TypeError("Club code must be a string")
        if not code or not code.strip():
            raise ValueError("Club code cannot be empty")
        # Allow alphanumeric, hyphens, underscores
        if not re.match(r'^[a-zA-Z0-9\-_]+$', code.strip()):
            raise ValueError("Club code can only contain letters, numbers, hyphens, and underscores")
        if len(code.strip()) < 2 or len(code.strip()) > 50:
            raise ValueError("Club code must be between 2-50 characters")
        return True
    except (ValueError, TypeError) as e:
        logger.warning(f"Club code validation failed: {str(e)}")
        raise


def validate_tags(tags):
    """Validate tags input."""
    try:
        if not isinstance(tags, (set, list)):
            raise TypeError("Tags must be a set or list")
        if len(tags) > 10:
            raise ValueError("Cannot have more than 10 tags")
        for tag in tags:
            validate_string(tag, "Tag", min_length=2, max_length=50)
        return True
    except (ValueError, TypeError) as e:
        logger.warning(f"Tags validation failed: {str(e)}")
        raise


def sanitize_html(text):
    """Remove potentially dangerous HTML from text."""
    return html.escape(text) if text else text


def validate_json_input(data, required_fields=None):
    """Validate JSON input exists and has required fields."""
    if not data:
        raise ValidationError("No input data provided")
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return True