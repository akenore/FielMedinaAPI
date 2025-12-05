from django.dispatch import receiver
from cities_light.signals import city_items_pre_import
import logging

logger = logging.getLogger(__name__)

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
        'Damascus', 'Aleppo'
    ]
}

@receiver(city_items_pre_import)
def filter_cities(sender, items, **kwargs):
    country_code = items[0] 
    
    name = items[1]
    country = items[8]
    
    if country in ALLOWED_CITIES:
        allowed_list = ALLOWED_CITIES[country]
        asciiname = items[2]
        
        if name in allowed_list or asciiname in allowed_list:
            return # Keep it
        
        if country == 'YE' and "Sana'a" in allowed_list:
             if name in ["Sana'a", "Sanaa", "Sana"]:
                 return

        if country == 'LB' and 'Sidon' in allowed_list:
            if name in ['Sidon', 'Saida']:
                return
                
        from cities_light.exceptions import InvalidItems
        raise InvalidItems()
    else:
        from cities_light.exceptions import InvalidItems
        raise InvalidItems()
