"""process_hamza against every call the Lua module made (hamza.jsonl.gz)."""

from conftest import fixture_records

from mazini.hamza import process_hamza


def test_hamza_matches_every_recorded_call():
    recs = fixture_records("hamza.jsonl.gz")
    assert len(recs) > 50000
    bad = [(r["in"], r["out"], process_hamza(r["in"])) for r in recs if process_hamza(r["in"]) != r["out"]]
    assert bad[:10] == []
