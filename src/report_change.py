import argparse
import glob
import os
import pandas as pd

from test import get_logger

def get_change(dirty_df, clean_df):
    # Set 'id' as the index for easy comparison
    dirty_df.set_index('id', inplace=True)
    clean_df.set_index('id', inplace=True)

    # Find common ids (present in both dirty and clean data)
    common_ids = dirty_df.index.intersection(clean_df.index)

    # Find removed ids (present in dirty, not in clean)
    removed_ids = dirty_df.index.difference(clean_df.index)

    # Subset dataframes to common ids for cell comparison
    dirty_common = dirty_df.loc[common_ids].sort_index()
    clean_common = clean_df.loc[common_ids].sort_index()

    # Boolean DataFrame of cell-level changes
    changes = dirty_common != clean_common

    # Count cell changes only in common rows
    total_changed_cells = changes.sum().sum()

    # Count rows with changes in common rows
    rows_with_cell_changes = changes.any(axis=1).sum()

    # Add count of removed rows to total changed rows
    total_changed_rows = rows_with_cell_changes + len(removed_ids)

    # Count per-column cell changes
    column_change_counts = changes.sum()

    return total_changed_cells, total_changed_rows, rows_with_cell_changes, removed_ids, column_change_counts

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
    logger = get_logger(os.path.join(args.outdir, 'report_change.log'))

    for clean_f in glob.glob(os.path.join(args.cleandir, '*.csv')):
        fn = os.path.basename(clean_f)
        dirty_f = os.path.join(args.dirtydir, fn)
        if (os.path.isfile(dirty_f)):
            # print(clean_f, dirty_f)
            # continue
            # Load the dirty and cleaned data files
            dirty_df = pd.read_csv(dirty_f)
            clean_df = pd.read_csv(clean_f)
            total_changed_cells, total_changed_rows, rows_with_cell_changes, removed_ids, column_change_counts = get_change(dirty_df, clean_df)
            logger.info('='*70, extra={'simple': True})
            logger.info(f'Filename: {fn}', extra={'simple': True})
            # Display the results
            logger.info(f"Total changed rows (modified + removed): {total_changed_rows}", extra={'simple': True})
            logger.info(f" - Modified rows: {rows_with_cell_changes}", extra={'simple': True})
            logger.info(f" - Removed rows: {len(removed_ids)}", extra={'simple': True})
            logger.info(f"Total changed cells (excluding removed rows): {total_changed_cells}", extra={'simple': True})
            logger.info("\nChanged cells per column:", extra={'simple': True})
            logger.info(column_change_counts, extra={'simple': True})
            logger.info('\n', extra={'simple': True})

            # Optionally save column-level change counts to a CSV
            column_change_counts.to_csv(os.path.join(args.outdir, f'changed_{fn}'), header=['changed_cells'])