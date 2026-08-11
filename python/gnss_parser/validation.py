"""Single-pass real-log validation output for Python/MATLAB comparison."""
from __future__ import annotations

import csv, json, math
from collections import deque
from pathlib import Path
from typing import Iterable

from .mixed import GnssLogEvent, GnssLogStats, iter_gnss_log, normalize_message_selection

SCHEMA_VERSION = 1
COMMON = ["message_type", "record_index", "source_line_number", "raw_line"]
FIELDS = {
    "psrvel": ["week","sow","time_status","sol_status","vel_type","latency_s","age_s","hor_speed_mps","track_deg","vert_speed_mps","reserved","crc"],
    "range": ["week","sow","time_status","observation_count","obs_index","prn","glofreq","pseudorange_m","pseudorange_std_m","adr_cycles","adr_std_cycles","doppler_hz","cn0_dbhz","lock_time_s","tracking_raw","tracking_state","sv_channel","phase_locked","parity_known","code_locked","correlator_type","satellite_system","satellite_system_name","grouped","signal_type","signal_name","primary_l1","half_cycle_added","digital_filter","prn_locked_out","forced_assignment","crc"],
    "inspva": ["week","sow","header_week","header_sow","time_status","latitude_deg","longitude_deg","ellipsoidal_height_m","vel_n_mps","vel_e_mps","vel_u_mps","roll_deg","pitch_deg","azimuth_deg","ins_status","crc"],
    "bestpos": ["week","sow","time_status","sol_status","pos_type","latitude_deg","longitude_deg","msl_height_m","undulation_m","datum","lat_std_m","lon_std_m","hgt_std_m","station_id","diff_age_s","sol_age_s","tracked_sv","used_sv","used_l1_sv","used_multi_sv","reserved","ext_sol_status","gal_bds_signal_mask","gps_glo_signal_mask","crc"],
    "bestvel": ["week","sow","time_status","sol_status","vel_type","latency_s","age_s","hor_speed_mps","track_deg","vert_speed_mps","reserved","crc"],
    "rmc": ["talker_id","utc_time","utc_seconds_of_day","status","latitude_deg","longitude_deg","speed_knots","course_deg","date_ddmmyy","magnetic_variation_deg","magnetic_variation_ew","position_mode","navigation_status","checksum"],
}
CSV_COLUMNS = {key: COMMON + value for key, value in FIELDS.items()}


def _fmt(value: object) -> str:
    if value is None: return ""
    if isinstance(value, bool): return "1" if value else "0"
    if isinstance(value, int): return str(value)
    if isinstance(value, float):
        if math.isnan(value): return ""
        return format(value, ".17g")
    return str(value)


def _base(event: GnssLogEvent, index: int) -> dict[str, str]:
    return {"message_type": event.message_type, "record_index": str(index),
            "source_line_number": str(event.line_number), "raw_line": event.raw_line or ""}


def flatten_event(event: GnssLogEvent, index: int) -> list[dict[str, str]]:
    """Flatten one parsed record to the shared validation CSV schema."""
    key, r, base = event.message_type, event.record, _base(event, index)
    if key != "range":
        values = {}
        for name in FIELDS[key]:
            if name == "header_week": value = r.header_week
            elif name == "header_sow": value = r.header_sow
            else: value = getattr(r, name)
            values[name] = _fmt(value)
        return [{**base, **values}]

    rows = []
    for obs_index, obs in enumerate(r.observations, 1):
        t = obs.tracking
        values = {
            "week": r.week, "sow": r.sow, "time_status": r.time_status,
            "observation_count": r.observation_count, "obs_index": obs_index,
            "prn": obs.prn, "glofreq": obs.glofreq, "pseudorange_m": obs.pseudorange_m,
            "pseudorange_std_m": obs.pseudorange_std_m, "adr_cycles": obs.adr_cycles,
            "adr_std_cycles": obs.adr_std_cycles, "doppler_hz": obs.doppler_hz,
            "cn0_dbhz": obs.cn0_dbhz, "lock_time_s": obs.lock_time_s,
            "tracking_raw": t.raw, "tracking_state": t.tracking_state, "sv_channel": t.sv_channel,
            "phase_locked": t.phase_locked, "parity_known": t.parity_known,
            "code_locked": t.code_locked, "correlator_type": t.correlator_type,
            "satellite_system": t.satellite_system, "satellite_system_name": t.satellite_system_name,
            "grouped": t.grouped, "signal_type": t.signal_type, "signal_name": t.signal_name,
            "primary_l1": t.primary_l1, "half_cycle_added": t.half_cycle_added,
            "digital_filter": t.digital_filter, "prn_locked_out": t.prn_locked_out,
            "forced_assignment": t.forced_assignment, "crc": r.crc,
        }
        rows.append({**base, **{name: _fmt(values[name]) for name in FIELDS[key]}})
    return rows


