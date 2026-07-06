from pathlib import Path
import pandas as pd


class DatasetLoader:

    def __init__(self):
        self.dataset_path = (
            Path(__file__).resolve().parents[2]
            / "datasets"
            / "BNPParibas_Data.csv"
        )

    def load_dataset(self):
        return pd.read_csv(self.dataset_path)


if __name__ == "__main__":
    loader = DatasetLoader()

    df = loader.load_dataset()

    print(df.head())
    print()
    print(df.info())
    print()
    print(df.shape)