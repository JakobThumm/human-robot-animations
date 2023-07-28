import os

import pandas as pd


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Data augmentation')
    parser.add_argument('file', nargs="+", type=str, help='CSV file(s) from which all nan frames should be erased')
    args = parser.parse_args()

    for f in args.file:
        assert f.endswith(".csv")
        assert os.path.exists(f)

        with open(f, "r") as fp:
            lines = fp.read().splitlines()
            header = "\n".join(lines[:5]) + "\n"

        df = pd.read_csv(f, header=4)

        clean_df = df.dropna()
        clean_df["Unnamed: 0"] = [i + 1 for i in range(len(clean_df))]  # Rename Frames

        with open(f, "w") as fp:
            fp.write(header)

        clean_df.to_csv(f, mode="a", header=False, index=False)
