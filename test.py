import requests
import json

class LolAPI:
    def __init__(self):
        self.api_key = 'RGAPI-991ae20a-22b9-4efd-82ed-8f5802f7320d'
        self.champion_list = self.get_champions()
    @property
    def summoner (self):
        req = requests.get("https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/{}?api_key={}".format("Shadowblasts",self.api_key))
        info = json.loads(req.content)
        return info

    def get_free_champions(self):
        string = ""
        req = requests.get("https://na1.api.riotgames.com/lol/platform/v3/champions?freeToPlay=true&api_key={}".format(self.api_key))
        info = json.loads(req.content)
        for i in self.champion_list["data"]:
            for j in range(len(info["champions"])):
                if self.champion_list["data"][i]["key"] == str(info["champions"][j]["id"]):
                    string += self.champion_list["data"][i]["name"] + "\n"
        return string

    def get_champions(self):
        req = requests.get("http://ddragon.leagueoflegends.com/cdn/8.13.1/data/en_US/champion.json")
        info = json.loads(req.content)
        return info

l = LolAPI()
print(l.get_free_champions())
# print(l.champion_list)
# l.get_champion_info()
# print(l.summoner["id"])