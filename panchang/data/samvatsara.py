"""
60-year Jovian (Brihaspati) cycle — Samvatsara names.

Index 0 = Prabhava (first in the cycle).
The current Samvatsara is computed in calculations.py via Jupiter's sidereal
longitude and is looked up here by (shaka_year % 60).
"""

# Each entry: (english_name, telugu_name)
SAMVATSARA: list[tuple[str, str]] = [
    ("Prabhava",        "ప్రభవ"),        # 0
    ("Vibhava",         "విభవ"),          # 1
    ("Shukla",          "శుక్ల"),          # 2
    ("Pramoda",         "ప్రమోద"),        # 3
    ("Prajapati",       "ప్రజాపతి"),      # 4
    ("Angirasa",        "అంగీరస"),        # 5
    ("Shrimukha",       "శ్రీముఖ"),       # 6
    ("Bhava",           "భావ"),            # 7
    ("Yuva",            "యువ"),            # 8
    ("Dhatu",           "ధాతు"),           # 9
    ("Ishvara",         "ఈశ్వర"),         # 10
    ("Bahudhanya",      "బహుధాన్య"),      # 11
    ("Pramadi",         "ప్రమాది"),       # 12
    ("Vikrama",         "విక్రమ"),         # 13
    ("Vrisha",          "వృష"),            # 14
    ("Chitrabhanu",     "చిత్రభాను"),     # 15
    ("Svabhanu",        "స్వభాను"),       # 16
    ("Tarana",          "తారణ"),           # 17
    ("Parthiva",        "పార్థివ"),        # 18
    ("Vyaya",           "వ్యయ"),           # 19
    ("Sarvajit",        "సర్వజిత్"),      # 20
    ("Sarvadharin",     "సర్వధారి"),      # 21
    ("Virodhi",         "విరోధి"),         # 22
    ("Vikrita",         "వికృతి"),         # 23
    ("Khara",           "ఖర"),             # 24
    ("Nandana",         "నందన"),           # 25
    ("Vijaya",          "విజయ"),           # 26
    ("Jaya",            "జయ"),             # 27
    ("Manmatha",        "మన్మథ"),         # 28
    ("Durmukhi",        "దుర్ముఖి"),      # 29
    ("Hevilambi",       "హేవిళంబి"),      # 30
    ("Vilambi",         "విళంబి"),         # 31
    ("Vikari",          "వికారి"),         # 32
    ("Sharvari",        "శార్వరి"),        # 33
    ("Plava",           "ప్లవ"),           # 34
    ("Shubhakrit",      "శుభకృత్"),       # 35
    ("Shobhana",        "శోభన"),           # 36
    ("Krodhi",          "క్రోధి"),         # 37
    ("Vishvavasu",      "విశ్వావసు"),     # 38
    ("Parabhava",       "పరాభవ"),          # 39
    ("Plavanga",        "ప్లవంగ"),         # 40
    ("Kilaka",          "కీలక"),           # 41
    ("Saumya",          "సౌమ్య"),         # 42
    ("Sadharana",       "సాధారణ"),         # 43
    ("Virodhikrit",     "విరోధికృత్"),    # 44
    ("Paridhavi",       "పరిధావి"),        # 45
    ("Pramadicha",      "ప్రమాదీచ"),      # 46
    ("Ananda",          "ఆనంద"),           # 47
    ("Rakshasa",        "రాక్షస"),         # 48
    ("Nala",            "నల"),             # 49
    ("Pingala",         "పింగళ"),          # 50
    ("Kalayukta",       "కాళయుక్త"),      # 51
    ("Siddharthi",      "సిద్ధార్థి"),    # 52
    ("Raudra",          "రౌద్ర"),          # 53
    ("Durmati",         "దుర్మతి"),        # 54
    ("Dundubhi",        "దుందుభి"),        # 55
    ("Rudhirodgari",    "రుధిరోద్గారి"),  # 56
    ("Raktakshi",       "రక్తాక్షి"),     # 57
    ("Krodhana",        "క్రోధన"),         # 58
    ("Akshaya",         "అక్షయ"),          # 59
]


def get_samvatsara(shaka_year: int) -> tuple[str, str]:
    """Return (english, telugu) Samvatsara name for a given Shaka year."""
    return SAMVATSARA[shaka_year % 60]
