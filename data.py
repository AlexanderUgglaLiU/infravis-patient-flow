import pandas as pd
from timeline import Event, EventTimeline, EventTimelineAggregate
from time_utils import str2datetime
import math


def create_aggregate(
    data_paths: list[str],
    pick_from_csv: str,
    patient_attributes_csv: str,
    num_patients: int,
):

    # Extract which seq-ids to use
    pick_from_df = pd.read_csv(pick_from_csv).head(num_patients)

    # Get attributes of all patients
    patient_attributes_df: pd.DataFrame = pd.read_csv(patient_attributes_csv)

    # Filter to all rows with the given sequence ids
    patient_attributes_df = patient_attributes_df.loc[
        patient_attributes_df["seqID"].isin(pick_from_df["seqID"])
    ]

    tl_dict = load_event_timelines(data_paths, patient_attributes_df)
    agg = EventTimelineAggregate()
    for key in tl_dict.keys():
        # Ignore all timelines that don't start with arrival
        if tl_dict[key].events[0].event_type != Event.Type.ARRIVAL:
            continue
        agg.add_event_timeline(tl_dict[key])
    return agg


def read_csv(csv_path: str, seq_ids: pd.Series) -> pd.DataFrame:
    data = pd.read_csv(csv_path)
    subset = data.loc[data["seqID"].isin(seq_ids)]
    return subset


def load_event_timelines(
    data_paths: list[str], sequence_info: pd.DataFrame
) -> dict[int, EventTimeline]:

    # Initialize timelines
    timelines: dict[int, EventTimeline] = {}
    for _i, row in sequence_info.iterrows():
        tl: EventTimeline = EventTimeline(
            row["seqID"], str2datetime(row["ankomst_tidpunkt"])
        )
        timelines[int(row["seqID"])] = tl

    # Read each csv
    for path in data_paths:
        dataset = read_csv(path, sequence_info["seqID"])
        has_info = "event_info" in dataset.columns

        dataset = dataset.reindex()
        for _i, row in dataset.iterrows():
            t = row["time"]
            if not (type(t) is str) and math.isnan(t):
                t = "2000-01-01 00:00:00"
            if has_info:
                timelines[int(row["seqID"])].add_event(
                    Event(str2datetime(t), row["event_type"], str(row["event_value"]), str(row["event_info"]))
                )
            else:
                timelines[int(row["seqID"])].add_event(
                    Event(str2datetime(t), row["event_type"], str(row["event_value"]))
                )
    for id in timelines.keys():
        timelines[id].sort()
    return timelines

class AggregateDict():
    data_discrete:dict
    data_continuous:dict
    def __init__(self) -> None:
        self.data_discrete = {}
        self.data_continuous = {}
    
    def add_discrete(self, title:str, value:str) -> None:
        if not title in self.data_discrete.keys():
            self.data_discrete[title] = {}

        if value in self.data_discrete[title].keys():
            self.data_discrete[title][value] += 1
        else:
            self.data_discrete[title][value] = 1

    def add_continuous(self, title:str, value) -> None:
        if not title in self.data_continuous.keys():
            self.data_continuous[title] = [value]
        else:
            self.data_continuous[title].append(value)

    def __str__(self) -> str:
        agg_str = ""
        for key in self.data_discrete.keys():
            agg_str += f"[{key}]\n"
            for value_key in sorted(self.data_discrete[key].keys()):
                agg_str += (
                    f"{value_key}: {self.data_discrete[key][value_key]}, "
                )
            agg_str += "\n\n"
        for key in self.data_continuous.keys():
            agg_str += f"[{key}]\n" + str(sorted(self.data_continuous[key])) + "\n"
        return agg_str

def get_patient_attribute_aggregate(pa_path:str, seq_ids:list[int]):
    # Get attributes of all patients
    patient_attributes_df: pd.DataFrame = pd.read_csv(pa_path)

    # Filter to all rows with the given sequence ids
    patient_attributes_df = patient_attributes_df.loc[
        patient_attributes_df["seqID"].isin(seq_ids)
    ]

    agg = AggregateDict()
    for _i, row in patient_attributes_df.drop_duplicates(subset="seqID").iterrows():
        agg.add_discrete("Gender", str(row["kon"]))
        agg.add_discrete("Arrival", str(row["akutankomstsatt_namn"]))
        agg.add_discrete("Priority", str(row["prioritet_akut_kod"]))
        agg.add_discrete("Visit reason", str(row["besokorsak_forsta"]))
        agg.add_continuous("Age", row["alder"])

    return agg

