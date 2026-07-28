#!/usr/bin/env python3
from __future__ import annotations

import csv
import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import quote_plus

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PDF_PATH = DATA_DIR / "paedsengage-clinics.pdf"
TEXT_PATH = DATA_DIR / "paedsengage-clinics.txt"
OUTPUT_JSON = DATA_DIR / "clinics.json"
OUTPUT_CLINICS_CSV = DATA_DIR / "clinics.csv"
OUTPUT_HOURS_CSV = DATA_DIR / "clinic_hours.csv"
OUTPUT_BLOCKS_CSV = DATA_DIR / "clinic_hours_blocks.csv"
SITE_DATA_DIR: Path | None = None

DAY_ORDER = ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun", "PH"]
DAY_INDEX = {day: i for i, day in enumerate(DAY_ORDER)}
DAY_ALIASES = {
    "Mon": "Mon",
    "Monday": "Mon",
    "Tues": "Tues",
    "Tue": "Tues",
    "Tuesday": "Tues",
    "Wed": "Wed",
    "Wednesday": "Wed",
    "Thurs": "Thurs",
    "Thu": "Thurs",
    "Thursday": "Thurs",
    "Fri": "Fri",
    "Friday": "Fri",
    "Sat": "Sat",
    "Saturday": "Sat",
    "Sun": "Sun",
    "Sunday": "Sun",
    "PH": "PH",
    "Public Holiday": "PH",
}
TITLE_RE = re.compile(r"^(Dr|A/Prof|Prof|Assoc Prof|Associate Prof)\b", re.I)
PHONE_RE = re.compile(r"\b\d{8}\b")
TOC_RE = re.compile(r"^\s*([A-Za-z][A-Za-z\-\s]+?)\s*\.{3,}\s+\d+\s*$")
HOURS_START_RE = re.compile(r"^(Mon|Tues|Tue|Wed|Thurs|Thu|Fri|Sat|Sun|PH|Closed)\b", re.I)
TIME_BLOCK_RE = re.compile(r"(\d{1,2}:\d{2}\s*[ap]m)\s*[–-]\s*(\d{1,2}:\d{2}\s*[ap]m)", re.I)
CLOSED_RE = re.compile(r"Closed on\s+(.+)$", re.I)

DOCTOR_X = 134.7
CLINIC_X = 228.5
ADDRESS_X = 348.8
CONTACT_X = 412.4
LINE_TOLERANCE = 2.2
TOP_CROP = 120
BOTTOM_CROP = 760


@dataclass
class RawLine:
    doctor: str = ""
    clinic: str = ""
    address: str = ""
    contact: str = ""
    hours: str = ""


@dataclass
class ClinicRecord:
    location: str
    lines: list[RawLine] = field(default_factory=list)

    def finalize(self) -> dict:
        doctors = build_doctors(self.lines)
        clinic_name = clean_join((line.clinic for line in self.lines), separator=" ")
        address = clean_join(line.address for line in self.lines)
        contact_parts = [clean_spaces(line.contact) for line in self.lines if clean_spaces(line.contact)]

        contacts: list[str] = []
        contact_notes: list[str] = []
        seen_contacts = set()
        for part in contact_parts:
            phones = PHONE_RE.findall(part)
            for phone in phones:
                if phone not in seen_contacts:
                    contacts.append(phone)
                    seen_contacts.add(phone)
            remainder = clean_spaces(PHONE_RE.sub("", part).strip("() "))
            if remainder:
                contact_notes.append(remainder)

        operating_lines = normalize_operating_lines(self.lines)
        schedule = parse_operating_lines(operating_lines)
        maps_query = quote_plus(f"{clinic_name}, {address}") if clinic_name or address else ""

        return {
            "location": self.location,
            "clinic_name": clinic_name,
            "doctors": doctors,
            "address": address,
            "contacts": contacts,
            "contact_primary": contacts[0] if contacts else "",
            "contact_notes": unique(contact_notes),
            "google_maps_url": f"https://www.google.com/maps/search/?api=1&query={maps_query}" if maps_query else "",
            "operating_hours_text": operating_lines,
            "schedule": schedule,
        }


def clean_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("–", "-").replace(" ", " ")).strip(" -")


def clean_join(parts: Iterable[str], separator: str = ", ") -> str:
    cleaned = [clean_spaces(p) for p in parts if clean_spaces(p)]
    return separator.join(cleaned)


def extract_locations(pdf: pdfplumber.PDF) -> list[str]:
    if shutil.which("pdftotext"):
        text = subprocess.check_output(["pdftotext", "-layout", str(PDF_PATH), "-"], text=True)
    else:
        text = "\n".join((page.extract_text(layout=True) or "") for page in pdf.pages[:4])
    locations: list[str] = []
    for line in text.splitlines()[:140]:
        m = TOC_RE.match(line)
        if m:
            locations.append(clean_spaces(m.group(1)))
    return unique(locations)


