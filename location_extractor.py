import spacy
import re


# ---------------- LOAD NLP MODEL ----------------

nlp = spacy.load("en_core_web_sm")


# ---------------- INDIAN STATES ----------------

INDIAN_STATES = [

    "andhra pradesh",
    "arunachal pradesh",
    "assam",
    "bihar",
    "chhattisgarh",
    "goa",
    "gujarat",
    "haryana",
    "himachal pradesh",
    "jharkhand",
    "karnataka",
    "kerala",
    "madhya pradesh",
    "maharashtra",
    "manipur",
    "meghalaya",
    "mizoram",
    "nagaland",
    "odisha",
    "punjab",
    "rajasthan",
    "sikkim",
    "tamil nadu",
    "telangana",
    "tripura",
    "uttar pradesh",
    "uttarakhand",
    "west bengal",
    "delhi",
    "jammu and kashmir",
    "ladakh",
    "puducherry",
    "chandigarh",
    "andaman and nicobar islands",
    "dadra and nagar haveli and daman and diu",
    "lakshadweep"
]


# ---------------- BAD LOCATIONS ----------------

BAD_LOCATIONS = [

    "ai",
    "ml",
    "ngo",
    "foundation",
    "news",
    "sporting",
    "media",
    "team",
    "project",
    "initiative",
    "education",
    "health",
    "women",
    "indiaisus",
    "webpulse",
    "ddindia",
    "unhrc-dd",
    "snehalaya",

    # junk website entities
    "internships",
    "internship",
    "career",
    "jobs",
    "contact",
    "about",
    "privacy",
    "cookies",
    "login",
    "signup",

    # noisy geography
    "london",
    "unitedkingdom",
    "united kingdom",
    "uk"
]


# ---------------- PRIORITY LOCATIONS ----------------

PRIORITY_LOCATIONS = [

    "india",
    "delhi",
    "assam",
    "karnataka",
    "maharashtra",
    "uttar pradesh",
    "odisha",
    "haryana",
    "goa"
]


# ---------------- NORMALIZATION ----------------

LOCATION_NORMALIZATION = {

    "newdelhi": "New Delhi",

    "southdelhi": "South Delhi",

    "southdelhi-": "South Delhi",

    "new delhi": "New Delhi",

    "uttarpradesh": "Uttar Pradesh",

    "madhyapradesh": "Madhya Pradesh"
}


# ---------------- CLEAN LOCATION ----------------

def clean_location(text):

    text = text.strip()

    # remove special chars
    text = re.sub(
        r'[^a-zA-Z\s-]',
        '',
        text
    )

    # remove repeated spaces
    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    return text.strip()


# ---------------- VALIDATE LOCATION ----------------

def is_valid_location(location):

    location_lower = location.lower()

    # reject tiny/noisy text
    if len(location_lower) < 3:

        return False

    # reject numbers
    if location_lower.isdigit():

        return False

    # reject bad entities
    if location_lower in BAD_LOCATIONS:

        return False

    return True


# ---------------- NORMALIZE LOCATION ----------------

def normalize_location(location):

    location_lower = location.lower()

    # remove spaces for matching
    compact = location_lower.replace(
        " ",
        ""
    )

    if compact in LOCATION_NORMALIZATION:

        return LOCATION_NORMALIZATION[
            compact
        ]

    return location.title()


# ---------------- EXTRACT LOCATIONS ----------------

def extract_locations(text):

    doc = nlp(text)

    locations = set()

    # ---------------- SPACY ENTITIES ----------------

    for ent in doc.ents:

        if ent.label_ in ["GPE", "LOC"]:

            cleaned = clean_location(
                ent.text
            )

            if not is_valid_location(
                cleaned
            ):

                continue

            normalized = normalize_location(
                cleaned
            )

            locations.add(normalized)

    # ---------------- INDIAN STATE MATCHING ----------------

    lower_text = text.lower()

    for state in INDIAN_STATES:

        if state in lower_text:

            locations.add(
                state.title()
            )

    # ---------------- FINAL CLEANUP ----------------

    final_locations = []

    seen = set()

    for loc in locations:

        loc_clean = loc.strip()

        if (
            loc_clean and
            loc_clean.lower() not in seen
        ):

            final_locations.append(
                loc_clean
            )

            seen.add(
                loc_clean.lower()
            )

    # ---------------- PRIORITIZE INDIA ----------------

    priority = []

    others = []

    for loc in final_locations:

        if loc.lower() in PRIORITY_LOCATIONS:

            priority.append(loc)

        else:

            others.append(loc)

    return sorted(priority) + sorted(others)


# ---------------- TEST ----------------

if __name__ == "__main__":

    text = '''

    AI-driven women empowerment initiative
    working across Delhi, Assam,
    rural Karnataka, and Uttar Pradesh.

    '''

    locations = extract_locations(text)

    print(locations)