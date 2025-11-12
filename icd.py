import pandas as pd
import os

path = "icd-10-se.tsv"


class ICD_SE:
    data_frame: pd.DataFrame

    def __init__(self) -> None:
        self.data_frame = pd.read_csv(
            os.path.join(path), delimiter="\t", low_memory=False
        )

    def get_title(self, code: str) -> str:
        if len(code) == 4:
            code = code[:3] + "." + code[-1]

        search = self.data_frame.loc[self.data_frame["Kod"] == code]
        for _i, row in search.iterrows():
            return row["Titel"]
        return "Unknown diagnosis"

def get_title(code:str) -> str:
    icd_se = ICD_SE()
    return icd_se.get_title("N30.1")


if __name__ == "__main__":
    icd_se = ICD_SE()
    print(icd_se.get_title("N30.1"))