def _time(event: GnssLogEvent) -> dict[str, object]:
    r = event.record
    return ({"date_ddmmyy": r.date_ddmmyy, "utc_time": r.utc_time}
            if event.message_type == "rmc" else {"week": int(r.week), "sow": float(r.sow)})


class _Collector:
    def __init__(self, key: str, out: Path, first: int, last: int, every: int, full: bool):
        self.key, self.path, self.first, self.every, self.full = key, out/f"{key}.csv", max(0, first), max(0, every), full
        self.last = deque(maxlen=max(1, last)); self.last_count = max(0, last)
        self.fixed = {}; self.count = 0; self.rows = 0; self.first_time = None; self.last_time = None
        self.stream = self.writer = None
        if full:
            self.stream = self.path.open("w", encoding="utf-8", newline="")
            self.writer = csv.DictWriter(self.stream, fieldnames=CSV_COLUMNS[key]); self.writer.writeheader()

    def _write(self, rows):
        for row in rows: self.writer.writerow(row); self.rows += 1

    def add(self, event):
        self.count += 1; idx = self.count; marker = _time(event)
        if self.first_time is None: self.first_time = marker
        self.last_time = marker
        if self.full: self._write(flatten_event(event, idx)); return
        if idx <= self.first or (self.every and idx % self.every == 0): self.fixed[idx] = event
        if self.last_count: self.last.append((idx, event))

    def finish(self):
        if self.full: self.stream.close(); return
        entries = dict(self.fixed)
        for idx, event in self.last: entries.setdefault(idx, event)
        with self.path.open("w", encoding="utf-8", newline="") as stream:
            self.writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS[self.key]); self.writer.writeheader()
            for idx in sorted(entries): self._write(flatten_event(entries[idx], idx))
        self.writer = None


def validate_real_log(source: str|Path, output_dir: str|Path, *, implementation="python",
                      messages: str|Iterable[str]|None=None, strict=False, verify_crc=False,
                      verify_checksum=False, sample_first=5, sample_last=5, sample_every=1000,
                      full_export=False) -> dict[str, object]:
    """Scan one real log once and write summary.json plus per-message CSV samples."""
    source, out = Path(source), Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    selected = normalize_message_selection(messages)
    collectors = {k: _Collector(k, out, sample_first, sample_last, sample_every, full_export) for k in selected}
    stats = GnssLogStats()
    for event in iter_gnss_log(source, messages=selected, strict=strict, verify_crc=verify_crc,
                               verify_checksum=verify_checksum, stats=stats):
        collectors[event.message_type].add(event)
    for collector in collectors.values(): collector.finish()
    messages_summary = {k: {"target_lines": stats.target_lines[k], "records": stats.records[k],
        "malformed": stats.malformed[k], "csv_file": f"{k}.csv", "export_mode": "full" if full_export else "sample",
        "exported_rows": collectors[k].rows, "first_time": collectors[k].first_time, "last_time": collectors[k].last_time}
        for k in selected}
    summary = {"schema_version": SCHEMA_VERSION, "implementation": implementation,
        "source": {"file_name": source.name, "size_bytes": source.stat().st_size},
        "options": {"strict": strict, "verify_crc": verify_crc, "verify_checksum": verify_checksum,
                    "sample_first": sample_first, "sample_last": sample_last, "sample_every": sample_every,
                    "full_export": full_export},
        "stats": {"selected_messages": list(stats.selected_messages), "total_lines": stats.total_lines,
                  "unrelated_lines": stats.unrelated_lines, "target_lines": stats.target_lines,
                  "records": stats.records, "malformed": stats.malformed},
        "messages": messages_summary}
    (out/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    return summary
