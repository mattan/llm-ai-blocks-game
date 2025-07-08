"""portfolio_calc_summary.py

This module provides a helper function that summarises pair-wise optimal shift
statistics for every stock ticker that is currently stored in the TTL cache of
`get_yahoo_finance_data` (defined in `portfolio_calc.py`).

The public function `summarise_arbitrage` returns a list of dictionaries.  Each
dictionary contains:
    ticker1       – first ticker symbol
    ticker2       – second ticker symbol (can be identical to ticker1)
    shift         – optimal shift in days that maximises the absolute
                    correlation between the two return series (as determined
                    by `find_optimal_shift`)
    covariance    – Pearson correlation coefficient at that shift
    score         – the absolute value of the correlation (used for sorting)

The list is sorted from highest score to lowest score.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .portfolio_calc import (
    calculate_shifted_data,
    find_optimal_shift,
    get_yahoo_finance_data,
)


def _extract_cached_tickers() -> List[str]:
    """Return a list of all ticker symbols that currently exist in the
    ttl_cache backing `get_yahoo_finance_data`.

    The decorator `@ttl_cache` adds a ``cache`` attribute to the wrapped
    function, which is an instance of :class:`cachetools.TTLCache`.  The
    keys inside that cache are the arguments tuple used for the function call.
    In our case the key structure is typically ``(ticker,)``.
    """
    try:
        cache = get_yahoo_finance_data.cache  # type: ignore[attr-defined]
    except AttributeError:
        # If, for some reason, the function was monkey-patched and the cache
        # attribute is missing, return an empty list so that the caller gets
        # a graceful fallback rather than crashing the application.
        return []

    tickers: List[str] = []
    for key in cache.keys():
        # Keys are usually tuples like ('KO',) – handle both tuple and str.
        if isinstance(key, tuple):
            if key and isinstance(key[0], str):
                tickers.append(key[0])
        elif isinstance(key, str):
            tickers.append(key)

    # Remove possible duplicates while preserving order.
    seen = set()
    unique_tickers: List[str] = []
    for t in tickers:
        if t not in seen:
            unique_tickers.append(t)
            seen.add(t)
    return unique_tickers


def summarise_arbitrage() -> List[Dict[str, Any]]:
    """Generate the arbitrage summary as requested by the user.

    The function inspects the TTL cache of ``get_yahoo_finance_data`` to find
    all downloaded tickers, computes the optimal shift and corresponding
    correlation for every *ordered* pair of tickers (including a ticker with
    itself), and returns the results sorted by descending *score* (absolute
    correlation).
    """

    tickers = _extract_cached_tickers()
    if not tickers:
        # Nothing in cache – return empty list immediately.
        return []

    results: List[Dict[str, Any]] = []

    # Use ordered pairs so that (A, B) and (B, A) are considered distinct,
    # as per the user's instruction to evaluate "לכל זוג מניות (כולל מנייה עם
    # עצמה)".
    for ticker1 in tickers:
        for ticker2 in tickers:
            try:
                # Retrieve dataframes from cache; if not present for some
                # reason, fall back to normal function call (it will also add
                # to cache).
                data1, _ = get_yahoo_finance_data(ticker1)
                data2, _ = get_yahoo_finance_data(ticker2)
            except Exception:
                # Skip pair if data retrieval failed.
                continue

            if data1 is None or data2 is None:
                continue

            # Determine optimal shift and corresponding correlation.
            shift = find_optimal_shift(data1, data2)
            _, covariance = calculate_shifted_data(data1, data2, shift)

            # Guard against NaN results.
            if covariance is None or (isinstance(covariance, float) and not covariance == covariance):
                covariance = 0.0
            score = abs(covariance)

            results.append(
                {
                    "ticker1": ticker1,
                    "ticker2": ticker2,
                    "shift": shift,
                    "covariance": float(covariance),
                    "score": float(score),
                }
            )

    # Sort by score descending.
    results.sort(key=lambda item: item["score"], reverse=True)
    return results


# If you want to allow running this module directly for quick CLI testing, you
# can keep the following block. It will print the summary to stdout.
if __name__ == "__main__":  # pragma: no cover
    import json

    summary = summarise_arbitrage()
    print(json.dumps(summary, indent=2, ensure_ascii=False))
