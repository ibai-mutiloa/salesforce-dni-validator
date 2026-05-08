"""Unit tests for text processing utilities"""
import pytest
from app.utils import normalize_name, fuzzy_match_names, combine_names, remove_accents


class TestTextNormalization:
    """Tests for text normalization functions"""
    
    def test_normalize_name_basic(self):
        """Test basic name normalization"""
        assert normalize_name("John") == "john"
        assert normalize_name("  spaces  ") == "spaces"
    
    def test_normalize_name_accents(self):
        """Test accent removal"""
        assert normalize_name("José") == "jose"
        assert normalize_name("García") == "garcia"
        assert normalize_name("François") == "francois"
    
    def test_normalize_name_special_chars(self):
        """Test special character removal"""
        assert normalize_name("John's") == "johns"
        assert normalize_name("O'Connor") == "oconnor"
    
    def test_normalize_empty_string(self):
        """Test normalization of empty string"""
        assert normalize_name("") == ""
        assert normalize_name("   ") == ""
    
    def test_remove_accents(self):
        """Test accent removal function"""
        assert remove_accents("café") == "cafe"
        assert remove_accents("naïve") == "naive"


class TestFuzzyMatching:
    """Tests for fuzzy matching functions"""
    
    def test_exact_match(self):
        """Test exact name match"""
        score, is_match = fuzzy_match_names("John", "John", 80)
        assert is_match is True
        assert score == 100.0
    
    def test_case_insensitive_match(self):
        """Test case-insensitive matching"""
        score, is_match = fuzzy_match_names("JOHN", "john", 80)
        assert is_match is True
        assert score == 100.0
    
    def test_accent_insensitive_match(self):
        """Test accent-insensitive matching"""
        score, is_match = fuzzy_match_names("José", "Jose", 80)
        assert is_match is True
        assert score >= 90
    
    def test_partial_match(self):
        """Test partial name match"""
        score, is_match = fuzzy_match_names("Jon", "Jonathan", 80)
        assert is_match is True  # Token sort ratio should match
    
    def test_no_match(self):
        """Test non-matching names"""
        score, is_match = fuzzy_match_names("John", "Carlos", 80)
        assert is_match is False
        assert score < 50
    
    def test_similar_match(self):
        """Test similar but not exact match"""
        score, is_match = fuzzy_match_names("John", "Juan", 80)
        # These are similar but may not meet 80% threshold
        assert score > 50
    
    def test_threshold_boundary(self):
        """Test threshold boundary conditions"""
        # This should fail with high threshold
        score, is_match = fuzzy_match_names("John", "Juan", 90)
        assert is_match is False


class TestNameCombination:
    """Tests for name combination"""
    
    def test_combine_full_names(self):
        """Test combining first and last names"""
        result = combine_names("John", "Smith")
        assert result == "John Smith"
    
    def test_combine_with_empty(self):
        """Test combining with empty names"""
        assert combine_names("John", "") == "John"
        assert combine_names("", "Smith") == "Smith"
        assert combine_names("", "") == ""
    
    def test_combine_with_spaces(self):
        """Test combining with extra spaces"""
        result = combine_names("  John  ", "  Smith  ")
        assert result == "John Smith"
    
    def test_combine_single_name(self):
        """Test combining single names"""
        result = combine_names("Madonna", "")
        assert result == "Madonna"


class TestNameCombining:
    """Tests for name combining functions"""
    
    def test_combine_two_names(self):
        """Test combining two names"""
        combined = combine_names("John", "Smith")
        assert combined == "John Smith"
    
    def test_combine_with_empty(self):
        """Test combining with empty string"""
        combined = combine_names("John", "")
        assert combined == "John"
