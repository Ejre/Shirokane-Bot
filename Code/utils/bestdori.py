import requests
import time
import random

# Bestdori API Endpoints
API_EVENTS = "https://bestdori.com/api/events/all.5.json"
API_CARDS = "https://bestdori.com/api/cards/all.5.json"
API_GACHA = "https://bestdori.com/api/gacha/all.5.json"

# Asset URLs
ASSET_JP_EVENT = "https://bestdori.com/assets/jp/event/{}/images_rip/banner.png"
ASSET_JP_CARD = "https://bestdori.com/assets/jp/characters/resourceset/{}_rip/card_after_training.png"
ASSET_JP_CARD_NORMAL = "https://bestdori.com/assets/jp/characters/resourceset/{}_rip/card_normal.png"

def get_jp_event():
    """
    Fetches the currently active or next event for JP Server (Server 0).
    Returns a dict with event info and image URL, or None if error.
    """
    try:
        response = requests.get(API_EVENTS)
        if response.status_code != 200:
            return None
        
        events = response.json()
        current_time = int(time.time() * 1000)
        
        # Iterate to find current event
        for event_id, event_data in events.items():
            # Server 0 is JP. startAt and endAt are lists indexed by server ID.
            if not event_data.get("startAt") or len(event_data["startAt"]) < 1:
                continue
                
            start = int(event_data["startAt"][0]) if event_data["startAt"][0] else 0
            end = int(event_data["endAt"][0]) if event_data["endAt"][0] else 0
            
            if start <= current_time <= end:
                # Found active event
                event_name = event_data["eventName"][0] if event_data.get("eventName") else "Unknown Event"
                asset_bundle = event_data.get("assetBundleName")
                banner_url = ASSET_JP_EVENT.format(asset_bundle) if asset_bundle else None
                
                return {
                    "name": event_name,
                    "end_time": end,
                    "image": banner_url,
                    "status": "Active"
                }
        
        # If no active event, look for next upcoming
        upcoming_events = []
        for event_id, event_data in events.items():
             if not event_data.get("startAt") or len(event_data["startAt"]) < 1:
                continue
             start = int(event_data["startAt"][0]) if event_data["startAt"][0] else 0
             if start > current_time:
                 upcoming_events.append((start, event_data))
        
        if upcoming_events:
            # Sort by start time
            upcoming_events.sort(key=lambda x: x[0])
            next_event = upcoming_events[0][1]
            event_name = next_event["eventName"][0] if next_event.get("eventName") else "Unknown Event"
            asset_bundle = next_event.get("assetBundleName")
            banner_url = ASSET_JP_EVENT.format(asset_bundle) if asset_bundle else None
            
            return {
                "name": event_name,
                "start_time": upcoming_events[0][0],
                "image": banner_url,
                "status": "Upcoming"
            }

        return None

    except Exception as e:
        print(f"[Bestdori Error] get_jp_event: {e}")
        return None

# Character ID Mapping
CHARACTER_MAP = {
    "kasumi": 1, "tae": 2, "rimi": 3, "saaya": 4, "arisa": 5, # Poppin'Party
    "ran": 6, "moca": 7, "himari": 8, "tomoe": 9, "tsugumi": 10, # Afterglow
    "kokoro": 11, "kaoru": 12, "hagumi": 13, "kanon": 14, "misaki": 15, # HHW
    "aya": 16, "hina": 17, "chisato": 18, "maya": 19, "eve": 20, # Pastel*Palettes
    "yukina": 21, "sayo": 22, "lisa": 23, "ako": 24, "rinko": 25, # Roselia
    "mashiro": 26, "touko": 27, "nanami": 28, "tsukushi": 29, "rui": 30, # Morfonica
    "layer": 31, "lock": 32, "masking": 33, "pareo": 34, "chu2": 35, # RAS
    "rei": 31, "roku": 32, "masuki": 33, "chiyuri": 35 # RAS Alternate names
}