def page_lines(page: pdfplumber.page.Page) -> list[dict]:
    words = page.extract_words(use_text_flow=True)
    if not words:
        return []

    lines: list[list[dict]] = []
    current: list[dict] = []
    current_top: float | None = None

    for word in sorted(words, key=lambda w: (round(w["top"], 1), w["x0"])):
        if current_top is None or abs(word["top"] - current_top) <= LINE_TOLERANCE:
            current.append(word)
            current_top = word["top"] if current_top is None else current_top
        else:
            lines.append(current)
            current = [word]
            current_top = word["top"]
    if current:
        lines.append(current)

    output = []
    for line in lines:
        parts = {"doctor": [], "clinic": [], "address": [], "contact": [], "hours": []}
        kept_words = []
        for word in line:
            if word["top"] < TOP_CROP or word["top"] > BOTTOM_CROP:
                continue
            kept_words.append(word)
            midpoint = (word["x0"] + word["x1"]) / 2
            if midpoint < DOCTOR_X:
                bucket = "doctor"
            elif midpoint < CLINIC_X:
                bucket = "clinic"
            elif midpoint < ADDRESS_X:
                bucket = "address"
            elif midpoint < CONTACT_X:
                bucket = "contact"
            else:
                bucket = "hours"
            parts[bucket].append(word["text"])
        row = {key: clean_spaces(" ".join(value)) for key, value in parts.items()}
        if any(row.values()):
            row["_top"] = min(word["top"] for word in kept_words)
            output.append(row)
    return output


def build_records(pdf: pdfplumber.PDF, locations: list[str]) -> list[dict]:
    location_set = set(locations)
    records: list[ClinicRecord] = []
    current_location = ""
    current: ClinicRecord | None = None

    for page in pdf.pages[2:]:
        for row in page_lines(page):
            plain_line = clean_spaces(" ".join(v for k, v in row.items() if k != "_top" and v))
            if not plain_line:
                continue
            if (
                plain_line.startswith("Participating PaedsENGAGE Clinics")
                or plain_line.startswith("IMPORTANT NOTE")
                or plain_line.startswith("[Accurate as of")
                or re.match(r"^Page \d+ of \d+$", plain_line)
            ):
                continue
            if plain_line in location_set and not row["clinic"] and not row["address"] and not row["contact"] and not row["hours"]:
                if current:
                    records.append(current)
                    current = None
                current_location = plain_line
                location_set.add(plain_line)
                continue
            if plain_line.startswith("GP Name") or plain_line == "Contact":
                continue
            if not current_location:
                continue

            normalized_row = {k: v for k, v in row.items() if k in {"doctor", "clinic", "address", "contact", "hours"}}
            if normalized_row["contact"] and not PHONE_RE.search(normalized_row["contact"]):
                normalized_row["hours"] = clean_spaces(f"{normalized_row['contact']} {normalized_row['hours']}")
                normalized_row["contact"] = ""
            parsed = RawLine(**normalized_row)
            is_new_record = bool(parsed.doctor and TITLE_RE.match(parsed.doctor) and PHONE_RE.search(parsed.contact))
            if is_new_record:
                if current:
                    records.append(current)
                current = ClinicRecord(location=current_location, lines=[parsed])
            elif current:
                current.lines.append(parsed)

    if current:
        records.append(current)

    finalized = []
    for record in records:
        clinic = record.finalize()
        if clinic["clinic_name"] and clinic["address"]:
            finalized.append(clinic)
    return finalized


def build_doctors(lines: list[RawLine]) -> list[str]:
    doctors: list[str] = []
    pending_name: str | None = None
    for line in lines:
        text = clean_spaces(line.doctor)
        if not text:
            continue
        if TITLE_RE.match(text):
            if pending_name:
                doctors.append(pending_name)
            pending_name = text
            if not line.clinic and not line.address and not line.contact and not line.hours:
                continue
        elif pending_name and not line.contact and not line.hours and not line.clinic:
            pending_name = clean_spaces(f"{pending_name} {text}")
            continue
        elif doctors:
            doctors[-1] = clean_spaces(f"{doctors[-1]} {text}")
            continue
        else:
            pending_name = text if pending_name is None else clean_spaces(f"{pending_name} {text}")
    if pending_name:
        doctors.append(pending_name)
    return unique(doctors)


