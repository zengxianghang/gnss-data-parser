# u-blox / NMEA parser notes

## RMC

The RMC parser targets standard NMEA RMC sentences emitted by u-blox positioning receivers.

Public APIs:

```python
from gnss_parser.ublox import iter_rmc, parse_rmc_line, read_rmc
```

Supported behavior:

- accepts direct `$xxRMC` sentences with talker IDs such as `GP` and `GN`
- preserves UTC text and `ddmmyy` date text
- exposes unambiguous UTC seconds-of-day when UTC is present
- converts NMEA latitude/longitude degrees+minutes to signed decimal degrees
- preserves speed over ground in knots and course over ground in degrees
- accepts legacy sentences that omit newer optional trailing fields
- exposes magnetic variation, position mode and navigation status when present
- preserves `status=V` records rather than filtering them
- supports explicit NMEA XOR checksum validation via `verify_checksum=True`
- supports streaming tolerant/strict behavior for mixed text logs

The parser intentionally does not infer a century from the two-digit RMC year and does not convert UTC to GPST. Those operations require application-level time policy (including leap-second handling) and belong downstream.

Reference structure used for compatibility:

```text
$xxRMC,time,status,lat,NS,lon,EW,spd,cog,date,mv,mvEW,posMode,navStatus*cs
```

u-blox firmware/NMEA versions may omit optional trailing fields. Missing optional fields are returned as empty strings or `None`, as appropriate.
