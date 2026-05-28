from HERD_download_maria_aws import create_db_engine
from sqlalchemy import text
from datetime import datetime

import re
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://ncses.nsf.gov/surveys/higher-education-research-development"

REMOVE_PHRASES = [
    "at institutions in the standard form survey population",
]


def normalize(s):
    s = s.lower().strip()

    for phrase in REMOVE_PHRASES:
        s = s.replace(phrase, "")

    s = s.replace("–", "-")
    s = s.replace("—", "-")
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s)

    return s


def similarity(a, b):
    a_words = set(normalize(a).split())
    b_words = set(normalize(b).split())

    if not a_words and not b_words:
        return 1
    if not a_words or not b_words:
        return 0

    return len(a_words & b_words) / len(a_words | b_words)


def extract_table_number(text):
    parts = text.strip().split()

    if len(parts) < 2:
        return None

    return parts[1]


def update_dict(table_dict, num, name):
    if num in table_dict:
        print(f"Duplicate table number {num}")

        if table_dict[num] == name:
            print("\tMatches previous table name")
        else:
            print(f"Mismatch:\n\t{name}\n\t{table_dict[num]}")
    else:
        table_dict[num] = name


def scrape_table_dict(year):
    url = f"{BASE_URL}/{year}#data"

    page = requests.get(url, timeout=10)
    page.raise_for_status()

    soup = BeautifulSoup(page.content, "html.parser")
    table_dict = {}

    table_rows = soup.find_all("div", class_="table-row")

    for row in table_rows:
        table_names = row.find_all("a", class_="table-title")
        table_numbers = row.find_all("a", class_="table-link")

        if len(table_names) != 1 or len(table_numbers) != 1:
            print("DIDN'T FIND EXACTLY ONE ITEM IN ROW")
            print(f"Names: {len(table_names)}")
            print(f"Numbers: {len(table_numbers)}")
            continue

        table_number = extract_table_number(table_numbers[0].get_text(strip=True))

        if table_number is None:
            print("Could not parse table number")
            continue

        table_name = table_names[0].get_text(strip=True)
        update_dict(table_dict, table_number, table_name)

    supplemental_tables = soup.find(id="supplemental-tables")

    if supplemental_tables is None:
        print("No supplemental tables")
    else:
        print("Reading supplemental tables")

        for row in supplemental_tables.find_all("tr"):
            table_data = row.find_all("td")

            if len(table_data) < 2:
                continue

            table_number = extract_table_number(table_data[1].get_text(strip=True))

            if table_number is None:
                print("Could not parse supplemental table number")
                continue

            table_name = table_data[0].get_text(strip=True)
            update_dict(table_dict, table_number, table_name)

    return table_dict

def get_expected_table_names(year):
    year = str(year)

    return {
        21: f"Higher education R&D expenditures, ranked by FY {year} R&D expenditures: FYs 2010-{year[2:]}",
        22: f"Higher education R&D expenditures, ranked by all R&D expenditures, by source of funds: FY {year}",
        23: f"Higher education R&D expenditures, ranked by all R&D expenditures, by R&D field: FY {year}",
        79: (
            f"Headcount and FTEs of R&D personnel at higher education institutions, "
            f"by state, institutional control, institution, and personnel function: FY {year}"
        ),
    }

def find_best_matches(year, table_dict):
    table_names = get_expected_table_names(year)

    actual_numbers = {
        num: {"table_number": None, "confidence": 0}
        for num in table_names
    }

    for num, expected_name in table_names.items():
        for scraped_num, scraped_name in table_dict.items():
            if normalize(expected_name) == normalize(scraped_name):
                actual_numbers[num]["table_number"] = scraped_num
                actual_numbers[num]["confidence"] = 1
                break

            sim = similarity(expected_name, scraped_name)

            if sim > actual_numbers[num]["confidence"]:
                actual_numbers[num]["table_number"] = scraped_num
                actual_numbers[num]["confidence"] = sim

    return actual_numbers


def save_table_dict(year, table_dict):
    with open(f"tables_{year}.tsv", "w", encoding="utf-8") as f:
        for key, value in table_dict.items():
            f.write(f"{key}\t{value}\n")

def setup_table_lookup_table(engine):
    """
    Create the database table that stores logical HERD table numbers
    and the actual NSF table numbers used for each year.

    This only creates the table if it does not already exist.
    Existing data will not be deleted.
    """
    query = text("""
        CREATE TABLE IF NOT EXISTS herd_table_lookup (
            year INT NOT NULL,
            logical_table_number INT NOT NULL,
            actual_table_number INT NOT NULL,
            expected_title TEXT,
            scraped_title TEXT,
            confidence FLOAT,
            source_url TEXT,
            last_update DATETIME,
            PRIMARY KEY (year, logical_table_number)
        )
    """)

    with engine.begin() as conn:
        conn.execute(query)

    print("herd_table_lookup table is ready.")

def populate_table_lookup_table(year, table_dict, actual_numbers, engine):
    """
    Insert or update table-number lookup values in herd_table_lookup.

    Each row maps:
        year + logical_table_number -> actual_table_number
    """
    expected_table_names = get_expected_table_names(year)
    source_url = f"{BASE_URL}/{year}#data"

    query = text("""
        INSERT INTO herd_table_lookup
            (
                year,
                logical_table_number,
                actual_table_number,
                expected_title,
                scraped_title,
                confidence,
                source_url,
                last_update
            )
        VALUES
            (
                :year,
                :logical_table_number,
                :actual_table_number,
                :expected_title,
                :scraped_title,
                :confidence,
                :source_url,
                :last_update
            )
        ON DUPLICATE KEY UPDATE
            actual_table_number = VALUES(actual_table_number),
            expected_title = VALUES(expected_title),
            scraped_title = VALUES(scraped_title),
            confidence = VALUES(confidence),
            source_url = VALUES(source_url),
            last_update = VALUES(last_update)
    """)

    with engine.begin() as conn:
        for logical_table_number, match_info in actual_numbers.items():
            actual_table_number = match_info["table_number"]
            confidence = match_info["confidence"]

            if actual_table_number is None:
                print(f"Skipping logical table {logical_table_number}: no match found")
                continue

            record = {
                "year": int(year),
                "logical_table_number": int(logical_table_number),
                "actual_table_number": int(actual_table_number),
                "expected_title": expected_table_names[logical_table_number],
                "scraped_title": table_dict.get(str(actual_table_number)),
                "confidence": float(confidence),
                "source_url": source_url,
                "last_update": datetime.now(),
            }

            print(
                f"Saving year={year}, "
                f"logical_table={logical_table_number}, "
                f"actual_table={actual_table_number}, "
                f"confidence={confidence:.2f}"
            )

            conn.execute(query, record)

    print(f"Finished saving table lookup values for {year}.")

def main():
    year = "2022"

    engine = create_db_engine()

    with engine.connect() as conn:
        db_name = conn.execute(text("SELECT DATABASE()")).scalar()
        print(f"Connected to database: {db_name}")

    setup_table_lookup_table(engine)

    table_dict = scrape_table_dict(year)
    save_table_dict(year, table_dict)

    actual_numbers = find_best_matches(year, table_dict)

    print("\nMatched table numbers:")
    for logical_table_number, match in actual_numbers.items():
        print(
            f"Logical table {logical_table_number} -> "
            f"Actual table {match['table_number']} "
            f"(confidence: {match['confidence']:.2f})"
        )

    populate_table_lookup_table(year, table_dict, actual_numbers, engine)

    engine.dispose()


if __name__ == "__main__":
    main()