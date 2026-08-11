"""Compare Python and MATLAB real-log validation artifacts."""
from __future__ import annotations

import csv, json, math
from pathlib import Path

FLOAT_COLUMNS = {
    "sow","header_sow","latency_s","age_s","hor_speed_mps","track_deg","vert_speed_mps",
    "pseudorange_m","pseudorange_std_m","adr_cycles","adr_std_cycles","doppler_hz","cn0_dbhz",
    "lock_time_s","latitude_deg","longitude_deg","ellipsoidal_height_m","vel_n_mps","vel_e_mps",
    "vel_u_mps","roll_deg","pitch_deg","azimuth_deg","msl_height_m","undulation_m","lat_std_m",
    "lon_std_m","hgt_std_m","diff_age_s","sol_age_s","utc_seconds_of_day","speed_knots","course_deg",
    "magnetic_variation_deg",
}


def _load_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def compare_validation_outputs(left_dir: str|Path, right_dir: str|Path, *, rtol=1e-9, atol=1e-12):
    left_dir, right_dir = Path(left_dir), Path(right_dir)
    left = json.loads((left_dir/"summary.json").read_text(encoding="utf-8"))
    right = json.loads((right_dir/"summary.json").read_text(encoding="utf-8"))
    issues = []
    if left.get("schema_version") != right.get("schema_version"): issues.append("schema_version differs")
    if left.get("source",{}).get("size_bytes") != right.get("source",{}).get("size_bytes"): issues.append("source size differs")
    selected = left.get("stats",{}).get("selected_messages",[])
    if selected != right.get("stats",{}).get("selected_messages",[]): issues.append("selected_messages differs")
    per_message = {}
    for key in selected:
        msg_issues = []
        for field in ("target_lines","records","malformed"):
            a = left.get("messages",{}).get(key,{}).get(field)
            b = right.get("messages",{}).get(key,{}).get(field)
            if a != b: msg_issues.append(f"{field}: {a!r} != {b!r}")
        lf, lr = _load_csv(left_dir/f"{key}.csv"); rf, rr = _load_csv(right_dir/f"{key}.csv")
        if lf != rf: msg_issues.append("CSV columns differ")
        elif len(lr) != len(rr): msg_issues.append(f"CSV row count: {len(lr)} != {len(rr)}")
        else:
            for n,(a,b) in enumerate(zip(lr,rr),1):
                for col in lf:
                    av,bv = a.get(col,""), b.get(col,"")
                    if col in FLOAT_COLUMNS and av and bv:
                        try: same = math.isclose(float(av), float(bv), rel_tol=rtol, abs_tol=atol)
                        except ValueError: same = False
                    else: same = av == bv
                    if not same: msg_issues.append(f"row {n} {col}: {av!r} != {bv!r}")
                    if len(msg_issues) >= 20: break
                if len(msg_issues) >= 20:
                    msg_issues.append("additional differences omitted"); break
        per_message[key] = {"status":"PASS" if not msg_issues else "FAIL", "issues":msg_issues}
        issues.extend(f"{key}: {x}" for x in msg_issues)
    return {"schema_version":1, "status":"PASS" if not issues else "FAIL", "rtol":rtol, "atol":atol,
            "messages":per_message, "issues":issues}
