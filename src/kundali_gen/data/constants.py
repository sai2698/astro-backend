"""
Core astronomical constants: Nakshatras, Signs, Planets, Karakas, Avasthas, etc.
"""

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
SIGN_SHORT = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir", "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]

PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
PLANET_SHORT = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]

NAKSHATRAS = [
    {"name": "Ashwini",       "lord": "Ketu",    "deity": "Ashwins"},
    {"name": "Bharani",       "lord": "Venus",   "deity": "Yama"},
    {"name": "Krittika",      "lord": "Sun",     "deity": "Agni"},
    {"name": "Rohini",        "lord": "Moon",    "deity": "Brahma"},
    {"name": "Mrigashira",    "lord": "Mars",    "deity": "Soma"},
    {"name": "Ardra",         "lord": "Rahu",    "deity": "Rudra"},
    {"name": "Punarvasu",     "lord": "Jupiter", "deity": "Aditi"},
    {"name": "Pushya",        "lord": "Saturn",  "deity": "Brihaspati"},
    {"name": "Ashlesha",      "lord": "Mercury", "deity": "Nagas"},
    {"name": "Magha",         "lord": "Ketu",    "deity": "Pitrs"},
    {"name": "Purva Phalguni","lord": "Venus",   "deity": "Bhaga"},
    {"name": "Uttara Phalguni","lord": "Sun",    "deity": "Aryaman"},
    {"name": "Hasta",         "lord": "Moon",    "deity": "Savitar"},
    {"name": "Chitra",        "lord": "Mars",    "deity": "Tvashtr"},
    {"name": "Swati",         "lord": "Rahu",    "deity": "Vayu"},
    {"name": "Vishakha",      "lord": "Jupiter", "deity": "Indra-Agni"},
    {"name": "Anuradha",      "lord": "Saturn",  "deity": "Mitra"},
    {"name": "Jyeshtha",      "lord": "Mercury", "deity": "Indra"},
    {"name": "Mula",          "lord": "Ketu",    "deity": "Nirrti"},
    {"name": "Purva Ashadha", "lord": "Venus",   "deity": "Apas"},
    {"name": "Uttara Ashadha","lord": "Sun",     "deity": "Vishvedevas"},
    {"name": "Shravana",      "lord": "Moon",    "deity": "Vishnu"},
    {"name": "Dhanishtha",    "lord": "Mars",    "deity": "Eight Vasus"},
    {"name": "Shatabhisha",   "lord": "Rahu",    "deity": "Varuna"},
    {"name": "Purva Bhadrapada","lord": "Jupiter","deity": "Ajaikapad"},
    {"name": "Uttara Bhadrapada","lord": "Saturn","deity": "Ahirbudhnya"},
    {"name": "Revati",        "lord": "Mercury", "deity": "Pushan"},
]

# Nakshatra navamsha sign for each pada (4 padas per nakshatra, 108 total)
# Starting from Aries for Ashwini pada 1, cycling through 12 signs
def get_nakshatra_navamsha(nak_idx, pada):
    """Returns navamsha sign index (0-based) for a given nakshatra (0-based) and pada (1-4)."""
    total_pada = nak_idx * 4 + (pada - 1)
    return total_pada % 12

# Vimshottari dasha years for each planet
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10,
    "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}
DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_TOTAL = 120  # Sum of all dasha years

# Map nakshatra index to dasha lord
NAKSHATRA_DASHA_LORD = [
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",  # 0-8
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",  # 9-17
    "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",  # 18-26
]

# Sign lords
SIGN_LORD = ["Mars","Venus","Mercury","Moon","Sun","Mercury","Venus","Mars","Jupiter","Saturn","Saturn","Jupiter"]

# Exaltation and debilitation
EXALTATION = {"Sun":0,"Moon":1,"Mars":9,"Mercury":5,"Jupiter":3,"Venus":11,"Saturn":6}  # sign idx
DEBILITATION = {"Sun":6,"Moon":7,"Mars":3,"Mercury":11,"Jupiter":9,"Venus":5,"Saturn":0}

# Own signs
OWN_SIGNS = {
    "Sun":[4], "Moon":[3], "Mars":[0,7], "Mercury":[2,5],
    "Jupiter":[8,11], "Venus":[1,6], "Saturn":[9,10]
}

