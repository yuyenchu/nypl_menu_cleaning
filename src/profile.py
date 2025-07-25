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
        default="../data/NYPL-menus",  # default folder if no path is given
    )
    return parser


def count_missing_values(df):
    # Count the number of missing (NaN) values in each column
    return df.isnull().sum()


def check_logical_issues(df):
    # Check for suspicious values based on schema understanding
    issues = {}

    # Check if certain price columns contain zero values, which may not be valid
    for col in ["lowest_price", "highest_price", "price"]:
        if col in df.columns:
            issues[f"{col}_is_zero"] = (df[col] == 0).sum()

    # Check for duplicate IDs which could indicate data duplication
    if "id" in df.columns:
        issues["duplicated_id"] = df["id"].duplicated().sum()

    return issues


if __name__ == "__main__":
    args = get_parser().parse_args()  # Get folder path from arguments
    print("configs =", args)

    for f in glob.glob(os.path.join(args.path, "*.csv")):
        print(f"Found file {f}, printing head:")
        df = pd.read_csv(f)
        print(df.head(), "\n")

        print("Missing values per column:")
        missing = count_missing_values(df)
        print(missing, "\n")

        print("Logic-based issues (e.g., 0 prices or duplicated IDs):")
        logic_issues = check_logical_issues(df)
        for k, v in logic_issues.items():
            print(f"{k}: {v}")

        print("-" * 50)

        # Save everything to a report file (append mode)
        with open("profiling_report.txt", "a") as f_out:
            f_out.write(f"\nFile: {f}\n")
            f_out.write("Missing values:\n")
            f_out.write(str(missing) + "\n")
            f_out.write("Logic-based issues:\n")
            for k, v in logic_issues.items():
                f_out.write(f"{k}: {v}\n")
            f_out.write("-" * 50 + "\n")
