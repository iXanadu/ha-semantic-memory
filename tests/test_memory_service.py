"""Unit tests for memory_service logic."""

import pytest

from server.services.memory_service import _build_search_text, _expand_key


def test_expand_key_snake_case():
    assert _expand_key("my_location") == "my location"


def test_expand_key_camel_case():
    assert _expand_key("wifeName") == "wife name"


def test_expand_key_mixed():
    assert _expand_key("my_wifeName") == "my wife name"


def test_expand_key_hyphens():
    assert _expand_key("home-address") == "home address"


def test_build_search_text_basic():
    result = _build_search_text("my_location", "Portland, OR", "home address")
    assert "my location" in result
    assert "my_location" in result
    assert "Portland, OR" in result
    assert "home address" in result


def test_build_search_text_no_tags():
    result = _build_search_text("pet_name", "Rex", "")
    assert "pet name" in result
    assert "pet_name" in result
    assert "Rex" in result
