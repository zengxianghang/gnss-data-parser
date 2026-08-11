"""Parser for the NovAtel OEM7 BESTPOS ASCII log.

Reference:
https://docs.novatel.com/OEM7/Content/Logs/BESTPOS.htm
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from gnss_parser.common.io import TextSource, iter_text_lines

from .ascii import NovatelAsciiHeader, NovatelAsciiParseError, parse_ascii_line, peek_ascii_message_name

_MESSAGE = "BESTPOSA"


@dataclass(frozen=True, slots=True)
class BestposRecord:
    header: NovatelAsciiHeader
    sol_status: str
    pos_type: str
    latitude_deg: float
    longitude_deg: float
    msl_height_m: float
    undulation_m: float
    datum: str
    lat_std_m: float
    lon_std_m: float
    hgt_std_m: float
    station_id: str
    diff_age_s: float
    sol_age_s: float
    tracked_sv: int
    used_sv: int
    used_l1_sv: int
    used_multi_sv: int
    reserved: int
    ext_sol_status: int
    gal_bds_signal_mask: int
    gps_glo_signal_mask: int
    crc: int

    @property
    def week(self) -> int:
        return self.header.week

    @property
    def sow(self) -> float:
        return self.header.sow

    @property
    def time_status(self) -> str:
        return self.header.time_status


def parse_bestpos_line(line: str, *, verify_crc: bool = False, line_number: int | None = None) -> BestposRecord:
    message = parse_ascii_line(
        line,
        expected_message=_MESSAGE,
        verify_crc=verify_crc,
        line_number=line_number,
    )
    if len(message.fields) != 21:
        raise NovatelAsciiParseError(
            f"BESTPOSA requires 21 body fields, got {len(message.fields)}",
            line_number=line_number,
        )
    f = message.fields
    try:
        return BestposRecord(
            header=message.header,
            sol_status=f[0],
            pos_type=f[1],
            latitude_deg=float(f[2]),
            longitude_deg=float(f[3]),
            msl_height_m=float(f[4]),
            undulation_m=float(f[5]),
            datum=f[6],
            lat_std_m=float(f[7]),
            lon_std_m=float(f[8]),
            hgt_std_m=float(f[9]),
            station_id=f[10],
            diff_age_s=float(f[11]),
            sol_age_s=float(f[12]),
            tracked_sv=int(f[13], 10),
            used_sv=int(f[14], 10),
            used_l1_sv=int(f[15], 10),
            used_multi_sv=int(f[16], 10),
            reserved=int(f[17], 16),
            ext_sol_status=int(f[18], 16),
            gal_bds_signal_mask=int(f[19], 16),
            gps_glo_signal_mask=int(f[20], 16),
            crc=message.crc,
        )
    except ValueError as exc:
        raise NovatelAsciiParseError(
            f"invalid BESTPOSA body value: {exc}", line_number=line_number
        ) from exc


def iter_bestpos(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> Iterator[BestposRecord]:
    for line_number, line in iter_text_lines(source, encoding=encoding, errors=errors):
        if peek_ascii_message_name(line) != _MESSAGE:
            continue
        try:
            yield parse_bestpos_line(line, verify_crc=verify_crc, line_number=line_number)
        except NovatelAsciiParseError:
            if strict:
                raise


def read_bestpos(
    source: TextSource,
    *,
    strict: bool = False,
    verify_crc: bool = False,
    encoding: str = "utf-8",
    errors: str = "replace",
) -> list[BestposRecord]:
    return list(iter_bestpos(source, strict=strict, verify_crc=verify_crc, encoding=encoding, errors=errors))
