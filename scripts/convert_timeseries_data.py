

import pandas as pd
from pathlib import Path


def main(csv_data_folder):
    # Path to your folder containing .csv files
    folder = Path(csv_data_folder)

    # Columns to drop if they exist
    drop_cols = {"hour", "dayofweek", "month"}

    # Loop over all .csv files
    for file in folder.glob("*.csv"):
        print(f"Processing: {file.name}")

        # Load the CSV
        df = pd.read_csv(file)

        # Check if 'time' column exists
        if "time" not in df.columns:
            print(f"Skipping {file.name}: no 'time' column found.")
            continue

        # Detect format and convert
        first_value = str(df["time"].iloc[0])

        try:
            if "-" in first_value:  # format like "2015-01-01 00:00:00"
                df["time"] = pd.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
            else:  # format like "01/01/2015 14:00"
                df["time"] = pd.to_datetime(df["time"], format="%d/%m/%Y %H:%M", errors="coerce")
        except Exception as e:
            print(f"Error parsing {file.name}: {e}")
            continue

        # Reformat all datetimes to the desired format
        df["time"] = df["time"].dt.strftime("%d/%m/%Y %H:%M")

        # Drop unwanted columns if present
        df = df.drop(columns=[c for c in df.columns if c.lower() in drop_cols], errors="ignore")

        # Make 'time' the first column
        cols = ["time"] + [c for c in df.columns if c != "time"]
        df = df[cols]

        # Save in place
        df.to_csv(file, index=False)

    print("Done: all CSV files processed and saved in place.")

if __name__ == "__main__":
    main(csv_data_folder="input_data/ScenarioData")