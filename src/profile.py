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


def check_logic_issues(df, filename):
    logic_issues = {}

    # Check if certain price-related columns have zero values
    if "lowest_price" in df.columns:
        logic_issues["lowest_price_is_zero"] = (df["lowest_price"] == 0).sum()
    if "highest_price" in df.columns:
        logic_issues["highest_price_is_zero"] = (df["highest_price"] == 0).sum()
    if "price" in df.columns:
        logic_issues["price_is_zero"] = (df["price"] == 0).sum()

    # Check for duplicate IDs
    if "id" in df.columns:
        logic_issues["duplicated_id"] = df["id"].duplicated().sum()

    return logic_issues


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

        print("Logic-based issues (e.g., 0 prices or duplicated IDs):")
        logic = check_logic_issues(df, f)
        for k, v in logic.items():
            print(f"{k}: {v}")

        print("-" * 50)

        # Write all profiling results to a report file
        with open("profiling_report.txt", "a") as f_out:
            f_out.write(f"\nFile: {f}\n")
            f_out.write("Missing values:\n")
            f_out.write(str(missing) + "\n")
            f_out.write("Logic-based issues:\n")
            for k, v in logic.items():
                f_out.write(f"{k}: {v}\n")
            f_out.write("-" * 50 + "\n")
