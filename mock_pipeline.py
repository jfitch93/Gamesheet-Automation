"""
WRHL Gamesheet Processor — Step 1
Fake data pipeline: parse gamesheets, check rosters, assign tags.
Run with: python mock_pipeline.py
"""

import re
from datetime import date

# ─────────────────────────────────────────────
# MOCK SCHEDULE — games, referees, submission status
# ─────────────────────────────────────────────

SCHEDULE = [
    {
        "game_id": "G001",
        "date": "Jul 9, 2025",
        "time": "7:00 PM",
        "home_team": "Ice Dragons",
        "away_team": "Saracens",
        "referee": "Matt Kowalski",
        "referee_email": "ref_matt@wrhl.ca",
        "referee_phone": "204-555-0181",
        "submitted": True,
        "conv_id": "conv_001",
    },
    {
        "game_id": "G002",
        "date": "Jul 9, 2025",
        "time": "8:15 PM",
        "home_team": "Wolfpack",
        "away_team": "Brawlers",
        "referee": "Kira Dubois",
        "referee_email": "ref_kira@wrhl.ca",
        "referee_phone": "204-555-0194",
        "submitted": True,
        "conv_id": "conv_002",
    },
    {
        "game_id": "G003",
        "date": "Jul 10, 2025",
        "time": "6:30 PM",
        "home_team": "Thunderhawks",
        "away_team": "Night Owls",
        "referee": "Dan Reimer",
        "referee_email": "ref_dan@wrhl.ca",
        "referee_phone": "204-555-0162",
        "submitted": True,
        "conv_id": "conv_003",
    },
    {
        "game_id": "G004",
        "date": "Jul 11, 2025",
        "time": "7:00 PM",
        "home_team": "Ice Dragons",
        "away_team": "Wolfpack",
        "referee": "Matt Kowalski",
        "referee_email": "ref_matt@wrhl.ca",
        "referee_phone": "204-555-0181",
        "submitted": True,
        "conv_id": "conv_004",
    },
    {
        "game_id": "G005",
        "date": "Jul 12, 2025",
        "time": "6:00 PM",
        "home_team": "Saracens",
        "away_team": "Brawlers",
        "referee": "Kira Dubois",
        "referee_email": "ref_kira@wrhl.ca",
        "referee_phone": "204-555-0194",
        "submitted": True,
        "conv_id": "conv_005",
    },
    {
        "game_id": "G006",
        "date": "Jul 12, 2025",
        "time": "8:15 PM",
        "home_team": "Night Owls",
        "away_team": "Thunderhawks",
        "referee": "Sarah Fontaine",
        "referee_email": "ref_sarah@wrhl.ca",
        "referee_phone": "204-555-0177",
        "submitted": True,
        "conv_id": "conv_006",
    },
    {
        "game_id": "G007",
        "date": "Jul 13, 2025",
        "time": "7:30 PM",
        "home_team": "Brawlers",
        "away_team": "Ice Dragons",
        "referee": "Dan Reimer",
        "referee_email": "ref_dan@wrhl.ca",
        "referee_phone": "204-555-0162",
        "submitted": True,
        "conv_id": "conv_007",
    },
    {
        "game_id": "G008",
        "date": "Jul 14, 2025",
        "time": "6:00 PM",
        "home_team": "Wolfpack",
        "away_team": "Saracens",
        "referee": "Matt Kowalski",
        "referee_email": "ref_matt@wrhl.ca",
        "referee_phone": "204-555-0181",
        "submitted": True,
        "conv_id": "conv_008",
    },
    {
        "game_id": "G009",
        "date": "Jul 14, 2025",
        "time": "8:15 PM",
        "home_team": "Night Owls",
        "away_team": "Wolfpack",
        "referee": "Sarah Fontaine",
        "referee_email": "ref_sarah@wrhl.ca",
        "referee_phone": "204-555-0177",
        "submitted": True,
        "conv_id": "conv_009",
    },
    {
        "game_id": "G010",
        "date": "Jul 16, 2025",
        "time": "7:00 PM",
        "home_team": "Saracens",
        "away_team": "Thunderhawks",
        "referee": "Kira Dubois",
        "referee_email": "ref_kira@wrhl.ca",
        "referee_phone": "204-555-0194",
        "submitted": False,
        "conv_id": None,
    },
    {
        "game_id": "G011",
        "date": "Jul 16, 2025",
        "time": "8:30 PM",
        "home_team": "Ice Dragons",
        "away_team": "Night Owls",
        "referee": "Dan Reimer",
        "referee_email": "ref_dan@wrhl.ca",
        "referee_phone": "204-555-0162",
        "submitted": False,
        "conv_id": None,
    },
    {
        "game_id": "G012",
        "date": "Jul 17, 2025",
        "time": "6:30 PM",
        "home_team": "Brawlers",
        "away_team": "Wolfpack",
        "referee": "Sarah Fontaine",
        "referee_email": "ref_sarah@wrhl.ca",
        "referee_phone": "204-555-0177",
        "submitted": False,
        "conv_id": None,
    },
]

