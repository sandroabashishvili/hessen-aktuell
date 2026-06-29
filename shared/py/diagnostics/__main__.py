from __future__ import annotations

import argparse
import json

from .content_balance import run_content_balance_diagnostics
from .internal_links import run_internal_link_diagnostics
from .seo import run_seo_diagnostics
from .sitemap import run_sitemap_diagnostics
from .source_freshness import run_source_freshness_diagnostics
from .source_links import run_source_link_diagnostics


def _print_human_summary(
    result: dict[str, object],
    source_freshness: dict[str, object],
    content_balance: dict[str, object],
) -> None:
    print("Hessen Aktuell Diagnostics")
    print("--------------------------")
    print(
        "Source links: "
        f"{result['source_links']['ok']}/{result['source_links']['total']} ok, "
        f"{result['source_links']['broken']} broken"
    )
    if result["source_links"].get("parser_verified"):
        print(
            "Source link fallback: "
            f"{result['source_links']['parser_verified']} broken link check verified by parser output"
        )
    print(
        "Source freshness: "
        f"{result['source_freshness']['ok']} ok, "
        f"{result['source_freshness']['notices']} notice, "
        f"{result['source_freshness']['warnings']} warning, "
        f"{result['source_freshness']['empty']} empty"
    )
    stale = [
        check
        for check in source_freshness["checks"]
        if check["status"] != "ok" or check.get("stale_notice")
    ]
    if stale:
        print("Freshness notices:")
        for check in stale:
            age = "-" if check.get("age_days") is None else f"{check['age_days']}d"
            print(f"- {check['source_id']}: latest {check['latest_date'] or '-'} ({age}); {check['note']}")
    print(
        "Content balance: "
        f"{content_balance['total_items']} items, "
        f"top city {content_balance['top_city']['name']}={content_balance['top_city']['count']}, "
        f"top source {content_balance['top_source']['name']}={content_balance['top_source']['count']}"
    )
    print(
        "Internal links: "
        f"{result['internal_links']['ok']} ok, "
        f"{result['internal_links']['broken']} broken"
    )
    print(
        "Sitemap: "
        f"{result['sitemap']['sitemap_url_count']} URLs, "
        f"{result['sitemap']['missing']} missing, "
        f"robots {'ok' if result['sitemap']['robots_exists'] else 'missing'}"
    )
    print(
        "SEO meta: "
        f"{result['seo']['ok']} ok, "
        f"{result['seo']['missing']} missing"
    )
    print(f"Overall: {result['status']}")
    print()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Hessen Aktuell diagnostics.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full machine-readable JSON summary after the human summary.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    source_links = run_source_link_diagnostics()
    source_freshness = run_source_freshness_diagnostics()
    internal_links = run_internal_link_diagnostics()
    content_balance = run_content_balance_diagnostics()
    sitemap = run_sitemap_diagnostics()
    seo = run_seo_diagnostics()
    effective_broken_source_links = _effective_broken_source_links(source_links, source_freshness)
    result = {
        "source_links": {
            "total": source_links["total"],
            "ok": source_links["ok"],
            "warnings": source_links["warnings"],
            "broken": source_links["broken"],
            "effective_broken": effective_broken_source_links,
            "parser_verified": source_links["broken"] - effective_broken_source_links,
            "report_path": source_links["report_path"],
        },
        "source_freshness": {
            "total": source_freshness["total"],
            "ok": source_freshness["ok"],
            "notices": source_freshness["notices"],
            "warnings": source_freshness["warnings"],
            "empty": source_freshness["empty"],
            "report_path": source_freshness["report_path"],
        },
        "internal_links": {
            "total": internal_links["total"],
            "ok": internal_links["ok"],
            "skipped": internal_links["skipped"],
            "broken": internal_links["broken"],
            "report_path": internal_links["report_path"],
        },
        "content_balance": {
            "total_items": content_balance["total_items"],
            "top_city": content_balance["top_city"],
            "top_source": content_balance["top_source"],
            "status": content_balance["status"],
            "report_path": content_balance["report_path"],
        },
        "sitemap": {
            "total": sitemap["total"],
            "ok": sitemap["ok"],
            "missing": sitemap["missing"],
            "sitemap_url_count": sitemap["sitemap_url_count"],
            "robots_exists": sitemap["robots_exists"],
            "report_path": sitemap["report_path"],
        },
        "seo": {
            "total": seo["total"],
            "ok": seo["ok"],
            "missing": seo["missing"],
            "report_path": seo["report_path"],
        },
        "status": (
            "ok"
            if source_freshness["warnings"] == 0

            and internal_links["broken"] == 0
            and content_balance["status"] == "ok"
            and sitemap["missing"] == 0
            and seo["missing"] == 0
            else "attention_required"
        ),
    }
    _print_human_summary(result, source_freshness, content_balance)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))



def _effective_broken_source_links(source_links: dict[str, object], source_freshness: dict[str, object]) -> int:
    parser_verified_ids = {
        check["source_id"]
        for check in source_freshness["checks"]
        if check["status"] == "ok" and check.get("parsed_count", 0) > 0
    }
    return sum(
        1
        for check in source_links["checks"]
        if check["status"] == "broken" and check["source_id"] not in parser_verified_ids
    )
if __name__ == "__main__":
    main()



