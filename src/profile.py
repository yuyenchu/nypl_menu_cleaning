import argparse
import glob
import os
import pandas as pd

def get_parser():
    parser = argparse.ArgumentParser(description='options for training')
    parser.add_argument('-p', '--path',  help='path to the dataset folder', type=str, default='../data/NYPL-menus')
    return parser

if __name__=='__main__':
    args = get_parser().parse_args()  
    print('configs =',args)
    for f in glob.glob(os.path.join(args.path, '*.csv')):
        print(f'found file {f}, printing head')
        df = pd.read_csv(f)
        print(df.head(), '\n')