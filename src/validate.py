import pandas as pd
from typing import Tuple


def validate_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Validate weather data and separate good from bad rows.
    
    Returns:
        (clean_df, rejected_df): Passing rows and rejected rows with reasons
    """
    df = df.copy()
    rejected_rows = []
    
    for idx, row in df.iterrows():
        reasons = []
        
        # Check 1: Temperature ranges
        if row["temp_max"] is not pd.NA and row["temp_max"] > 50:
            reasons.append("temp_max > 50°C (unrealistic)")
        if row["temp_min"] is not pd.NA and row["temp_min"] < -20:
            reasons.append("temp_min < -20°C (unrealistic)")
        
        # Check 2: Max should be >= Min
        if (row["temp_max"] is not pd.NA and row["temp_min"] is not pd.NA 
            and row["temp_max"] < row["temp_min"]):
            reasons.append("temp_max < temp_min (logical error)")
        
        # Check 3: Rainfall should be non-negative
        if row["rainfall"] is not pd.NA and row["rainfall"] < 0:
            reasons.append("rainfall < 0 (negative rainfall)")
        
        # Check 4: No missing city or date
        if pd.isna(row["city"]):
            reasons.append("city is null")
        if pd.isna(row["date"]):
            reasons.append("date is null")
        
        # If any issues, mark as rejected
        if reasons:
            rejected_row = row.copy()
            rejected_row["reject_reason"] = " | ".join(reasons)
            rejected_rows.append(rejected_row)
        
    # Build rejected DataFrame and clean DataFrame
    if rejected_rows:
        rejected_df = pd.DataFrame(rejected_rows)
        # Remove rejected rows from main DataFrame
        clean_df = df[~df.index.isin([r.name for r in rejected_rows])]
    else:
        rejected_df = pd.DataFrame(columns=list(df.columns) + ["reject_reason"])
        clean_df = df
    
    return clean_df, rejected_df


def print_validation_report(clean_df: pd.DataFrame, rejected_df: pd.DataFrame) -> None:
    """Print a summary of validation results."""
    total = len(clean_df) + len(rejected_df)
    print(f"\n{'='*60}")
    print("Data Validation Report")
    print(f"{'='*60}")
    print(f"Total rows: {total}")
    print(f"✓ Passed: {len(clean_df)}")
    print(f"✗ Rejected: {len(rejected_df)}")
    
    if len(rejected_df) > 0:
        print(f"\nRejection reasons:")
        for reason in rejected_df["reject_reason"].unique():
            count = (rejected_df["reject_reason"] == reason).sum()
            print(f"  - {reason}: {count} rows")