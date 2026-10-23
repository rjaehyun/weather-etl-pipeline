import pytest
import pandas as pd
from datetime import datetime
from src.fetch_weather import clean_data
from src.validate import validate_data


class TestCleaning:
    """Test the clean_data function."""
    
    def test_clean_converts_date_to_datetime(self):
        """Dates should be converted to datetime type."""
        df = pd.DataFrame({
            "city": ["Manila"],
            "date": ["2026-10-16"],
            "temp_max": [31.5],
            "temp_min": [25.2],
            "rainfall": [0.0],
        })
        result = clean_data(df)
        assert str(result["date"].dtype).startswith("datetime64")
    
    def test_clean_converts_temps_to_float(self):
        """Temperature columns should be float."""
        df = pd.DataFrame({
            "city": ["Manila"],
            "date": ["2026-10-16"],
            "temp_max": ["31.5"],
            "temp_min": ["25.2"],
            "rainfall": ["0.0"],
        })
        result = clean_data(df)
        assert result["temp_max"].dtype == "float64"
        assert result["temp_min"].dtype == "float64"
    
    def test_clean_sorts_by_city_and_date(self):
        """Data should be sorted by city, then date."""
        df = pd.DataFrame({
            "city": ["Davao", "Manila", "Cebu"],
            "date": ["2026-10-16", "2026-10-16", "2026-10-16"],
            "temp_max": [30, 31, 29],
            "temp_min": [25, 26, 24],
            "rainfall": [0, 0, 0],
        })
        result = clean_data(df)
        assert result.iloc[0]["city"] == "Cebu"
        assert result.iloc[-1]["city"] == "Manila"
    
    def test_clean_replaces_sentinel_values(self):
        """Sentinel values like -9999 should become NaN."""
        df = pd.DataFrame({
            "city": ["Manila"],
            "date": ["2026-10-16"],
            "temp_max": [-9999],
            "temp_min": [25.2],
            "rainfall": [0.0],
        })
        result = clean_data(df)
        assert pd.isna(result.iloc[0]["temp_max"])


class TestValidation:
    """Test the validate_data function."""
    
    def test_validate_passes_good_data(self):
        """Good data should pass validation."""
        df = pd.DataFrame({
            "city": ["Manila"],
            "date": [pd.Timestamp("2026-10-16")],
            "temp_max": [31.5],
            "temp_min": [25.2],
            "rainfall": [0.0],
        })
        clean_df, rejected_df = validate_data(df)
        assert len(clean_df) == 1
        assert len(rejected_df) == 0
    
    def test_validate_rejects_unrealistic_temps(self):
        """Very high temps should be rejected."""
        df = pd.DataFrame({
            "city": ["Manila"],
            "date": [pd.Timestamp("2026-10-16")],
            "temp_max": [60.0],  # Unrealistic
            "temp_min": [25.2],
            "rainfall": [0.0],
        })
        clean_df, rejected_df = validate_data(df)
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
    
    def test_validate_rejects_inverted_temps(self):
        """Max < Min should be rejected."""
        df = pd.DataFrame({
            "city": ["Manila"],
            "date": [pd.Timestamp("2026-10-16")],
            "temp_max": [25.0],
            "temp_min": [30.0],  # Inverted
            "rainfall": [0.0],
        })
        clean_df, rejected_df = validate_data(df)
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
        assert "temp_max < temp_min" in rejected_df.iloc[0]["reject_reason"]
    
    def test_validate_rejects_negative_rainfall(self):
        """Negative rainfall should be rejected."""
        df = pd.DataFrame({
            "city": ["Manila"],
            "date": [pd.Timestamp("2026-10-16")],
            "temp_max": [31.5],
            "temp_min": [25.2],
            "rainfall": [-1.0],  # Negative
        })
        clean_df, rejected_df = validate_data(df)
        assert len(clean_df) == 0
        assert len(rejected_df) == 1
    
    def test_validate_mixed_data(self):
        """Mix of good and bad rows should split correctly."""
        df = pd.DataFrame({
            "city": ["Manila", "Manila", "Manila"],
            "date": [pd.Timestamp("2026-10-16"), pd.Timestamp("2026-10-17"), pd.Timestamp("2026-10-18")],
            "temp_max": [31.5, 60.0, 30.0],  # Middle one is bad
            "temp_min": [25.2, 25.0, 24.0],
            "rainfall": [0.0, 0.0, 0.0],
        })
        clean_df, rejected_df = validate_data(df)
        assert len(clean_df) == 2
        assert len(rejected_df) == 1