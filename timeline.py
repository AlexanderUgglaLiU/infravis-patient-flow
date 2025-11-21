from datetime import datetime
from enum import Enum

import json

from icd import ICD_SE

class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


# Data structs
class Attributes:
    # Enums
    class Gender(Enum):
        OTHER = -1
        MAN = 0
        WOMAN = 1

    class WayOfArrival(Enum):
        OTHER = -1
        WALKING = 0
        AMBULANCE = 1

    patient_key: int
    vardhandelse_key: int
    gender: Gender
    way_of_arrival: WayOfArrival
    priority: int
    visit_reason: str
    age: int
    care_form: str
    vitals: dict


class Event:
    time: datetime
    title: str
    value: str
    descriptive: str
    color: str

    class Type(Enum):
        OTHER = -1
        ARRIVAL = 0
        EXIT = 1
        DIAGNOSIS = 2
        NURSE = 3
        DOCTOR = 4
        XRAY = 5
        LAB_ORDER = 6
        LAB_RESULTS = 7
        SURGERY = 8
        MEDICATION = 9

    event_type: Type
    key: str
    info : str
    
    def __init__(self, time: datetime, title: str, value: str, info:str = "") -> None:
        self.time: datetime = time
        self.title: str = title
        self.value: str = value
        self.info: str = info
        match title:
            case "ankomst":
                self.event_type = self.Type.ARRIVAL
                self.key = "Arrival"
                self.color = "#8dd3c7"
            case "ut_till_namn":
                self.event_type = self.Type.EXIT
                self.key = "Sent:\n" + value
                self.color = "#fdb462"
            case "Bidiagnos":
                self.event_type = self.Type.DIAGNOSIS
                self.key = "BD:\n" + value
                self.color = "#80b1d3"
                # timeline_str.append(self.icd_se.get_title(event.value))
            case "Huvuddiagnos":
                self.event_type = self.Type.DIAGNOSIS
                self.key = "MD:\n" + value
                self.color = "#80b1d3"
                # timeline_str.append(self.icd_se.get_title(event.value))
            case "skoterske_tidpunkt":
                self.event_type = self.Type.NURSE
                self.key = "Nurse"
                self.color = "#ffffb3"
            case "forsta_ansvariga_lakare":
                self.event_type = self.Type.DOCTOR
                self.key = "Doctor"
                self.color = "#bebada"
            case "rontgen":
                self.event_type = self.Type.XRAY
                self.key = "XR:\n" + value
                self.color = "#5fb86e"
            case "lakemedel":
                self.event_type = self.Type.MEDICATION
                code, description, count = Event.parse_meds(value)
                self.key = "Meds:\n" + code  # More info needed? pill vs drink
                self.info = description
                self.color = "#ff00ff"
            case "operation":
                self.event_type = self.Type.SURGERY
                self.key = "Surgery:\n" + value
                self.color = "#a57620"
            case "lab_svar":
                self.event_type = self.Type.LAB_RESULTS
                self.key = "Lab results"
                self.color = "#A6D3E2"
                self.info = Event.parse_test_results(value)
            case "lab_bestallning":
                self.event_type = self.Type.LAB_ORDER
                self.key = "Lab order"
                self.color = "#93B5C0"
                self.info = Event.parse_test_order(value)
            case _:
                self.event_type = self.Type.OTHER
                self.key = "?\n" + title + value
                self.color = "#FFFFFF"

    def __str__(self) -> str:
        return str(self.time) + " " + self.title + " : " + self.value

    @staticmethod
    def parse_test_results(s: str) -> str:
        x = json.loads(s)
        out = ""

        current_discipline = ""
        for row in x:
            if row['disciplin_beskrivning'] != current_discipline:
                current_discipline = row['disciplin_beskrivning']
                out += "[" + row['disciplin_beskrivning'] + "]\n"
            out += f"{row['analys_namn']}: {row['varde']}\n"
        
        return out
    @staticmethod
    def parse_test_order(s: str) -> str:
        x = json.loads(s)
        out = ""

        for row in x:
            out += f"{row['analys_namn']}\n"
        
        return out


    @staticmethod
    def parse_meds(s: str) -> tuple[str, str, int]:
        # [{""atc_kod"" : ""J01DD14"", ""beredningsform"" : ""Granulat till oral suspension""}]"

        x = json.loads(s)

        code = ""
        description = ""
        count = len(x)

        if count != 0:
            code = x[0]["atc_kod"]
            description = x[0]["beredningsform"]

        return code, description, count


class EventTimeline:
    seq_id: int
    start_time: datetime
    events: list[Event]
    patient_attributes: Attributes  # TODO

    def __init__(self, id: int, start_time: datetime) -> None:
        self.seq_id = id
        self.start_time = start_time
        self.events = []

    def add_event(self, event: Event) -> None:
        if (
            len(self.events) > 0
            and event.event_type == self.events[-1].event_type
            and event.value == self.events[-1].value
        ):
            return
        self.events.append(event)

    def sort(self) -> None:
        self.events.sort(key=lambda x: x.time)

    def __str__(self) -> str:
        out = "SeqID " + str(self.seq_id)
        for e in self.events:
            out += "\n" + str(e)
        return out


class EventAggregate:
    key: str
    color: str
    events: dict[int, Event]

    stop_here: int
    size: int

    parent: "EventAggregate|None"
    children: dict[str, "EventAggregate"]

    def __init__(self, event_key: str, info:str) -> None:
        # Data
        self.key = event_key
        self.wait_times = []
        self.stop_here = 0
        self.size = 0
        self.events = {}
        self.color = "#000000"
        self.info = info

        # Node
        self.parent = None
        self.children = {}

    def add_event(self, seq_id: int, event: Event, last_event: bool):
        self.events[seq_id] = event
        self.size += 1
        self.color = event.color
        if last_event:
            self.stop_here += 1

    def get_or_create_child(self, key: str, info: str) -> "EventAggregate":
        if key in self.children.keys():
            return self.children[key]
        else:
            ea = EventAggregate(key, info)
            self.children[key] = ea
            ea.parent = self
            return ea

    def get_time_diffs(self, other: "EventAggregate") -> list[float]:
        diffs: list[float] = []
        for seq_id in self.get_common_seqids(other):
            diff = abs(self.events[seq_id].time - other.events[seq_id].time)
            diffs.append(diff.total_seconds() / 60.0)
        return diffs
    
    def get_common_seqids(self, other: "EventAggregate") -> list[int]:
        common: list[int] = []
        for seq_id in self.events.keys():
            if seq_id in other.events.keys():
                common.append(seq_id)
        return common

class EventTimelineAggregate:
    event_aggregate_root: EventAggregate

    def __init__(self) -> None:
        self.event_aggregate_root = EventAggregate("", "")

    def add_event_timeline(self, timeline: EventTimeline):
        current_node = self.event_aggregate_root
        last = timeline.events[-1]
        for event in timeline.events:
            child_ea: EventAggregate = current_node.get_or_create_child(event.key, event.info)
            child_ea.add_event(timeline.seq_id, event, event == last)
            current_node = child_ea
