from __future__ import annotations

from collections.abc import Sequence
from textwrap import dedent


def section(title: str) -> None:
    print()
    print("=" * 88)
    print(title.upper())
    print("=" * 88)


def subsection(title: str) -> None:
    print()
    print("-" * 88)
    print(title)
    print("-" * 88)


def explain(text: str) -> None:
    print(dedent(text).strip())


def show_sql(sql: str) -> None:
    print()
    print("SQL executado:")
    print(sql.strip())


def print_table(rows: Sequence[dict], max_width: int = 34) -> None:
    if not rows:
        print("(nenhum resultado)")
        return

    headers = list(rows[0].keys())
    normalized_rows = [
        {key: _shorten(_format_value(row.get(key)), max_width) for key in headers}
        for row in rows
    ]
    widths = {
        header: max(
            len(header),
            *(len(row[header]) for row in normalized_rows),
        )
        for header in headers
    }

    separator = "+".join("-" * (widths[header] + 2) for header in headers)
    header_line = " | ".join(header.ljust(widths[header]) for header in headers)

    print(separator)
    print(header_line)
    print(separator)
    for row in normalized_rows:
        print(" | ".join(row[header].ljust(widths[header]) for header in headers))
    print(separator)


def _format_value(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _shorten(value: str, max_width: int) -> str:
    if len(value) <= max_width:
        return value
    return value[: max_width - 3] + "..."
