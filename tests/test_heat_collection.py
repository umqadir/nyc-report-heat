from nyc_report_heat.heat import _heat_queries, collect_heat
from nyc_report_heat.models import Candidate, Mention


def test_pdf_heat_queries_keep_exact_url_before_filename() -> None:
    candidate = Candidate(
        source_id="x",
        source_name="Test",
        kind="report",
        title="Report",
        url="https://example.com/reports/access-denied-long-filename.pdf",
        document_url="https://example.com/reports/access-denied-long-filename.pdf",
        format="pdf",
    )

    queries = _heat_queries(candidate)

    assert queries[0] == (candidate.heat_url, "exact_url")
    assert ("access-denied-long-filename.pdf", "filename") in queries


def test_collect_heat_dedupes_duplicate_mentions(monkeypatch) -> None:
    candidate = Candidate(source_id="x", source_name="Test", kind="report", title="Report", url="https://example.com/report")
    mention = Mention(
        provider="googlenews",
        query=candidate.heat_url,
        url="https://news.example.com/story",
        title="Story",
        confidence="exact_url",
    )

    def fake_google_news(client, candidate, days):
        return 2, [mention, mention], []

    monkeypatch.setattr("nyc_report_heat.heat.query_google_news", fake_google_news)

    result = collect_heat(client=None, candidate=candidate, days=7, providers={"googlenews"})  # type: ignore[arg-type]

    assert result.exact_url_mentions == 1
    assert len(result.mentions) == 1


def test_commoncrawl_is_not_counted_in_windowed_heat(monkeypatch) -> None:
    candidate = Candidate(source_id="x", source_name="Test", kind="report", title="Report", url="https://example.com/report")

    def fake_commoncrawl(client, candidate):
        return 5, []

    monkeypatch.setattr("nyc_report_heat.heat.query_common_crawl", fake_commoncrawl)

    result = collect_heat(client=None, candidate=candidate, days=1, providers={"commoncrawl"})  # type: ignore[arg-type]

    assert result.crawl_hits == 0
    assert result.errors == ["commoncrawl:skipped:not available as a rolling-window heat signal"]
