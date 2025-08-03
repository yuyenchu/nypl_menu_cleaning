import argparse
import glob
import logging
import numpy as np
import os
import pandas as pd
# import pytest
import time
import unittest
from tqdm import tqdm

from tests import (
    ENGINE, 
    RED,
    GREEN, 
    RESET,
    TABLE_MAP,
    TEST_GROUPS,
    LoggerTestRunner, 
    ConditionalFormatter,
)

def get_logger(fn='test.log'):
    console_handler = logging.StreamHandler()
    console_formatter = ConditionalFormatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    file_handler = logging.FileHandler(fn)
    file_formatter = ConditionalFormatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logging.basicConfig(level=logging.DEBUG, handlers=[console_handler, file_handler])

    logger = logging.getLogger(__name__)
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
        '-o', '--outdir',
        help='path to the output directory',
        type=str,
        default='.', 
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
        help=f'Specify which test groups to run, options: {['all']+list(TEST_GROUPS.keys())}',
        default=[],
    )
    return parser

def load_selected_tests(selected_groups, output_dir='.', logger=None):
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    if ('all' in selected_groups):  # load all
        selected_groups = TEST_GROUPS.keys()

    for group in selected_groups:
        test_classes = TEST_GROUPS.get(group, [])
        for test_class in test_classes:
            if logger:
                logger.debug(f'Loading tests from: {test_class.__name__}')
            # suite.addTest(test_class())
            test_class.output_dir = output_dir
            suite.addTest(loader.loadTestsFromTestCase(test_class))

    return suite

def load_pytest_args(selected_groups, logger=None):
    if ('all' in selected_groups):  # load all
        return list(TEST_GROUPS.values())

    args = []
    for group in selected_groups:
        test_fn = TEST_GROUPS.get(group, [])
        if logger:
            logger.debug(f'Loading tests from: {test_fn}')
        args += test_fn
    return args

def insert_data(f, engine, output_dir='.', logger=None):
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
            np.save(os.path.join(output_dir, f'{table_name}_failed.npy'), np.array(failed_rows))
            exit()
        except Exception as e:
            logger.error(f'Failed to insert row {idx} - Error: {e}')
            failed_rows.append(idx)

    if failed_rows:
        logger.info(f'\n Summary of {len(failed_rows)} failed rows for table "{table_name}":')
        logger.info(df.iloc[failed_rows])
    return df, failed_rows

if __name__ == "__main__":
    args = get_parser().parse_args()
    print('Configs =', args)

    # make output folder
    os.makedirs(args.outdir, exist_ok=True)
    assert os.path.isdir(args.outdir), f'output path does not exist or is not directory: {args.outdir}'
    logger = get_logger(os.path.join(args.outdir, 'test.log'))

    # table create/drop/insert logic
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
                insert_data(f, ENGINE, args.outdir, logger)
    
    if (len(args.tests)>0):
        # loading testcases
        suite = load_selected_tests(args.tests, args.outdir)
        runner = LoggerTestRunner(logger, verbosity=2)
        logger.info('        Starting Test')
        logger.info('='*60, extra={'simple': True})
        startTime = time.perf_counter()
        # pytest_args = ['-v', '-s'] + load_pytest_args(args.tests)
        try:
            result = runner.run(suite)
            # result = pytest.main(pytest_args)
        except KeyboardInterrupt:
            logger.warning('Test run interrupted by KeyboardInterrupt')
            exit()
        stopTime = time.perf_counter()
        timeTaken = stopTime - startTime
        success_count, fail_count, error_count = len(result.success), len(result.failures), len(result.errors)
        # print summary
        logger.info('        Final Result')
        logger.info('='*70, extra={'simple': True})
        logger.info(f'Tests run: {result.testsRun}')
        logger.info(f'Success: {GREEN}{success_count}{RESET}')
        logger.info(f'Failure: {RED}{fail_count}{RESET}')
        logger.info(f'Errors: {RED}{error_count}{RESET}')
        logger.info(f'Pass Rate: {(success_count/result.testsRun*100):.2f}%')
        logger.info(f'Total Runtime: {timeTaken:.4f}s')
        logger.info('='*70, extra={'simple': True})
        logger.info('\n', extra={'simple': True})