import pytest
import sys
import os

# Add the src directory to the Python path

from src.validation import *


def test_string_validation():
    """Test string validation functions."""
    # Valid cases
    assert validate_string("valid string", "test") == True
    assert validate_string("abc", "test", min_length=3) == True
    
    # Invalid cases
    with pytest.raises(TypeError):
        validate_string(123, "test")
    
    with pytest.raises(ValueError):
        validate_string("", "test")
    
    with pytest.raises(ValueError):
        validate_string("ab", "test", min_length=3)
    
    with pytest.raises(ValueError):
        validate_string("toolong", "test", max_length=5)


def test_integer_validation():
    """Test integer validation functions."""
    # Valid cases
    assert validate_integer(5, "test") == True
    assert validate_integer(10, "test", min_val=5, max_val=15) == True
    
    # Invalid cases
    with pytest.raises(TypeError):
        validate_integer("not_int", "test")
    
    with pytest.raises(ValueError):
        validate_integer(3, "test", min_val=5)
    
    with pytest.raises(ValueError):
        validate_integer(20, "test", max_val=15)


def test_boolean_validation():
    """Test boolean validation functions."""
    # Valid cases
    assert validate_boolean(True, "test") == True
    assert validate_boolean(False, "test") == True
    
    # Invalid cases
    with pytest.raises(TypeError):
        validate_boolean("true", "test")
    
    with pytest.raises(TypeError):
        validate_boolean(1, "test")


def test_email_validation():
    """Test email validation."""
    # Valid emails
    assert validate_email("test@example.com") == True
    assert validate_email("user.name+tag@domain.co.uk") == True
    assert validate_email("user123@test-domain.org") == True
    
    # Invalid emails
    with pytest.raises(ValueError):
        validate_email("invalid-email")
    
    with pytest.raises(ValueError):
        validate_email("@domain.com")
    
    with pytest.raises(ValueError):
        validate_email("user@")
    
    with pytest.raises(ValueError):
        validate_email("user.domain.com")


def test_club_code_validation():
    """Test club code validation."""
    # Valid codes
    assert validate_club_code("valid-club") == True
    assert validate_club_code("club_123") == True
    assert validate_club_code("CLUB-name") == True
    
    # Invalid codes
    with pytest.raises(ValueError):
        validate_club_code("club with spaces")
    
    with pytest.raises(ValueError):
        validate_club_code("a")  # too short
    
    with pytest.raises(ValueError):
        validate_club_code("club@special")  # invalid characters
    
    with pytest.raises(TypeError):
        validate_club_code(123)


def test_tags_validation():
    """Test tags validation."""
    # Valid tags
    assert validate_tags(["tag1", "tag2"]) == True
    assert validate_tags({"tag1", "tag2", "tag3"}) == True
    assert validate_tags([]) == True
    
    # Invalid tags
    with pytest.raises(TypeError):
        validate_tags("not_list_or_set")
    
    with pytest.raises(ValueError):
        validate_tags(["tag1"] * 11)  # too many tags
    
    with pytest.raises(ValueError):
        validate_tags(["a"])  # tag too short


def test_sanitize_html():
    """Test HTML sanitization."""
    assert sanitize_html("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    assert sanitize_html("normal text") == "normal text"
    assert sanitize_html(None) == None
    assert sanitize_html("") == ""


def test_validate_json_input():
    """Test JSON input validation."""
    # Valid cases
    assert validate_json_input({"key": "value"}) == True
    assert validate_json_input({"field1": "value1"}, ["field1"]) == True
    
    # Invalid cases
    with pytest.raises(ValidationError):
        validate_json_input(None)
    
    with pytest.raises(ValidationError):
        validate_json_input({})
    
    with pytest.raises(ValidationError):
        validate_json_input({"field1": "value1"}, ["field1", "missing_field"])