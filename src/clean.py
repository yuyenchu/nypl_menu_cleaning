import argparse
import json
# import numpy as np
import os
import pandas as pd
from datetime import datetime

def load_data(file_path):
    return pd.read_csv(file_path)

def try_parse_date(dt, date_str, format):
    if (dt is None):
        try:
            return datetime.strptime(date_str, format)
        except: 
            return None
    else:
        return dt

def clamp_year(date_str):
    date_str = str(date_str)
    dt = try_parse_date(None, date_str,'%Y-%m-%d')
    dt = try_parse_date(dt, date_str,'%Y/%m/%d')
    dt = try_parse_date(dt, date_str,'%Y-%m')
    dt = try_parse_date(dt, date_str,'%Y/%m')
    dt = try_parse_date(dt, date_str,'%Y')
    dt = try_parse_date(dt, date_str,'%Y')
    if (dt is None):
        return ''
    dt = dt.replace(year=min(2025, max(1500, dt.year)))
    return dt.strftime('%Y-%m-%d')

def clean_data(df, filename, failed_ids_files):
    # Remove zero ID values and drop duplicates
    if 'id' in df.columns:
        df = df[df['id'] != 0]
        df = df.drop_duplicates(subset=['id'])

    if filename.startswith("MenuPage") and 'menu_id' in df.columns:
        df = df[df['menu_id'] != 0]
    if filename.startswith("MenuItem"):
        if 'menu_page_id' in df.columns:
            df = df[df['menu_page_id'] != 0]
        if 'dish_id' in df.columns:
            df = df[df['dish_id'] != 0]

    # Remove rows listed in failed ID JSONs
    for failed_ids_file in failed_ids_files:
        with open(failed_ids_file) as f:
            failed_ids = json.load(f)
        if 'id' in df.columns:
            df = df[~df['id'].isin(failed_ids)]

    # Fix price rules
    if 'price' in df.columns and 'high_price' in df.columns:
        df.loc[df['high_price'] < df['price'], 'high_price'] = df['price']

    # Fix created_at vs updated_at
    if 'created_at' in df.columns and 'updated_at' in df.columns:
        df.loc[df['created_at'] > df['updated_at'], 'updated_at'] = df['created_at']

    # Fix date
    if 'date' in df.columns:
        df['date'] = df['date'].apply(lambda x: clamp_year(x))

    # Clamp years to >= 1500
    if 'first_appeared' in df.columns:
        df['first_appeared'] = df['first_appeared'].apply(lambda x: min(2025, max(x, 1500)))
    if 'last_appeared' in df.columns:
        df['last_appeared'] = df['last_appeared'].apply(lambda x: min(2025, max(x, 1500)))

    return df

def save_data(df, output_path):
    df.to_csv(output_path, index=False)

def get_parser():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='options for cleaning')
    parser.add_argument(
        '-i', '--inpdir',
        help='path to the dataset folder',
        type=str,
        default='../data/NYPL-menus',  # Default dataset path
    )
    parser.add_argument(
        '-o', '--outdir',
        help='path to the output directory',
        type=str,
        default='../data//NYPL-menus-clean', 
    )
    parser.add_argument(
        '-t', '--testdir',
        help='path to the test results directory',
        type=str,
        default='../data/test_output_dirty', 
    )

    return parser

# if you want to run this on your local maschine, please change the input_folder, test_folder and output_folder to your local path
def main():
    args = get_parser().parse_args()
    print('Configs =', args)

    input_folder = args.inpdir
    output_folder = args.outdir
    test_folder = args.testdir

    # if the output folder does not exist, create it
    os.makedirs(output_folder, exist_ok=True)

    # group test files by table so that we only apply the relevant ones
    failed_ids_by_table = {
        "Dish": [
            "TestDishYearValid_FailedID.json",
            "TestDisPriceValid_FailedID.json"
        ],
        "Menu": [
            "TestTablesSchema_FailedID.json"
        ],
        "MenuPage": [
            "TestMenuPageDuplicate_FailedID.json",
            "TestMenuPageNumberValid_FailedID.json"
        ],
        "MenuItem": [
            "TestMenuItemNumberValid_FailedID.json",
            "TestMenuItemDateValid_FailedID.json"
        ]
    }

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_folder, file_name)
            print(f"Cleaning {file_name}...")

            table_name = file_name.replace(".csv", "")
            df = load_data(file_path)

            # Load only relevant failed ID files
            relevant_tests = failed_ids_by_table.get(table_name, [])
            failed_ids_files = [os.path.join(test_folder, f) for f in relevant_tests]

            cleaned_df = clean_data(df, file_name, failed_ids_files)

            output_file_path = os.path.join(output_folder, f"cleaned_{file_name}")
            save_data(cleaned_df, output_file_path)
            print(f"Saved cleaned {file_name} to {output_file_path}")

if __name__ == '__main__':
    main()
