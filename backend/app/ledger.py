# Loads the Datev Buchungsstapel CSV into memory at startup.
# The spec PDF says delimiter `;` and decimal comma, but the actual file is
# comma-delimited with decimal points. We parse what's actually there.
from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class Booking:
    amount: float
    soll_haben: str
    konto: str
    gegenkonto: str
    belegdatum: str
    belegfeld_1: str
    buchungstext: str
    kostenstelle: str

    def to_dict(self) -> dict:
        return asdict(self)


COST_CENTERS = {
    "1100": "Product & Engineering",
    "1200": "Operations & Logistics",
    "2000": "Sales",
    "3000": "Infrastructure",
    "4000": "Reisen & Repräsentation",
    "5000": "Facilities",
    "6000": "People & Talent",
    "7000": "Marketing & Events",
    "9000": "Legal, Finance & Compliance",
}


# Parse the Datev EXTF CSV into typed Booking records. Called once at app startup.
def load_ledger(csv_path: Path) -> list[Booking]:
    bookings: list[Booking] = []
    # utf-8-sig strips the BOM some Datev exports include at the start of the file.
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Row 1 = EXTF metadata, row 2 = headers, data from row 3 onwards.
    for row in rows[2:]:
        # Skip blank separator lines and the trailing empty row at end-of-file.
        if not row or not row[0].strip():
            continue
        try:
            # Column indices come from the Datev EXTF spec — see README / assignment PDF.
            bookings.append(
                Booking(
                    amount=float(row[0]),
                    soll_haben=row[1],
                    konto=row[6],
                    gegenkonto=row[7],
                    belegdatum=row[9],
                    belegfeld_1=row[10],
                    buchungstext=row[13],
                    kostenstelle=row[26] if len(row) > 26 else "",
                )
            )
        except (ValueError, IndexError):
            # Tolerate malformed / truncated rows rather than crashing startup.
            continue
    return bookings