# Band → Member Mapping
# Allows queries like "kartu roselia limited" to correctly target Roselia members
BAND_MAP = {
    "poppinparty": ["kasumi", "tae", "rimi", "saaya", "arisa"],
    "poppin party": ["kasumi", "tae", "rimi", "saaya", "arisa"],
    "popipa": ["kasumi", "tae", "rimi", "saaya", "arisa"],
    "afterglow": ["ran", "moca", "himari", "tomoe", "tsugumi"],
    "afterguro": ["ran", "moca", "himari", "tomoe", "tsugumi"],
    "hellohappyworld": ["kokoro", "kaoru", "hagumi", "kanon", "misaki"],
    "hello happy world": ["kokoro", "kaoru", "hagumi", "kanon", "misaki"],
    "hhw": ["kokoro", "kaoru", "hagumi", "kanon", "misaki"],
    "pastelpalettes": ["aya", "hina", "chisato", "maya", "eve"],
    "pastel palettes": ["aya", "hina", "chisato", "maya", "eve"],
    "pasupare": ["aya", "hina", "chisato", "maya", "eve"],
    "roselia": ["yukina", "sayo", "lisa", "ako", "rinko"],
    "morfonica": ["mashiro", "touko", "nanami", "tsukushi", "rui"],
    "morphonica": ["mashiro", "touko", "nanami", "tsukushi", "rui"],
    "ras": ["layer", "lock", "masking", "pareo", "chu2"],
    "raise a suilen": ["layer", "lock", "masking", "pareo", "chu2"],
    "mygo": ["tomori", "anon", "soyo", "taki", "raana"],
    "ave mujica": ["mortis", "oblivionis", "timoris", "doloris", "pectus"],
}

def get_character_cards(character_name, limit=1, card_type_filter=None, rarity_filter=None):
    """
    Fetches cards for a specific character with optional type and rarity filtering.
    Args:
        character_name (str): Name of the character (e.g., "yukina", "rinko").
        limit (int): Number of cards to return.
        card_type_filter (str): Specific card type to filter (e.g., "dream_fes", "kirafes", "limited").
        rarity_filter (int): Minimum rarity to filter (e.g., 4 for 4-star, 5 for 5-star).
    Returns list of dicts with card info and image.
    """
    char_id = CHARACTER_MAP.get(character_name.lower())
    if not char_id:
        return []

    try:
        response = requests.get(API_CARDS)
        if response.status_code != 200:
            return []
            
        all_cards = response.json()
        found_cards = []
        
        for card_id, card_data in all_cards.items():
            if card_data.get("characterId") == char_id:
                # Check for limited/specific type if requested
                card_type = card_data.get("type", "permanent")
                rarity = card_data.get("rarity", 3)

                # Rarity filter
                if rarity_filter is not None and rarity < rarity_filter:
                    continue

                # Filter Logic
                if card_type_filter:
                    filter_lower = card_type_filter.lower()
                    
                    # Direct Match
                    if filter_lower in card_type.lower():
                        pass 
                    # Special Handling for "limited" general request vs specific "limited" type
                    elif filter_lower == "limited":
                        if card_type not in ["limited", "dream_fes", "birthday", "kirafes"]:
                            continue
                    # Handle DreamFes / KiraFes aliases
                    elif "dream" in filter_lower or "fes" in filter_lower:
                        if "dream_fes" not in card_type and "kirafes" not in card_type:
                            continue
                    else:
                        continue
                
                # Construct data
                prefix = card_data.get("prefix", ["Unknown"])[1] # English if available
                if not prefix:
                     prefix = card_data.get("prefix", ["?"])[0] # Fallback to JP

                resource_set = card_data.get("resourceSetName")
                
                # Image URL selection
                if rarity >= 3:
                     image_url = ASSET_JP_CARD.format(resource_set)
                else:
                     image_url = ASSET_JP_CARD_NORMAL.format(resource_set)
                
                # Handle release date
                released_at = card_data.get("releasedAt", [0])
                release_date = released_at[0] if released_at else 0

                found_cards.append({
                    "id": card_id,
                    "title": prefix,
                    "rarity": rarity,
                    "type": card_type,
                    "image": image_url,
                    "release_date": release_date
                })
        
        # Sort by release date (newest first)
        found_cards.sort(key=lambda x: int(x["release_date"] or 0), reverse=True)
        
        return found_cards[:limit]

    except Exception as e:
        print(f"[Bestdori Error] get_character_cards: {e}")
        return []


def get_band_cards(band_name, limit=1, card_type_filter=None, rarity_filter=None):
    """
    Fetches cards across all members of a band.
    Returns the best matching card(s) sorted by release date.
    """
    members = BAND_MAP.get(band_name.lower(), [])
    if not members:
        return []

    all_cards = []
    for member in members:
        cards = get_character_cards(
            member,
            limit=5,  # Get more per member so we can cross-compare
            card_type_filter=card_type_filter,
            rarity_filter=rarity_filter
        )
        for card in cards:
            card["character"] = member  # Tag which member it belongs to
        all_cards.extend(cards)

    # Sort all collected cards by release date (newest first)
    all_cards.sort(key=lambda x: int(x["release_date"] or 0), reverse=True)
    return all_cards[:limit]