def normalize_operating_lines(lines: list[RawLine]) -> list[str]:
    merged: list[str] = []
    for line in lines:
        text = line.hours
        if not text:
            continue
        if HOURS_START_RE.match(text):
            merged.append(text)
        elif merged:
            merged[-1] = clean_spaces(f"{merged[-1]} {text}")
        else:
            merged.append(text)
    return merged


def normalize_day_token(token: str) -> str:
    return DAY_ALIASES.get(clean_spaces(token).rstrip(":"), clean_spaces(token).rstrip(":"))


def expand_days(label: str) -> list[str]:
    label = clean_spaces(label.replace(" and ", " & "))
    if label in {"Daily", "Mon - Sun", "Mon-Sun"}:
        return ["Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun"]
    if "-" in label:
        left, right = [normalize_day_token(x) for x in re.split(r"\s*-\s*", label, maxsplit=1)]
        if left in DAY_INDEX and right in DAY_INDEX and DAY_INDEX[left] <= DAY_INDEX[right]:
            return DAY_ORDER[DAY_INDEX[left] : DAY_INDEX[right] + 1]
    pieces = [normalize_day_token(x) for x in re.split(r"\s*,\s*|\s*&\s*", label) if x.strip()]
    return [piece for piece in pieces if piece in DAY_INDEX]


def parse_time(text: str) -> tuple[str, int]:
    cleaned = clean_spaces(text).lower().replace(" ", "")
    if cleaned == "12:00am":
        return "00:00", 0
    dt = datetime.strptime(cleaned, "%I:%M%p")
    return dt.strftime("%H:%M"), dt.hour * 60 + dt.minute


def parse_operating_lines(lines: list[str]) -> dict:
    per_day: dict[str, dict] = defaultdict(lambda: {"time_blocks": [], "notes": []})
    general_notes: list[str] = []

    for raw_line in lines:
        line = normalize_hours_text(raw_line)
        if not line:
            continue
        closed_match = CLOSED_RE.match(line)
        if closed_match:
            day_text = closed_match.group(1).replace("Sun & PH", "Sun, PH").replace("Sat & PH", "Sat, PH")
            for day in expand_days(day_text):
                per_day[day]["notes"].append("Closed")
            continue

        label = value = None
        if ":" in line:
            left, right = [part.strip() for part in line.split(":", 1)]
            if not re.search(r"\d", left) and expand_days(left.replace("*", "")):
                label, value = left, right
        if label is None:
            time_match = re.search(r"\d{1,2}:\d{2}\s*[ap]m", line, re.I)
            if time_match:
                candidate_label = clean_spaces(line[: time_match.start()].strip(" :"))
                candidate_value = clean_spaces(line[time_match.start() :])
                if expand_days(candidate_label.replace("*", "")):
                    label, value = candidate_label, candidate_value

        if label is None:
            general_notes.append(line)
            continue

        days = expand_days(label.replace("*", ""))
        if not days:
            general_notes.append(line)
            continue
        blocks = TIME_BLOCK_RE.findall(value)
        note = clean_spaces(TIME_BLOCK_RE.sub("", value).strip(" ;,"))
        for day in days:
            for start_raw, end_raw in blocks:
                start_24, start_mins = parse_time(start_raw)
                end_24, end_mins = parse_time(end_raw)
                per_day[day]["time_blocks"].append(
                    {
                        "start": start_24,
                        "end": end_24,
                        "start_minutes": start_mins,
                        "end_minutes": end_mins,
                        "overnight": end_mins <= start_mins,
                        "display": f"{clean_spaces(start_raw)} - {clean_spaces(end_raw)}",
                    }
                )
            if note:
                per_day[day]["notes"].append(note)

    ordered_days = []
    for day in DAY_ORDER:
        if day in per_day:
            entry = per_day[day]
            ordered_days.append(
                {
                    "day": day,
                    "time_blocks": entry["time_blocks"],
                    "notes": unique(entry["notes"]),
                    "is_closed": not entry["time_blocks"] and any(clean_spaces(n).lower() == "closed" for n in entry["notes"]),
                }
            )
    return {"days": ordered_days, "general_notes": unique(general_notes)}


def normalize_hours_text(text: str) -> str:
    text = clean_spaces(text)
    text = re.sub(r"(?<=\d)\.(?=\d{2}\s*[ap]m)", ":", text, flags=re.I)
    text = re.sub(r"\bSat\s+(\d{1,2}:\d{2}\s*[ap]m)", r"Sat: \1", text, flags=re.I)
    return text


def unique(items: Iterable[str]) -> list[str]:
    output: list[str] = []
    seen = set()
    for item in items:
        cleaned = clean_spaces(item)
        if cleaned and cleaned not in seen:
            output.append(cleaned)
            seen.add(cleaned)
    return output