# Moola trikona signs
MOOLATRIKONA = {
    "Sun":4, "Moon":1, "Mars":0, "Mercury":5, "Jupiter":8, "Venus":6, "Saturn":10
}

# Natural friendships (Naisargika Maitri)
# 0=Enemy, 1=Neutral, 2=Friend
NATURAL_RELATIONS = {
    "Sun":    {"Moon":2,"Mars":2,"Mercury":1,"Jupiter":2,"Venus":0,"Saturn":0,"Rahu":0,"Ketu":0},
    "Moon":   {"Sun":2,"Mars":1,"Mercury":2,"Jupiter":1,"Venus":1,"Saturn":1,"Rahu":0,"Ketu":0},
    "Mars":   {"Sun":2,"Moon":2,"Mercury":1,"Jupiter":2,"Venus":1,"Saturn":1,"Rahu":1,"Ketu":2},
    "Mercury":{"Sun":2,"Moon":0,"Mars":1,"Jupiter":1,"Venus":2,"Saturn":1,"Rahu":1,"Ketu":1},
    "Jupiter":{"Sun":2,"Moon":2,"Mars":2,"Mercury":1,"Venus":1,"Saturn":1,"Rahu":0,"Ketu":0},
    "Venus":  {"Sun":0,"Moon":0,"Mars":1,"Mercury":2,"Jupiter":1,"Saturn":2,"Rahu":2,"Ketu":2},
    "Saturn": {"Sun":0,"Moon":0,"Mars":0,"Mercury":2,"Jupiter":1,"Venus":2,"Rahu":2,"Ketu":0},
    "Rahu":   {"Sun":0,"Moon":0,"Mars":1,"Mercury":1,"Jupiter":2,"Venus":2,"Saturn":2,"Ketu":0},
    "Ketu":   {"Sun":0,"Moon":2,"Mars":2,"Mercury":1,"Jupiter":1,"Venus":2,"Saturn":0,"Rahu":0},
}

# Avasthas rules (simplified by sign relationship)
AVASTHA_NAMES = ["Bala (Strength)", "Kumara (Youth)", "Yuva (Adult)", "Vriddha (Old)", "Mrita (Dead)"]

def get_avastha(planet, sign_idx):
    """Determine planetary avastha based on sign position."""
    lords = {"Aries":0,"Taurus":1,"Gemini":2,"Cancer":3,"Leo":4,"Virgo":5,
             "Libra":6,"Scorpio":7,"Sagittarius":8,"Capricorn":9,"Aquarius":10,"Pisces":11}
    sign_name = SIGNS[sign_idx]
    # Exaltation/own = Bala, friendly = Kumara, neutral = Yuva, enemy = Vriddha, debilitation = Mrita
    if sign_idx == EXALTATION.get(planet, -1):
        return "Bala (Strength)"
    if sign_idx == DEBILITATION.get(planet, -1):
        return "Mrita (Dead)"
    if sign_idx in OWN_SIGNS.get(planet, []):
        return "Bala (Strength)"
    sign_lord = SIGN_LORD[sign_idx]
    rel = NATURAL_RELATIONS.get(planet, {}).get(sign_lord, 1)
    if rel == 2:
        return "Kumara (Youth)"
    elif rel == 0:
        return "Vriddha (Old)"
    return "Yuva (Adult)"

# Swabhava (nature) by sign type
def get_swabhava(sign_idx):
    # Sthira (Fixed): Taurus, Leo, Scorpio, Aquarius
    # Dwi (Dual): Gemini, Virgo, Sag, Pisces
    # Chara (Movable): Aries, Cancer, Libra, Capricorn
    fixed = [1, 4, 7, 10]
    dual = [2, 5, 8, 11]
    if sign_idx in fixed: return "Sthira"
    if sign_idx in dual: return "Dwi"
    return "Chara"

# Tatwa (element) by sign
def get_tatwa(sign_idx):
    fire = [0, 4, 8]
    earth = [1, 5, 9]
    air = [2, 6, 10]
    water = [3, 7, 11]
    if sign_idx in fire: return "Agni"
    if sign_idx in earth: return "Prithvi"
    if sign_idx in air: return "Vayu"
    return "Jala"