# ─────────────────────────────────────────────
# FAKE INBOX — 9 mock emails with gamesheet text
# ─────────────────────────────────────────────

FAKE_EMAILS = [
    {
        "id": "conv_001",
        "subject": "Gamesheet - Ice Dragons vs Saracens - Jul 9",
        "from": "ref_matt@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 9, 2025
Home Team: Ice Dragons
Away Team: Saracens
Final Score: Ice Dragons 4 - Saracens 2

HOME ROSTER (Ice Dragons):
#7   Carter Novak
#11  Dylan Marsh
#18  Brett Kowalski
#23  Tom Hessler
#31  Mike Oduya
#44  Sam Firth
#55  Jake Lowen
#67  Andre Pelletier

AWAY ROSTER (Saracens):
#3   Ryan Stokes
#9   Liam Dunn
#14  Connor Walsh
#21  Brody Chen
#29  Marcus Reeves
#35  Tyler Park
#42  Nate Finley
#50  Joel Stroud

PENALTIES:
- Connor Walsh (#14, Saracens) — Slashing — 2 min
- Sam Firth (#44, Ice Dragons) — Hooking — 2 min
""",
    },
    {
        "id": "conv_002",
        "subject": "Gamesheet - Wolfpack vs Brawlers - Jul 9",
        "from": "ref_kira@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 9, 2025
Home Team: Wolfpack
Away Team: Brawlers
Final Score: Wolfpack 1 - Brawlers 3

HOME ROSTER (Wolfpack):
#4   Owen Reid
#10  Garrett Flynn
#17  Marcus Stone
#22  Dillon Chow
#38  Scott Mercer
#45  Evan Koval
#60  Zach Bourne

AWAY ROSTER (Brawlers):
#6   Tyler Bass
#13  James Ortega
#20  Peter Vance
#27  Caleb Norris
#33  Shane Dumont
#41  Drew Larkin
#58  UNKNOWN PLAYER

PENALTIES:
- James Ortega (#13, Brawlers) — Roughing — 2 min
""",
    },
    {
        "id": "conv_003",
        "subject": "Gamesheet - Thunderhawks vs Night Owls - Jul 10",
        "from": "ref_dan@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 10, 2025
Home Team: Thunderhawks
Away Team: Night Owls
Final Score: Thunderhawks 5 - Night Owls 1

HOME ROSTER (Thunderhawks):
#2   Devon Kramer
#8   Logan Pierce
#15  Ben Hartley
#26  Alex Sutton
#37  Mike Cannon
#49  Will Travers
#63  Noah Blight

AWAY ROSTER (Night Owls):
#5   Cam Decker
#12  Elliot Moore
#19  Finn Gallagher
#28  Jordan Nash
#34  Sam Polley
#47  Adam Russo
#56  GHOST PLAYER

PENALTIES:
- Ben Hartley (#15, Thunderhawks) — Fighting — 5 min
- Jordan Nash (#28, Night Owls) — Fighting — 5 min
- Jordan Nash (#28, Night Owls) — Game Misconduct — 10 min
""",
    },
    {
        "id": "conv_004",
        "subject": "Gamesheet - Ice Dragons vs Wolfpack - Jul 11",
        "from": "ref_matt@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 11, 2025
Home Team: Ice Dragons
Away Team: Wolfpack
Final Score: Ice Dragons 2 - Wolfpack 2

HOME ROSTER (Ice Dragons):
#7   Carter Novak
#11  Dylan Marsh
#18  Brett Kowalski
#23  Tom Hessler
#31  Mike Oduya
#44  Sam Firth
#55  Jake Lowen
#67  Andre Pelletier

AWAY ROSTER (Wolfpack):
#4   Owen Reid
#10  Garrett Flynn
#17  Marcus Stone
#22  Dillon Chow
#38  Scott Mercer
#45  Evan Koval
#60  Zach Bourne

PENALTIES:
- Dylan Marsh (#11, Ice Dragons) — Interference — 2 min
""",
    },
    {
        "id": "conv_005",
        "subject": "Gamesheet - Saracens vs Brawlers - Jul 12",
        "from": "ref_kira@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 12, 2025
Home Team: Saracens
Away Team: Brawlers
Final Score: Saracens 3 - Brawlers 0

HOME ROSTER (Saracens):
#3   Ryan Stokes
#9   Liam Dunn
#14  Connor Walsh
#21  Brody Chen
#29  Marcus Reeves
#35  Tyler Park
#42  Nate Finley
#50  Joel Stroud

AWAY ROSTER (Brawlers):
#6   Tyler Bass
#13  James Ortega
#20  Peter Vance
#27  Caleb Norris
#33  Shane Dumont
#41  Drew Larkin
#58  Aaron Sloane

PENALTIES:
- Marcus Reeves (#29, Saracens) — Gross Misconduct — 10 min
- Tyler Bass (#6, Brawlers) — Unsportsmanlike Conduct — 2 min
""",
    },
    {
        "id": "conv_006",
        "subject": "Gamesheet - Night Owls vs Thunderhawks - Jul 12",
        "from": "ref_sarah@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 12, 2025
Home Team: Night Owls
Away Team: Thunderhawks
Final Score: Night Owls 4 - Thunderhawks 4

HOME ROSTER (Night Owls):
#5   Cam Decker
#12  Elliot Moore
#19  Finn Gallagher
#28  Jordan Nash
#34  Sam Polley
#47  Adam Russo
#56  Kevin Park

AWAY ROSTER (Thunderhawks):
#2   Devon Kramer
#8   Logan Pierce
#15  Ben Hartley
#26  Alex Sutton
#37  Mike Cannon
#49  Will Travers
#63  Noah Blight

PENALTIES:
(none)
""",
    },
    {
        "id": "conv_007",
        "subject": "Gamesheet - Brawlers vs Ice Dragons - Jul 13",
        "from": "ref_dan@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 13, 2025
Home Team: Brawlers
Away Team: Ice Dragons
Final Score: Brawlers 6 - Ice Dragons 1

HOME ROSTER (Brawlers):
#6   Tyler Bass
#13  James Ortega
#20  Peter Vance
#27  Caleb Norris
#33  Shane Dumont
#41  Drew Larkin
#58  Aaron Sloane

AWAY ROSTER (Ice Dragons):
#7   Carter Novak
#11  Dylan Marsh
#18  Brett Kowalski
#23  Tom Hessler
#31  Mike Oduya
#44  Sam Firth
#55  Jake Lowen
#67  MYSTERY SKATER

PENALTIES:
- Shane Dumont (#33, Brawlers) — Tripping — 2 min
- Carter Novak (#7, Ice Dragons) — Slashing — 2 min
""",
    },
    {
        "id": "conv_008",
        "subject": "Gamesheet - Wolfpack vs Saracens - Jul 14",
        "from": "ref_matt@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 14, 2025
Home Team: Wolfpack
Away Team: Saracens
Final Score: Wolfpack 3 - Saracens 1

HOME ROSTER (Wolfpack):
#4   Owen Reid
#10  Garrett Flynn
#17  Marcus Stone
#22  Dillon Chow
#38  Scott Mercer
#45  Evan Koval
#60  Zach Bourne

AWAY ROSTER (Saracens):
#3   Ryan Stokes
#9   Liam Dunn
#14  Connor Walsh
#21  Brody Chen
#29  Marcus Reeves
#35  Tyler Park
#42  Nate Finley
#50  Joel Stroud

PENALTIES:
- Liam Dunn (#9, Saracens) — High Sticking — 2 min
- Owen Reid (#4, Wolfpack) — Delay of Game — 2 min
""",
    },
    {
        "id": "conv_009",
        "subject": "Gamesheet - Night Owls vs Wolfpack - Jul 14",
        "from": "ref_sarah@wrhl.ca",
        "body": """
WRHL OFFICIAL GAMESHEET
Date: July 14, 2025
Home Team: Night Owls
Away Team: Wolfpack
Final Score: Night Owls 2 - Wolfpack 5

HOME ROSTER (Night Owls):
#5   Cam Decker
#12  Elliot Moore
#19  Finn Gallagher
#28  Jordan Nash
#34  Sam Polley
#47  Adam Russo
#56  Kevin Park

AWAY ROSTER (Wolfpack):
#4   Owen Reid
#10  Garrett Flynn
#17  Marcus Stone
#22  Dillon Chow
#38  Scott Mercer
#45  Evan Koval
#60  Zach Bourne

PENALTIES:
- Finn Gallagher (#19, Night Owls) — Boarding — 2 min
- Jordan Nash (#28, Night Owls) — Fighting — 5 min
- Zach Bourne (#60, Wolfpack) — Fighting — 5 min
""",
    },
]


# ─────────────────────────────────────────────
# REGISTERED ROSTERS — ground truth for each team
# ─────────────────────────────────────────────

REGISTERED_ROSTERS = {
    "Ice Dragons": {
        7: "Carter Novak",
        11: "Dylan Marsh",
        18: "Brett Kowalski",
        23: "Tom Hessler",
        31: "Mike Oduya",
        44: "Sam Firth",
        55: "Jake Lowen",
        67: "Andre Pelletier",
    },
    "Saracens": {
        3: "Ryan Stokes",
        9: "Liam Dunn",
        14: "Connor Walsh",
        21: "Brody Chen",
        29: "Marcus Reeves",
        35: "Tyler Park",
        42: "Nate Finley",
        50: "Joel Stroud",
    },
    "Wolfpack": {
        4: "Owen Reid",
        10: "Garrett Flynn",
        17: "Marcus Stone",
        22: "Dillon Chow",
        38: "Scott Mercer",
        45: "Evan Koval",
        60: "Zach Bourne",
    },
    "Brawlers": {
        6: "Tyler Bass",
        13: "James Ortega",
        20: "Peter Vance",
        27: "Caleb Norris",
        33: "Shane Dumont",
        41: "Drew Larkin",
        58: "Aaron Sloane",
    },
    "Thunderhawks": {
        2: "Devon Kramer",
        8: "Logan Pierce",
        15: "Ben Hartley",
        26: "Alex Sutton",
        37: "Mike Cannon",
        49: "Will Travers",
        63: "Noah Blight",
    },
    "Night Owls": {
        5: "Cam Decker",
        12: "Elliot Moore",
        19: "Finn Gallagher",
        28: "Jordan Nash",
        34: "Sam Polley",
        47: "Adam Russo",
        56: "Kevin Park",
    },
}

# Players currently serving suspensions
SUSPENDED_PLAYERS = {
    "Jordan Nash",   # carried over from previous week
}

# Penalty types that trigger disciplinary review
DISCIPLINARY_PENALTIES = {
    "fighting",
    "gross misconduct",
    "game misconduct",
    "match penalty",
}


# ─────────────────────────────────────────────
# PARSER
# ─────────────────────────────────────────────

def parse_gamesheet(email):
    """
    Parse raw gamesheet text from a fake email.
    Returns a dict with structured fields.
    """
    body = email["body"]
    result = {
        "id": email["id"],
        "subject": email["subject"],
        "from": email["from"],
        "date": None,
        "home_team": None,
        "away_team": None,
        "score": None,
        "players": [],       # list of {"number": int, "name": str, "team": str}
        "penalties": [],     # list of {"name": str, "number": int, "team": str, "type": str, "minutes": int}
    }

    for line in body.splitlines():
        line = line.strip()

        m = re.match(r"Date:\s*(.+)", line)
        if m:
            result["date"] = m.group(1).strip()

        m = re.match(r"Home Team:\s*(.+)", line)
        if m:
            result["home_team"] = m.group(1).strip()

        m = re.match(r"Away Team:\s*(.+)", line)
        if m:
            result["away_team"] = m.group(1).strip()

        m = re.match(r"Final Score:\s*(.+)", line)
        if m:
            result["score"] = m.group(1).strip()

    # Parse players: lines like "#7   Carter Novak"
    current_section_team = None
    for line in body.splitlines():
        line = line.strip()
        m = re.match(r"(HOME|AWAY) ROSTER \((.+)\):", line)
        if m:
            current_section_team = m.group(2).strip()
            continue

        m = re.match(r"#(\d+)\s+(.+)", line)
        if m and current_section_team:
            number = int(m.group(1))
            name = m.group(2).strip()
            result["players"].append({
                "number": number,
                "name": name,
                "team": current_section_team,
            })

    # Parse penalties: lines like "- Connor Walsh (#14, Saracens) — Slashing — 2 min"
    for line in body.splitlines():
        line = line.strip()
        m = re.match(
            r"-\s+(.+?)\s+\(#(\d+),\s*(.+?)\)\s+[—\-]+\s+(.+?)\s+[—\-]+\s+(\d+)\s+min",
            line,
        )
        if m:
            result["penalties"].append({
                "name": m.group(1).strip(),
                "number": int(m.group(2)),
                "team": m.group(3).strip(),
                "type": m.group(4).strip(),
                "minutes": int(m.group(5)),
            })

    return result


# ─────────────────────────────────────────────
# ROSTER CHECKER
# ─────────────────────────────────────────────

def check_roster(parsed):
    """
    Compare players on the sheet against registered rosters.
    Returns lists of issues found.
    """
    issues = {
        "unregistered": [],    # players not on the official roster
        "suspended": [],       # suspended players who still played
        "number_mismatch": [], # right name, wrong number (or vice versa)
    }

    for player in parsed["players"]:
        team = player["team"]
        number = player["number"]
        name = player["name"]

        registered = REGISTERED_ROSTERS.get(team, {})

        # Skip obvious placeholder names
        if "UNKNOWN" in name.upper() or "GHOST" in name.upper() or "MYSTERY" in name.upper():
            issues["unregistered"].append(
                f"#{number} '{name}' ({team}) — placeholder name detected"
            )
            continue

        registered_name = registered.get(number)

        if registered_name is None:
            # Jersey number not on roster at all
            issues["unregistered"].append(
                f"#{number} {name} ({team}) — jersey not on roster"
            )
        elif registered_name.lower() != name.lower():
            # Number exists but name doesn't match
            issues["number_mismatch"].append(
                f"#{number} {team}: sheet says '{name}', roster says '{registered_name}'"
            )

        if name in SUSPENDED_PLAYERS:
            issues["suspended"].append(
                f"{name} ({team}) is serving a suspension"
            )

    return issues


# ─────────────────────────────────────────────
# TAGGER
# ─────────────────────────────────────────────

def assign_tag(parsed, issues):
    """
    Determine the appropriate status tag.
    Returns one of: 'gs-disciplinary', 'gs-needs-review', 'gs-verified'
    """
    # Disciplinary: fighting, gross/game misconduct
    for penalty in parsed["penalties"]:
        if penalty["type"].lower() in DISCIPLINARY_PENALTIES:
            return "gs-disciplinary"

    # Needs review: suspended players or unregistered skaters
    if issues["suspended"] or issues["unregistered"] or issues["number_mismatch"]:
        return "gs-needs-review"

    return "gs-verified"


# ─────────────────────────────────────────────
# PIPELINE RUNNER
# ─────────────────────────────────────────────

TAG_ICONS = {
    "gs-verified": "✅",
    "gs-needs-review": "⚠️ ",
    "gs-disciplinary": "🚨",
}

def run_pipeline(emails):
    results = []
    for email in emails:
        parsed = parse_gamesheet(email)
        issues = check_roster(parsed)
        tag = assign_tag(parsed, issues)
        results.append({
            "parsed": parsed,
            "issues": issues,
            "tag": tag,
        })
    return results


def print_results(results):
    divider = "─" * 60

    counts = {"gs-verified": 0, "gs-needs-review": 0, "gs-disciplinary": 0}
    for r in results:
        counts[r["tag"]] += 1

    print("\n" + "═" * 60)
    print("  WRHL GAMESHEET PROCESSOR — PIPELINE RESULTS")
    print("═" * 60)
    print(f"  Total processed : {len(results)}")
    print(f"  ✅  Verified     : {counts['gs-verified']}")
    print(f"  ⚠️   Needs Review : {counts['gs-needs-review']}")
    print(f"  🚨  Disciplinary : {counts['gs-disciplinary']}")
    print("═" * 60 + "\n")

    for r in results:
        p = r["parsed"]
        issues = r["issues"]
        tag = r["tag"]
        icon = TAG_ICONS[tag]

        print(divider)
        print(f"{icon}  [{tag}]  {p['subject']}")
        print(f"    Date  : {p['date']}")
        print(f"    Score : {p['score']}")
        print(f"    From  : {p['from']}")

        print(f"\n    Players on sheet: {len(p['players'])}")
        for pl in p["players"]:
            print(f"      #{pl['number']:>2}  {pl['name']}  ({pl['team']})")

        if p["penalties"]:
            print(f"\n    Penalties ({len(p['penalties'])}):")
            for pen in p["penalties"]:
                flag = " 🚨" if pen["type"].lower() in DISCIPLINARY_PENALTIES else ""
                print(f"      {pen['name']} ({pen['team']}) — {pen['type']} — {pen['minutes']} min{flag}")
        else:
            print("\n    Penalties: none")

        all_issues = (
            issues["unregistered"]
            + issues["suspended"]
            + issues["number_mismatch"]
        )
        if all_issues:
            print(f"\n    Issues flagged:")
            for issue in all_issues:
                print(f"      ⚠️  {issue}")
        else:
            print("\n    Issues flagged: none")

        print()

    print(divider)
    print("  Pipeline complete.\n")


if __name__ == "__main__":
    results = run_pipeline(FAKE_EMAILS)
    print_results(results)
