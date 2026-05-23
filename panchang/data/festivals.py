"""
Indian Festivals Database - Lunar and Gregorian festivals with all sources.

Festival types:
1. Lunar festivals: Matched by (Paksha, Tithi, Masa)
2. Fixed Gregorian: Matched by (Month, Day)

Each festival has (English name, Telugu name) tuple.
"""

# Lunar-based festivals (Tithi + Masa + Paksha)
LUNAR_FESTIVALS = {
    ("Shukla", "Pratipada", "Chaitra"): ("Ugadi / Gudi Padwa (Hindu New Year)", "ఉగాది / గుడీ పడ్వ (హిందూ నববర్ష)"),
    ("Shukla", "Navami", "Chaitra"): ("Rama Navami (Birth of Lord Rama)", "రామ నవమి (రాముని జన్మ)"),
    ("Shukla", "Purnima", "Vaishakha"): ("Buddha Purnima / Buddha Jayanti", "బుద్ధ పూర్ణిమ"),
    ("Krishna", "Ashtami", "Bhadrapada"): ("Janmashtami (Birth of Lord Krishna)", "జన్మాష్టమి (కృష్ణుని జన్మ)"),
    ("Shukla", "Chaturthi", "Bhadrapada"): ("Ganesh Chaturthi (Birth of Ganesha)", "గణేష చతుర్థి (గణేశుని జన్మ)"),
    ("Shukla", "Purnima", "Phalguna"): ("Holi (Festival of Colors)", "హోలీ (రంగుల పండుగ)"),
    ("Krishna", "Chaturdashi", "Phalguna"): ("Maha Shivaratri (Night of Shiva)", "మహా శివరాత్రి (శివుని రాత్రి)"),
    ("Shukla", "Purnima", "Shravan"): ("Raksha Bandhan (Sister-Brother Bond)", "రక్ష బందన (సోదరుల బంధం)"),
    ("Shukla", "Panchami", "Shravan"): ("Nag Panchami (Snake Worship)", "నాగ పంచమి (నాగ పూజ)"),
    ("Krishna", "Amavasya", "Kartik"): ("Diwali (Festival of Lights) 🪔", "దీపావళి (కాంతుల పండుగ) 🪔"),
    ("Shukla", "Pratipada", "Kartik"): ("Govardhan Puja (Day after Diwali)", "గోవర్థన పూజ (దీపావళికే రోజు)"),
    ("Shukla", "Dwadashi", "Kartik"): ("Bhai Dooj (Brother-Sister Bond)", "భాయ్య దూజ (సోదరుల ప్రేమ)"),
    ("Shukla", "Purnima", "Kartik"): ("Kartik Purnima", "కార్తిక పూర్ణిమ"),
    ("Krishna", "Panchami", "Chaitra"): ("Naag Panchami", "నాగ పంచమి"),
}

# Fixed Gregorian date festivals (Month, Day)
FIXED_GREGORIAN_FESTIVALS = {
    (1, 14): ("Makar Sankranti (Sun enters Capricorn, Harvest Festival)", "మకర సంక్రాంతి (ఫసల్ పండుగ)"),
    (1, 15): ("Pongal (Harvest Festival - South India)", "పొంగల్ (దక్షిణ భారతీయ ఫసల్ పండుగ)"),
    (1, 26): ("Republic Day (National Holiday) 🇮🇳", "రిపబ్లిక్ దినం (జాతీయ విషయం) 🇮🇳"),
    (8, 15): ("Independence Day (National Holiday) 🇮🇳", "స్వాతంత్ర్య దినం (జాతీయ విषయం) 🇮🇳"),
    (10, 2): ("Gandhi Jayanti (National Holiday)", "గాంధీ జయంతి (జాతీయ విషయం)"),
    (12, 25): ("Christmas", "క్రిస్మస్"),
}


def get_todays_festival(gregorian_date, tithi_name, masa_name, paksha_name):
    """
    Get festival for today combining lunar and Gregorian checks.
    
    Args:
        gregorian_date: datetime.date object
        tithi_name: String like "Ashtami", "Purnima"
        masa_name: String like "Kartik", "Chaitra"
        paksha_name: "Shukla" or "Krishna"
    
    Returns:
        Tuple of (festival_name_en, festival_name_te) or (None, None) if no festival.
    """
    # Check lunar festival (priority over Gregorian)
    key = (paksha_name, tithi_name, masa_name)
    if key in LUNAR_FESTIVALS:
        return LUNAR_FESTIVALS[key]
    
    # Check Gregorian festivals
    greg_key = (gregorian_date.month, gregorian_date.day)
    if greg_key in FIXED_GREGORIAN_FESTIVALS:
        return FIXED_GREGORIAN_FESTIVALS[greg_key]
    
    return (None, None)
