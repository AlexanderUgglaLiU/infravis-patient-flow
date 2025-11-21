import pandas as pd

import icd
data = pd.read_csv("data/dataset/diagnos_events.csv")

icd_reader = icd.ICD_SE()

explanations:list[str] = []

j = 0
for i, row in data.iterrows():
    explanations.append(icd_reader.get_title(str(row["event_value"])))
    j+= 1
    if j%100 == 0:
        print(j)
data["event_info"] = explanations

data.to_csv("data/dataset/diagnos_events_2.csv", index=False)