# Recommendation to the Head of Strategy

**What the alert is for.** At the end of each lap, the alert flags a rival who is likely to pit within their next three laps. It could help the pit wall choose which rivals to watch when weighing an undercut or a cover stop. It predicts what rivals *do*, not what we *should* do.

**How we tested it.** We trained on 2018–2021 races and tested on the first 11 races of 2022, which contain 370 rival pit stops. Every system could alert on at most 10% of rival-laps (about 945 alerts), so all face the same workload.

| System | Stops warned in advance | Alerts | Wrong alerts |
|---|---:|---:|---:|
| Simple historical rule (circuit, tyre, tyre age) | 94 of 370 (25%) | 931 | 681 (73%) |
| Best standard model | 140 of 370 (38%) | 945 | 605 (64%) |
| Same model, less detailed (our change) | **159 of 370 (43%)** | 938 | 562 (60%) |

Our change forces each judgement to rest on at least 100 past laps instead of 30. It warned of 19 more stops with slightly fewer alerts.

**Most important blind spot.** The alert is almost silent for stops on fresh tyres. When the rival's tyres were 10 laps old or less, it missed 94 of 102 such stops. These may be reactive stops (e.g. under a safety car), often the most decisive; that cause is not yet confirmed. It also over-alerts at unfamiliar circuits: at Miami 2022, one rival-lap in five triggered an alert, and three of four alerts were wrong.

**Recommendation: further checking, not live use yet.** The improved version is our best candidate, but:
- six in ten alerts are still wrong;
- the same 2022 races were used to choose this version and its alert level, so 43% is likely optimistic;
- 19 extra stops over half a season could partly be chance;
- the scores are not reliable percentages, and no gain in positions or race time has been measured.

**Limitation.** This test replays recorded data. It does not show that the live timing feed would deliver the same information in time.

**Next check.** Freeze this exact version and alert level and test it once on later races it has never seen. Also review the missed fresh-tyre stops against safety-car periods. Until then, use it at most as a secondary prompt, and never read "no alert" as "no stop coming".
