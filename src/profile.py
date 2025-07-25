import argparse
import glob
import os
import pandas as pd


def get_parser():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="options for profiling")
    parser.add_argument(
        "-p",
        "--path",
        help="path to the dataset folder",
        type=str,
        default="../data/NYPL-menus",  # Default dataset path
    )
    return parser


def count_missing_values(df):
    # Count the number of missing values per column
    return df.isnull().sum()


def detect_outliers_iqr(df):
    # Detect outliers in numeric columns using the IQR method
    outlier_info = {}
    for col in df.select_dtypes(include="number").columns:
        Q1 = df[col].quantile(0.25)  # First quartile
        Q3 = df[col].quantile(0.75)  # Third quartile
        IQR = Q3 - Q1  # Interquartile range
        lower = Q1 - 1.5 * IQR  # Lower bound for outliers
        upper = Q3 + 1.5 * IQR  # Upper bound for outliers
        outliers = df[(df[col] < lower) | (df[col] > upper)]
        outlier_info[col] = len(outliers)
    return outlier_info


if __name__ == "__main__":
    args = get_parser().parse_args()
    print("configs =", args)

    for f in glob.glob(os.path.join(args.path, "*.csv")):
        print(f"\nFound file {f}, printing head:")
        df = pd.read_csv(f)
        print(df.head(), "\n")

        print("Missing values per column:")
        missing = count_missing_values(df)
        print(missing, "\n")

        print("Outliers:")
        outlier_counts = detect_outliers_iqr(df)
        for col, count in outlier_counts.items():
            print(f"{col}: {count} outliers")

        print("-" * 50)

        # Write all profiling results to a report file
        with open("profiling_report.txt", "a") as f_out:
            f_out.write(f"\nFile: {f}\n")
            f_out.write("Missing values:\n")
            f_out.write(str(missing) + "\n")
            f_out.write("Outliers:\n")
            for col, count in outlier_counts.items():
                f_out.write(f"{col}: {count} outliers\n")
            f_out.write("-" * 50 + "\n")
