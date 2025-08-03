import argparse
import glob
import os
import pandas as pd


def get_change(dirty_df, clean_df):
    # Set 'id' as the index for easy comparison
    dirty_df.set_index('id', inplace=True)
    clean_df.set_index('id', inplace=True)

    # Align both DataFrames to ensure they have the same index order
    dirty_df = dirty_df.sort_index()
    clean_df = clean_df.sort_index()

    # Compare dataframes to find changed cells
    changes = dirty_df != clean_df

    # Count total number of changed cells
    total_changed_cells = changes.sum().sum()

    # Count number of rows that have at least one change
    rows_with_changes = changes.any(axis=1).sum()

    # Count changes per column
    column_change_counts = changes.sum()

    return total_changed_cells, rows_with_changes, column_change_counts

def get_parser():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='options for reporting changes')
    parser.add_argument(
        '-d', '--dirtydir',
        help='path to the dirty files directory',
        type=str,
        default='../data/NYPL-menus',  # Default dataset path
    )
    parser.add_argument(
        '-c', '--cleandir',
        help='path to the cleaned files directory',
        type=str,
        default='../data//NYPL-menus-cleaned', 
    )
    parser.add_argument(
        '-o', '--outdir',
        help='path to the output directory',
        type=str,
        default='.', 
    )
    return parser

if __name__=='__main__':
    args = get_parser().parse_args()
    print('Configs =', args)
    
    # make output folder
    os.makedirs(args.outdir, exist_ok=True)
    assert os.path.isdir(args.outdir), f'output path does not exist or is not directory: {args.outdir}'

    for clean_f in glob.glob(os.path.join(args.cleandir, '*.csv')):
        fn = os.path.basename(clean_f)
        dirty_f = os.path.join(args.dirtydir, fn)
        if (os.path.isfile(dirty_f)):
            # print(clean_f, dirty_f)
            # continue
            # Load the dirty and cleaned data files
            dirty_df = pd.read_csv(dirty_f)
            clean_df = pd.read_csv(clean_f)
            total_changed_cells, rows_with_changes, column_change_counts = get_change(dirty_df, clean_df)
            print(f'Filename: {fn}')
            # Display the results
            print(f"Total changed cells: {total_changed_cells}")
            print(f"Total rows with changes: {rows_with_changes}")
            print("\nChanged cells per column:")
            print(column_change_counts)

            # Optionally save column-level change counts to a CSV
            column_change_counts.to_csv(f'changed_count_{fn}', header=['changed_cells'])