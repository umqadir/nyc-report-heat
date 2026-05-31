from __future__ import annotations

from nyc_report_heat.heat import heat_score
from nyc_report_heat.models import Candidate, HeatResult, RankedItem


def rank_candidate(candidate: Candidate, heat_windows: dict[str, HeatResult], rank_window: str) -> RankedItem:
    heat = heat_windows[rank_window]
    h_score = heat_score(heat)
    reasons: list[str] = []
    if heat.exact_url_mentions or heat.social_exact_mentions:
        reasons.append("exact URL mentions found")
    if heat.canonical_mentions:
        reasons.append("canonical URL variant mentions found")
    elif heat.filename_mentions:
        reasons.append("filename mentions found; lower-confidence heat")
    if heat.crawl_hits:
        reasons.append("exact URL found in Common Crawl index")
    if not reasons:
        reasons.append("no public exact-link mentions found in checked heat sources")
    return RankedItem(
        candidate=candidate,
        heat_windows=heat_windows,
        rank_window=rank_window,
        heat_score=h_score,
        heat_rank_score=h_score,
        rationale=reasons,
    )
