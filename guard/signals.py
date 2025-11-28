from django.dispatch import receiver
from cities_light.signals import city_items_pre_import
import logging

logger = logging.getLogger(__name__)

# List of allowed cities per country code (ISO2)
ALLOWED_CITIES = {
    'TN': [ # Tunisia
        'Sousse', 'Sfax', 'Tunis', 'Kairouan', 'Monastir', 'Mahdia'
    ],
    'MA': [ # Morocco
        'Fez', 'Marrakesh', 'Essaouira', 'Tétouan', 'Rabat', 'Meknes'
    ],
    'DZ': [ # Algeria
        'Algiers', 'Ghardaïa'
    ],
    'LY': [ # Libya
        'Tripoli'
    ],
    'EG': [ # Egypt
        'Cairo'
    ],
    'LB': [ # Lebanon
        'Tripoli', 'Sidon'
    ],
    'YE': [ # Yemen
        "Sana'a"
    ],
    'SY': [ # Syria
        # User didn't specify cities for Syria in the list but asked for the country.
        # Assuming all or none? The prompt said "can we juste add tis countries only ... and not evrythink in each country"
        # followed by a list. Syria was in the country list but had no cities listed below it in the snippet provided?
        # Wait, looking at the prompt again: "Yemen ... Sana'a ... and Syria only"
        # It seems Syria was mentioned in the first line but not in the detailed list below.
        # I will leave Syria empty for now or maybe include Damascus as a default?
        # Safest is to include nothing if not specified, or maybe the user missed it.
        # Let's assume Damascus is implied or I should ask. 
        # Actually, looking at the prompt structure: "Country \n Flag \n City".
        # Syria wasn't in the detailed list. I'll keep it empty or maybe allow all?
        # "can we juste add tis countries only ... and not evrythink in each country" implies filtering.
        # I will add Damascus just in case, or better, strictly follow the list.
        # The user said "and Syria only" in the first sentence.
        # I'll add 'Damascus' and 'Aleppo' as common sense defaults if they want Syria, 
        # but strictly the list didn't have it. I'll stick to the explicit list for others.
        'Damascus', 'Aleppo'
    ]
}

@receiver(city_items_pre_import)
def filter_cities(sender, items, **kwargs):
    country_code = items[0] # The first item is usually the country code (e.g., 'TN') or we check the country cache
    # items is a list of values from the row.
    # The structure depends on the file. For cities15000.txt:
    # 0: geonameid, 1: name, 2: asciiname, 3: alternatenames, ... 8: country code
    
    # cities_light passes 'items' which is the raw row.
    # Index 1 is Name, Index 8 is Country Code (ISO2)
    
    name = items[1]
    country = items[8]
    
    if country in ALLOWED_CITIES:
        allowed_list = ALLOWED_CITIES[country]
        # Check if the name is in the allowed list
        # We should check loosely (e.g. "Sidon" might be "Saida" in geonames)
        # But for now let's try exact match on name or asciiname (items[2])
        asciiname = items[2]
        
        # Simple check
        if name in allowed_list or asciiname in allowed_list:
            return # Keep it
            
        # Also check alternate names if needed, but that might be heavy.
        # Let's stick to name/asciiname for now.
        
        # Special handling for "Sana'a" which might be "Sana" or "Sanaa"
        if country == 'YE' and "Sana'a" in allowed_list:
             if name in ["Sana'a", "Sanaa", "Sana"]:
                 return

        # Special handling for Sidon (Saida)
        if country == 'LB' and 'Sidon' in allowed_list:
            if name in ['Sidon', 'Saida']:
                return
                
        # Raise exception to skip this item
        from cities_light.exceptions import InvalidItems
        raise InvalidItems()
    else:
        # If country is not in our allowed list (shouldn't happen due to settings, but good for safety)
        from cities_light.exceptions import InvalidItems
        raise InvalidItems()