# Planet gender
PLANET_GENDER = {
    "Sun": "Male", "Moon": "Male", "Mars": "Male", "Mercury": "Male",
    "Jupiter": "Male", "Venus": "Female", "Saturn": "Female",
    "Rahu": "Male", "Ketu": "Male"
}

# Nakshatra attributes
NAKSHATRA_NADI = ["Vata","Pitta","Kapha"] * 9  # cycles through 27
NAKSHATRA_GANA = [
    "Deva","Manushya","Rakshasa","Deva","Deva","Manushya","Deva","Deva","Rakshasa",
    "Rakshasa","Manushya","Manushya","Deva","Rakshasa","Deva","Rakshasa","Deva","Rakshasa",
    "Rakshasa","Manushya","Manushya","Deva","Rakshasa","Deva","Manushya","Manushya","Deva"
]
NAKSHATRA_YONI = [
    "Horse","Elephant","Goat","Serpent","Serpent","Dog","Cat","Goat","Cat",
    "Rat","Rat","Cow","Buffalo","Tiger","Buffalo","Tiger","Deer","Deer","Dog",
    "Monkey","Mongoose","Monkey","Lion","Horse","Lion","Cow","Elephant"
]
NAKSHATRA_NADI_NAME = [
    "Vata","Pitta","Kapha","Vata","Pitta","Kapha","Vata","Pitta","Kapha",
    "Vata","Pitta","Kapha","Vata","Pitta","Kapha","Vata","Pitta","Kapha",
    "Vata","Pitta","Kapha","Vata","Pitta","Kapha","Vata","Pitta","Kapha",
]
NAKSHATRA_NADI_LABEL = {
    "Vata":"Antya","Pitta":"Madhya","Kapha":"Adya"
}

# Varna by sign (for Varna Kuta in matching)
VARNA = ["Brahmin","Kshatriya","Vaishya","Shudra"] * 3
SIGN_VARNA = {
    0:"Vaishya",1:"Shudra",2:"Shudra",3:"Brahmin",4:"Kshatriya",5:"Vaishya",
    6:"Shudra",7:"Brahmin",8:"Kshatriya",9:"Vaishya",10:"Shudra",11:"Brahmin"
}
SIGN_VASHYA = {
    0:"Chatushpada",1:"Chatushpada",2:"Manava",3:"Jalachara",4:"Vanachara",5:"Keet",
    6:"Manava",7:"Keet",8:"Manava",9:"Chatushpada",10:"Manava",11:"Jalachara"
}

# Bhava names
BHAVA_NAMES = [
    "Lagna Bhava","Dhana Bhava","Bhratru Bhava","Matru Bhava",
    "Putra Bhava","Shatru Bhava","Kalatra Bhava","Ayu Bhava",
    "Bhagya Bhava","Rajya Bhava","Labha Bhava","Vyaya Bhava"
]
BHAVA_MEANINGS = [
    "Overall life, health","Finance & Family","Siblings, short journeys",
    "Mother, Education, Vehicles","Knowledge, Children, Love","Health & Enemies",
    "Marriage & Business","Longevity & Accidents","Father & Fortune",
    "Career, Name, Fame","Gains & Friends","Expenditure & Foreign Travel"
]

# Tithi names
TITHI_NAMES = [
    "Pratipad","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami",
    "Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi",
    "Purnima/Amavasya"
]
PAKSHA = ["Shukla","Krishna"]

# Yoga names
YOGA_NAMES = [
    "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma",
    "Dhriti","Shula","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
    "Siddhi","Vyatipata","Variyan","Parigha","Shiva","Siddha","Sadhya","Shubha",
    "Shukla","Brahma","Indra","Vaidhriti"
]

# Karana names
KARANA_NAMES = [
    "Kimstughna","Bava","Balava","Kaulava","Taitula","Gara","Vanija",
    "Vishti","Shakuni","Chatushpada","Naga"
]

# Hindu months
HINDU_MONTHS = [
    "Chaitra","Vaishakha","Jyeshtha","Ashadha","Shravana","Bhadrapada",
    "Ashwina","Kartika","Margashirsha","Pausha","Magha","Phalguna"
]

# Ayana
AYANA = ["Uttarayana","Dakshinayana"]

# Ritu (Season)
RITU_NAMES = [
    "Vasanta Ritu","Grishma Ritu","Varsha Ritu","Sharad Ritu","Hemanta Ritu","Shishira Ritu"
]

