#!/usr/bin/env python3
"""
Test runner script for the Flask club review application.
Runs all test suites and provides a comprehensive report.
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def main():
    """Run all tests and report results."""
    print("Flask Club Review Application - Test Suite Runner")
    print("=" * 60)
    
    # Change to the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Updated test commands for new structure
    tests = [
        ("python -m pytest tests/test_validation.py -v", "Validation Tests"),
        ("python -m pytest tests/test_models.py -v", "Model Tests"),
        ("python -m pytest tests/test_apis.py", "API functionality tests"),
        ("python -m pytest tests/test_api_validation.py -v", "API I/O Tests"),
        ("python -m pytest tests/test_reviews.py -v", "Review Model Tests"),
        ("python -m pytest tests/test_review_apis.py -v", "Review API Tests"),
        ("python -m pytest tests/ -v", "All Tests Combined")
    ]
    
    results = []
    
    for command, description in tests:
        success = run_command(command, description)
        results.append((description, success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for description, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"{description}: {status}")
        if not success:
            all_passed = False
    
    print(f"\nOverall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    # Run a quick validation check
    print(f"\n{'='*60}")
    print("VALIDATION MODULE CHECK")
    print(f"{'='*60}")
    
    try:
        sys.path.insert(0, 'src')
        from validation import validate_string, validate_email, validate_club_code
        print("✓ Validation module imported successfully")
        
        # Test basic functions
        validate_string("test", "test")
        validate_email("test@example.com")
        validate_club_code("test-club")
        print("✓ Basic validation functions working")
        
    except Exception as e:
        print(f"✗ Validation module error: {e}")
        all_passed = False
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())