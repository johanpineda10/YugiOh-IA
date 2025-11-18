# model/card_model.py
import requests

class Card:
    def __init__(self, name, atk, defe, img_url):
        self.name = name
        self.atk = atk
        self.defe = defe
        self.img_url = img_url

class CardAPI:

    @staticmethod
    def get_cards_list():
        """Retorna lista de nombres de cartas Monster."""
        try:
            url = "https://db.ygoprodeck.com/api/v7/cardinfo.php?num=30&offset=20"
            data = requests.get(url).json()["data"]

            return [c["name"] for c in data if "Monster" in c["type"]]

        except:
            return []

    @staticmethod
    def get_card_by_name(name):
        try:
            url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={requests.utils.quote(name)}"
            card = requests.get(url).json()["data"][0]

            atk = card.get("atk", 0)
            defe = card.get("def", 0)
            img = card["card_images"][0]["image_url"]

            return Card(card["name"], atk, defe, img)

        except:
            return None

    @staticmethod
    def get_random_monster():
        """Obtiene una carta Monster aleatoria."""
        while True:
            url = "https://db.ygoprodeck.com/api/v7/randomcard.php"
            card = requests.get(url).json()["data"][0]

            if "Monster" not in card["type"]:
                continue

            atk = card.get("atk", 0)
            defe = card.get("def", 0)
            img = card["card_images"][0]["image_url"]

            return Card(card["name"], atk, defe, img)