# Hindu year names (60-year cycle - Jovian years)
HINDU_YEAR_NAMES = [
    "Prabhava","Vibhava","Shukla","Pramoda","Prajapati","Angiras","Shrimukha","Bhava",
    "Yuva","Dhata","Ishvara","Bahudhanya","Pramathi","Vikrama","Vrishabha","Chitrabhanu",
    "Svabhanu","Tarana","Parthiva","Vyaya","Sarvajit","Sarvadhari","Virodhi","Vikrita",
    "Khara","Nandana","Vijaya","Jaya","Manmatha","Durmukhi","Hevilambi","Vilambi",
    "Vikari","Sharvari","Plava","Shubhakrit","Shobhana","Krodhi","Vishvavasu","Parabhava",
    "Plavanga","Kilaka","Saumya","Sadharana","Virodhakrit","Paridhavi","Pramadi","Ananda",
    "Rakshasa","Nala","Pingala","Kalayukti","Siddharthi","Raudra","Durmati","Dundubhi",
    "Rudhirodgari","Raktakshi","Krodhana","Akshaya"
]

# Jaimini Karakas (Chara - based on degrees in sign, descending order)
CHARA_KARAKAS = [
    "Atmakaraka","Amatyakaraka","Bhratrukaraka","Matrukaraka",
    "Putrakaraka","Gnatikaraka","Darakaraka"
]
STHIRA_KARAKAS = {
    "Sun": "Atma Karaka", "Moon": "Matru Karaka", "Mars": "Bhratru Karaka",
    "Mercury": "Gnyati Karaka", "Jupiter": "Putra Karaka", "Venus": "Dara Karaka",
    "Saturn": "Ayu Karaka", "Rahu": "Matru Karaka (alt)"
}

# Lucky things by Lagna sign index (0=Aries ... 11=Pisces)
LUCKY_THINGS = {
    10: {  # Aquarius
        "days": ["Friday", "Saturday", "Tuesday"],
        "planets": ["Venus", "Saturn", "Mars"],
        "friendly_signs": ["Libra", "Gemini"],
        "friendly_asc": ["Libra", "Sagittarius"],
        "life_stone": "Blue Sapphire",
        "lucky_stone": "Diamond",
        "punya_stone": "Emerald",
        "deity": ["Lord Venkateswara", "Lord Subrahmanya", "Goddess Lakshmi"],
        "metal": "Gold",
        "color": ["Blue", "Red", "Green"],
        "direction": ["South", "Northeast"],
        "time": "Evening",
        "numbers": ["3", "6", "9"],
    },
    0: {  # Aries
        "days": ["Tuesday", "Sunday"],
        "planets": ["Mars", "Sun", "Jupiter"],
        "friendly_signs": ["Leo", "Sagittarius"],
        "friendly_asc": ["Leo", "Scorpio"],
        "life_stone": "Red Coral",
        "lucky_stone": "Ruby",
        "punya_stone": "Yellow Sapphire",
        "deity": ["Lord Subrahmanya", "Lord Hanuman"],
        "metal": "Copper",
        "color": ["Red", "Orange"],
        "direction": ["East", "South"],
        "time": "Morning",
        "numbers": ["1", "3", "9"],
    },
    # Add other lagnas similarly; fallback below
}

def get_lucky_things(lagna_sign_idx):
    return LUCKY_THINGS.get(lagna_sign_idx, LUCKY_THINGS.get(10, {}))

# Aspect rules for Vedic astrology (1-indexed houses from planet position)
# All planets aspect 7th. Mars also 4th, 8th. Jupiter also 5th, 9th. Saturn also 3rd, 10th. Rahu/Ketu also 5th, 9th.
EXTRA_ASPECTS = {
    "Mars": [4, 8],
    "Jupiter": [5, 9],
    "Saturn": [3, 10],
    "Rahu": [5, 9],
    "Ketu": [5, 9],
}

# Upagraha calculation constants (fractional day multiples of arc)
# These are calculated from sunrise time

# Combust degrees (planet within this distance from Sun = combust)
COMBUST_DEGREES = {
    "Moon": 12, "Mars": 17, "Mercury": 14, "Jupiter": 11, "Venus": 10, "Saturn": 15
}
