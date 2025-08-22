import os
import pytest
from utils import format_file_size, is_supported_image, is_supported_pdf, validate_file_size

def test_format_file_size():
    assert format_file_size(100) == "100.0 B"
    assert format_file_size(1500) == "1.5 KB"
    assert format_file_size(1500000) == "1.4 MB"
    assert format_file_size(1500000000) == "1.4 GB"

def test_is_supported_image():
    assert is_supported_image("test.jpg") == True
    assert is_supported_image("test.jpeg") == True
    assert is_supported_image("test.png") == True
    assert is_supported_image("test.webp") == True
    assert is_supported_image("test.gif") == False
    assert is_supported_image("test.pdf") == False

def test_is_supported_pdf():
    assert is_supported_pdf("test.pdf") == True
    assert is_supported_pdf("test.txt") == False
    assert is_supported_pdf("test.jpg") == False

def test_validate_file_size(tmp_path):
    # Create a dummy file of 1KB
    file_path = tmp_path / "test_file.txt"
    with open(file_path, "wb") as f:
        f.write(os.urandom(1024))

    assert validate_file_size(file_path, max_size_mb=1) == True
    assert validate_file_size(file_path, max_size_mb=0.0009) == False

    # Test with a non-existent file
    assert validate_file_size("non_existent_file.txt") == False
