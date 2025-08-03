# @begin main
# @in NYPL-menus/*.csv @AS filename
# @in test_output_dirty/*.json @AS failed_ids_files
# @out NYPL-menus-clean/*.csv @AS output_files
import argparse
import json
import os
import pandas as pd
from datetime import datetime

# @begin load_data
# @in file_path
# @out df
def load_data(file_path):
    return pd.read_csv(file_path)
# @end load_data

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

# @begin clean_data
# @in df
# @in filename
# @in failed_ids_files
# @out cleaned_df
def clean_data(df, filename, failed_ids_files):
    # @begin remove_zero_ids
    # @in df
    # @out df_1
    if 'id' in df.columns:
        df = df[df['id'] != 0]
        df = df.drop_duplicates(subset=['id'])
    # @end remove_zero_ids

    if filename.startswith("MenuPage") and 'menu_id' in df.columns:
        df = df[df['menu_id'] != 0]
    if filename.startswith("MenuItem"):
        if 'menu_page_id' in df.columns:
            df = df[df['menu_page_id'] != 0]
        if 'dish_id' in df.columns:
            df = df[df['dish_id'] != 0]

    for failed_ids_file in failed_ids_files:
        with open(failed_ids_file) as f:
            failed_ids = json.load(f)
        if 'id' in df.columns:
            df = df[~df['id'].isin(failed_ids)]
    
    # @begin clamp_high_price
    # @in df_1
    # @out df_2
    if 'price' in df.columns and 'high_price' in df.columns:
        df.loc[df['high_price'] < df['price'], 'high_price'] = df['price']
    # @end clamp_high_price
    
    # @begin clamp_updated_at
    # @in df_2
    # @out df_3
    if 'created_at' in df.columns and 'updated_at' in df.columns:
        df.loc[df['created_at'] > df['updated_at'], 'updated_at'] = df['created_at']
    # @end clamp_updated_at
    
    # @begin clamp_year
    # @in df_3
    # @out df_4
    if 'date' in df.columns:
        df['date'] = df['date'].apply(lambda x: clamp_year(x))
    # @end clamp_year
    
    # @begin clamp_first_appeared
    # @in df_4
    # @out df_5
    if 'first_appeared' in df.columns:
        df['first_appeared'] = df['first_appeared'].apply(lambda x: min(2025, max(x, 1500)))
    # @end clamp_first_appeared
    
    # @begin clamp_last_appeared
    # @in df_5
    # @out cleaned_df
    if 'last_appeared' in df.columns:
        df['last_appeared'] = df['last_appeared'].apply(lambda x: min(2025, max(x, 1500)))
    # @end clamp_last_appeared
    return df
# @end clean_data


# @begin save_data
# @in cleaned_df
# @in output_path
# @out output_files
def save_data(df, output_path):
    df.to_csv(output_path, index=False)
# @end save_data

# @begin get_parser
# @out file_path
# @out output_path
def get_parser():
    parser = argparse.ArgumentParser(description='options for cleaning')
    parser.add_argument('-i', '--inpdir', help='path to the dataset folder', type=str, default='../data/NYPL-menus')
    parser.add_argument('-o', '--outdir', help='path to the output directory', type=str, default='../data/NYPL-menus-clean')
    parser.add_argument('-t', '--testdir', help='path to the test results directory', type=str, default='../data/test_output_dirty')
    return parser
# @end get_parser

def main():
    args = get_parser().parse_args()
    print('Configs =', args)

    input_folder = args.inpdir
    output_folder = args.outdir
    test_folder = args.testdir

    os.makedirs(output_folder, exist_ok=True)

    failed_ids_by_table = {
        "Dish": ["TestDishYearValid_FailedID.json", "TestDisPriceValid_FailedID.json"],
        "Menu": ["TestTablesSchema_FailedID.json"],
        "MenuPage": ["TestMenuPageDuplicate_FailedID.json", "TestMenuPageNumberValid_FailedID.json"],
        "MenuItem": ["TestMenuItemNumberValid_FailedID.json", "TestMenuItemDateValid_FailedID.json"]
    }

    for file_name in os.listdir(input_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(input_folder, file_name)
            print(f"Cleaning {file_name}...")

            table_name = file_name.replace(".csv", "")
            df = load_data(file_path)

            relevant_tests = failed_ids_by_table.get(table_name, [])
            failed_ids_files = [os.path.join(test_folder, f) for f in relevant_tests]

            cleaned_df = clean_data(df, file_name, failed_ids_files)

            output_file_path = os.path.join(output_folder, f"cleaned_{file_name}")
            save_data(cleaned_df, output_file_path)
            print(f"Saved cleaned {file_name} to {output_file_path}")
# @end main

if __name__ == '__main__':
    main()