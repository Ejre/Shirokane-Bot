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

def get_rinko_cards(limit=1, only_limited=False):
    """
    Fetches cards for Shirokane Rinko (Character ID 24).
    Args:
        limit (int): Number of cards to return.
        only_limited (bool): If True, return only limited cards.
    Returns list of dicts with card info and image.
    """
    try:
        response = requests.get(API_CARDS)
        if response.status_code != 200:
            return []
            
        all_cards = response.json()
        rinko_cards = []
        
        for card_id, card_data in all_cards.items():
            if card_data.get("characterId") == 25:
                # Check for limited if requested
                card_type = card_data.get("type", "permanent")
                
                if only_limited:
                    if card_type not in ["limited", "dream_fes", "birthday", "kirafes"]:
                        continue
                
                # Construct data
                prefix = card_data.get("prefix", ["Unknown"])[1] # English if available
                if not prefix:
                     prefix = card_data.get("prefix", ["?"])[0] # Fallback to JP

                resource_set = card_data.get("resourceSetName")
                rarity = card_data.get("rarity", 3)
                
                # Image URL selection
                if rarity >= 3:
                     image_url = ASSET_JP_CARD.format(resource_set)
                else:
                     image_url = ASSET_JP_CARD_NORMAL.format(resource_set)
                
                # Handle release date
                released_at = card_data.get("releasedAt", [0])
                release_date = released_at[0] if released_at else 0

                rinko_cards.append({
                    "id": card_id,
                    "title": prefix,
                    "rarity": rarity,
                    "type": card_type,
                    "image": image_url,
                    "release_date": release_date
                })
        
        # Sort by release date (newest first)
        rinko_cards.sort(key=lambda x: int(x["release_date"] or 0), reverse=True)
        
        return rinko_cards[:limit]

    except Exception as e:
        print(f"[Bestdori Error] get_rinko_cards: {e}")
        return []
