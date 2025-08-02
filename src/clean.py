import pandas as pd
import numpy as np
import json
import os

def load_data(file_path):
    return pd.read_csv(file_path)

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

    # Clamp years to >= 1500
    if 'first_appeared' in df.columns:
        df['first_appeared'] = df['first_appeared'].apply(lambda x: max(x, 1500))
    if 'last_appeared' in df.columns:
        df['last_appeared'] = df['last_appeared'].apply(lambda x: max(x, 1500))

    return df

def save_data(df, output_path):
    df.to_csv(output_path, index=False)

# if you want to run this on your local maschine, please change the input_folder, test_folder and output_folder to your local path
def main():
    input_folder = '/Users/xian_zhao/Desktop/cs513/NYPL-menus'
    output_folder = '/Users/xian_zhao/Desktop/cs513/cleaned_data'
    test_folder = '/Users/xian_zhao/Desktop/cs513/test_output_dirty'

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
