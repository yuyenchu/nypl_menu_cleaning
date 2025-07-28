import argparse
import glob
import io
import logging
import numpy as np
import os
import pandas as pd
import unittest
from tqdm import tqdm

from test_base import (
    Dish,
    Menu,
    MenuPage,
    MenuItem,
    ENGINE, 
    LoggerTestRunner, 
    TestTablesSchema
)
from test_dish import TestDishYearValid, TestDisPriceValid

TABLE_MAP = {
    'Dish': Dish,
    'Menu': Menu,
    'MenuPage': MenuPage,
    'MenuItem': MenuItem,
}
TEST_GROUPS = {
    'schema': [TestTablesSchema],
    'dish': [TestDishYearValid, TestDisPriceValid],
    # 'menu': [TestMenuSomethingValid],
}


def get_logger(fn='test.log'):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG) 
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    file_handler = logging.FileHandler(fn)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger

def get_parser():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description='options for testing')
    parser.add_argument(
        '-p', '--path',
        help='path to the dataset folder',
        type=str,
        default='../data/NYPL-menus',  # Default dataset path
    )
    parser.add_argument(
        '--reset',
        nargs='*',
        metavar='TABLE',
        help=f'Reset tables and insert data, options: {list(TABLE_MAP.keys())}',
    )
    parser.add_argument(
        '--tests',
        nargs='*',
        metavar='TEST',
        help=f'Specify which test groups to run, options: {list(TEST_GROUPS.keys())}',
        default=[],
    )
    return parser

def load_selected_tests(selected_groups):
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    if ('all' in selected_groups):  # load all
        selected_groups = TEST_GROUPS.keys()

    for group in selected_groups:
        test_classes = TEST_GROUPS.get(group, [])
        for test_class in test_classes:
            suite.addTests(loader.loadTestsFromTestCase(test_class))

    return suite

def insert_data(f, engine):
    df = pd.read_csv(f)
    table_name = os.path.splitext(os.path.basename(f))[0]
    failed_rows = []
    logger.info(f'Start inserting into {table_name}')
    # Preprocess datetime columns: strip " UTC" and parse
    for col in ['created_at', 'updated_at']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col].str.replace(' UTC', '', regex=False), errors='coerce')
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        try:
            # Convert row to a DataFrame for to_sql
            pd.DataFrame([row]).to_sql(table_name, con=engine, if_exists='append', index=False)
        except KeyboardInterrupt:
            logger.error(f'User interrupted at row {idx}')
            np.save(f'{table_name}_failed.npy', np.array(failed_rows))
            exit()
        except Exception as e:
            logger.error(f'Failed to insert row {idx} - Error: {e}')
            failed_rows.append(idx)

    if failed_rows:
        logger.info(f'\n Summary of {len(failed_rows)} failed rows for table "{table_name}":')
        logger.info(df.iloc[failed_rows])
    return df, failed_rows

if __name__ == "__main__":
    logger = get_logger()
    args = get_parser().parse_args()
    print('Configs =', args)
    if (args.reset is not None):
        reset_tables = args.reset if args.reset else TABLE_MAP.keys()
        logger.info(f'Resetting tables: {list(reset_tables)}')

        # Reflect base metadata for partial drop
        for table in reset_tables:
            model = TABLE_MAP.get(table)
            if (model):
                logger.info(f'Dropping and creating table "{table}"')
                model.__table__.drop(ENGINE, checkfirst=True)
                model.__table__.create(ENGINE, checkfirst=True)
            else:
                logger.warning(f'Unknown table: {table}, skipping...')

        # Insert data only for reset tables
        for f in glob.glob(os.path.join(args.path, "*.csv")):
            table_name = os.path.splitext(os.path.basename(f))[0]
            if (table_name in reset_tables):
                insert_data(f, ENGINE)
    
    suite = load_selected_tests(args.tests)
    runner = LoggerTestRunner(logger, verbosity=2)
    try:
        result = runner.run(suite)
    except KeyboardInterrupt:
        logger.warning('Test run interrupted by KeyboardInterrupt')
        exit()

    # Summary
    logger.info(f"Tests run: {result.testsRun}")
    logger.info(f"Failures: {len(result.failures)}")
    logger.info(f"Errors: {len(result.errors)}")