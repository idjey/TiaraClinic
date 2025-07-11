import pandas as pd
from datetime import datetime

STANDARD_COLUMNS = [
    "visit_date", "treatment", "payment_method", "actual_amount",
    "deposit_paid", "deposit_method", "month", "year"
]

COLUMN_ALIASES = {
    "visit_date": ["date", "appointment_date", "service_date", "visit date"],
    "treatment": ["service", "procedure", "treatment type"],
    "payment_method": ["payment", "method of payment"],
    "actual_amount": ["amount", "total amount", "price"],
    "deposit_paid": ["deposit", "paid deposit"],
    "deposit_method": ["deposit payment method", "how deposit paid"],
    "month": ["month of visit"],
    "year": ["year of visit"]
}

# Columns that are strictly required and cannot be null
STRICTLY_REQUIRED_COLUMNS = [
    "visit_date", "treatment", "payment_method", "actual_amount"
]

def validate_excel(file_path):
    try:
        df = pd.read_excel(file_path)

        # Normalize columns (strip spaces, lowercase)
        df.columns = [col.strip().lower() for col in df.columns]

        # Rename columns based on aliases
        renamed_columns = {}
        for standard_col, aliases in COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in df.columns and standard_col not in renamed_columns.values():
                    renamed_columns[alias] = standard_col
                    break
        df.rename(columns=renamed_columns, inplace=True)

        # Check for strictly required columns after renaming
        if not all(col in df.columns for col in STRICTLY_REQUIRED_COLUMNS):
            missing = [col for col in STRICTLY_REQUIRED_COLUMNS if col not in df.columns]
            return None, f"Missing required columns: {', '.join(missing)}"

        # Type conversion and initial cleaning
        df["visit_date"] = pd.to_datetime(df["visit_date"], format="%d.%m.%y", errors="coerce").dt.date
        df["actual_amount"] = pd.to_numeric(df["actual_amount"], errors="coerce")

        # Convert 'deposit_paid' to boolean, handling various string representations
        df['deposit_paid'] = df['deposit_paid'].astype(str).str.lower().map({
            'yes': True, 'true': True, '1': True,
            'no': False, 'false': False, '0': False,
            '': False # Treat empty string as False
        }).fillna(False)

        # If deposit_paid is False, set deposit_method to None
        df.loc[df['deposit_paid'] == False, 'deposit_method'] = None

        # Drop rows where any of the STRICTLY_REQUIRED_COLUMNS are missing or invalid after conversion
        df.dropna(subset=STRICTLY_REQUIRED_COLUMNS, inplace=True)

        # Handle missing 'month' and 'year' by deriving from 'visit_date' if possible
        df['month'] = df.apply(lambda row: row['visit_date'].strftime('%B') if pd.notna(row['visit_date']) else None, axis=1)
        df['year'] = df.apply(lambda row: row['visit_date'].year if pd.notna(row['visit_date']) else None, axis=1)

        # Ensure year is integer or None
        df['year'] = df['year'].apply(lambda x: int(x) if pd.notna(x) else None)

        # Ensure all STANDARD_COLUMNS exist, fill missing with None if not strictly required
        for col in STANDARD_COLUMNS:
            if col not in df.columns:
                df[col] = None

        # Debugging: Print DataFrame before returning
        print("DataFrame after processing and before returning:")
        print(df.to_string())

        rows = df.to_dict(orient="records")
        return rows, None

    except Exception as e:
        return None, f"Error reading file: {str(e)}"
