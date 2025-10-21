import pytest
import sqlite3
import json
from datetime import datetime


@pytest.fixture
def db_connection():
    """Fixture to create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER UNIQUE,
        utc_date TEXT,
        competition_code TEXT,
        home_team TEXT,
        away_team TEXT,
        status TEXT,
        score_home INTEGER,
        score_away INTEGER,
        raw_json TEXT
    )
    """)
    conn.commit()
    yield conn
    conn.close()


def test_store_json_data(db_connection):
    """Test storing JSON data into SQLite."""
    print("\nStarting test: Storing JSON data...")

    # Sample JSON data (simplified football matches)
    json_data = """
    {
      "filters": {"dateFrom": "2025-10-21", "dateTo": "2025-10-22"},
      "resultSet": {"count": 2},
      "matches": [
        {"id": 535218, "utcDate": "2025-10-21T00:30:00Z", "competition": {"code": "BSA"}, "homeTeam": {"name": "Santos FC"}, "awayTeam": {"name": "EC Vitória"}, "status": "FINISHED", "score": {"fullTime": {"home": 0, "away": 1}}},
        {"id": 551955, "utcDate": "2025-10-21T16:45:00Z", "competition": {"code": "CL"}, "homeTeam": {"name": "FC Barcelona"}, "awayTeam": {"name": "PAE Olympiakos SFP"}, "status": "TIMED", "score": {"fullTime": {"home": null, "away": null}}}
      ]
    }
    """
    data = json.loads(json_data)

    cursor = db_connection.cursor()
    insert_data = []
    for match in data.get("matches", []):
        score_home = (
            match["score"]["fullTime"]["home"]
            if match["status"] == "FINISHED"
            else None
        )
        score_away = (
            match["score"]["fullTime"]["away"]
            if match["status"] == "FINISHED"
            else None
        )
        insert_data.append(
            (
                match["id"],
                match["utcDate"],
                match["competition"]["code"],
                match["homeTeam"]["name"],
                match["awayTeam"]["name"],
                match["status"],
                score_home,
                score_away,
                json.dumps(match),
            )
        )

    cursor.executemany(
        """
    INSERT INTO matches (match_id, utc_date, competition_code, home_team, away_team, status, score_home, score_away, raw_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        insert_data,
    )
    db_connection.commit()

    # Verify insertion
    cursor.execute("SELECT COUNT(*) FROM matches")
    count = cursor.fetchone()[0]
    assert count == 2, f"Expected 2 rows, got {count}"

    print(f"Stored {count} matches successfully.")


def test_retrieve_json_data(db_connection):
    """Test retrieving and querying JSON data from SQLite."""
    print("\nStarting test: Retrieving JSON data...")

    # First, insert sample data (reuse from previous test logic for independence)
    json_data = """
    {
      "filters": {"dateFrom": "2025-10-21", "dateTo": "2025-10-22"},
      "resultSet": {"count": 2},
      "matches": [
        {"id": 535218, "utcDate": "2025-10-21T00:30:00Z", "competition": {"code": "BSA"}, "homeTeam": {"name": "Santos FC"}, "awayTeam": {"name": "EC Vitória"}, "status": "FINISHED", "score": {"fullTime": {"home": 0, "away": 1}}},
        {"id": 551955, "utcDate": "2025-10-21T16:45:00Z", "competition": {"code": "CL"}, "homeTeam": {"name": "FC Barcelona"}, "awayTeam": {"name": "PAE Olympiakos SFP"}, "status": "TIMED", "score": {"fullTime": {"home": null, "away": null}}}
      ]
    }
    """
    data = json.loads(json_data)

    cursor = db_connection.cursor()
    insert_data = []
    for match in data.get("matches", []):
        score_home = (
            match["score"]["fullTime"]["home"]
            if match["status"] == "FINISHED"
            else None
        )
        score_away = (
            match["score"]["fullTime"]["away"]
            if match["status"] == "FINISHED"
            else None
        )
        insert_data.append(
            (
                match["id"],
                match["utcDate"],
                match["competition"]["code"],
                match["homeTeam"]["name"],
                match["awayTeam"]["name"],
                match["status"],
                score_home,
                score_away,
                json.dumps(match),
            )
        )

    cursor.executemany(
        """
    INSERT INTO matches (match_id, utc_date, competition_code, home_team, away_team, status, score_home, score_away, raw_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        insert_data,
    )
    db_connection.commit()

    # Retrieve and query
    cursor.execute(
        "SELECT home_team, status FROM matches WHERE competition_code = 'CL'"
    )
    result = cursor.fetchone()
    assert result == ("FC Barcelona", "TIMED"), (
        f"Expected ('FC Barcelona', 'TIMED'), got {result}"
    )

    # JSON extraction test
    cursor.execute(
        "SELECT json_extract(raw_json, '$.score.fullTime.home') FROM matches WHERE status = 'FINISHED'"
    )
    score = cursor.fetchone()[0]
    assert score == 0, f"Expected home score 0, got {score}"

    print("Retrieved data matches expectations.")
    print(f"Example retrieved score: {score}")