def write_text_dump(clinics: list[dict]) -> None:
    lines: list[str] = []
    for clinic in clinics:
        lines.append(f"[{clinic['location']}] {clinic['clinic_name']}")
        lines.append(f"  Address: {clinic['address']}")
        lines.append(f"  Contact: {' / '.join(clinic['contacts']) or '-'}")
        for hours in clinic["operating_hours_text"]:
            lines.append(f"  Hours: {hours}")
        lines.append("")
    TEXT_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(clinics: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(clinics, indent=2, ensure_ascii=False), encoding="utf-8")
    write_text_dump(clinics)

    with OUTPUT_CLINICS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "location",
                "clinic_name",
                "doctors",
                "address",
                "contact_primary",
                "contacts",
                "contact_notes",
                "google_maps_url",
                "operating_hours_text",
                "general_notes",
            ],
        )
        writer.writeheader()
        for clinic in clinics:
            writer.writerow(
                {
                    "location": clinic["location"],
                    "clinic_name": clinic["clinic_name"],
                    "doctors": " | ".join(clinic["doctors"]),
                    "address": clinic["address"],
                    "contact_primary": clinic["contact_primary"],
                    "contacts": " | ".join(clinic["contacts"]),
                    "contact_notes": " | ".join(clinic["contact_notes"]),
                    "google_maps_url": clinic["google_maps_url"],
                    "operating_hours_text": " | ".join(clinic["operating_hours_text"]),
                    "general_notes": " | ".join(clinic["schedule"]["general_notes"]),
                }
            )

    with OUTPUT_HOURS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["location", "clinic_name", "day", "time_blocks", "notes", "is_closed"])
        writer.writeheader()
        for clinic in clinics:
            for day in clinic["schedule"]["days"]:
                writer.writerow(
                    {
                        "location": clinic["location"],
                        "clinic_name": clinic["clinic_name"],
                        "day": day["day"],
                        "time_blocks": " | ".join(block["display"] for block in day["time_blocks"]),
                        "notes": " | ".join(day["notes"]),
                        "is_closed": str(day["is_closed"]).lower(),
                    }
                )

    with OUTPUT_BLOCKS_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["location", "clinic_name", "day", "start", "end", "start_minutes", "end_minutes", "overnight", "display"],
        )
        writer.writeheader()
        for clinic in clinics:
            for day in clinic["schedule"]["days"]:
                for block in day["time_blocks"]:
                    writer.writerow({"location": clinic["location"], "clinic_name": clinic["clinic_name"], "day": day["day"], **block})

    if SITE_DATA_DIR:
        SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        (SITE_DATA_DIR / "clinics.json").write_text(json.dumps(clinics, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    global DATA_DIR, PDF_PATH, TEXT_PATH, OUTPUT_JSON, OUTPUT_CLINICS_CSV, OUTPUT_HOURS_CSV, OUTPUT_BLOCKS_CSV, SITE_DATA_DIR

    parser = argparse.ArgumentParser(description="Parse the PaedsENGAGE clinic PDF into JSON and CSV tables.")
    parser.add_argument("--pdf", type=Path, default=PDF_PATH, help="Path to the PaedsENGAGE PDF.")
    parser.add_argument("--out-dir", type=Path, default=DATA_DIR, help="Directory for clinics.json/csv outputs.")
    parser.add_argument("--site-data-dir", type=Path, default=None, help="Optional site/data directory to receive clinics.json.")
    args = parser.parse_args()

    DATA_DIR = args.out_dir.resolve()
    PDF_PATH = args.pdf.resolve()
    TEXT_PATH = DATA_DIR / f"{PDF_PATH.stem}.txt"
    OUTPUT_JSON = DATA_DIR / "clinics.json"
    OUTPUT_CLINICS_CSV = DATA_DIR / "clinics.csv"
    OUTPUT_HOURS_CSV = DATA_DIR / "clinic_hours.csv"
    OUTPUT_BLOCKS_CSV = DATA_DIR / "clinic_hours_blocks.csv"
    SITE_DATA_DIR = args.site_data_dir.resolve() if args.site_data_dir else None

    if not PDF_PATH.exists():
        print(f"Missing PDF: {PDF_PATH}", file=sys.stderr)
        return 1

    with pdfplumber.open(PDF_PATH) as pdf:
        locations = extract_locations(pdf)
        clinics = build_records(pdf, locations)

    write_outputs(clinics)
    print(f"Parsed {len(clinics)} clinics across {len(locations)} locations with pdfplumber.")
    print(f"JSON:  {OUTPUT_JSON}")
    print(f"CSV:   {OUTPUT_CLINICS_CSV}")
    print(f"Hours: {OUTPUT_HOURS_CSV}")
    print(f"Slots: {OUTPUT_BLOCKS_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
