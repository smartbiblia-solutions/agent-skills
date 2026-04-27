#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Example helper script for scrape-web-pages

This is a thin wrapper script that can be executed directly.
Imports and runs the main scraper from scrape.py.
"""

if __name__ == "__main__":  # pragma: no cover
    from scrape import main

    main()
