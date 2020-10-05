#!/usr/bin/env python
import json
from dataclasses import dataclass

#https://www.ea.com/fifa/ultimate-team/web-app/content/21D4F1AC-91A3-458D-A64E-895AA6D871D1/2021/fut/items/web/players.json?_=21016
#https://www.ea.com/fifa/ultimate-team/web-app/content/21D4F1AC-91A3-458D-A64E-895AA6D871D1/2021/fut/items/web/nations.json?_=21016
#https://www.ea.com/fifa/ultimate-team/web-app/content/21D4F1AC-91A3-458D-A64E-895AA6D871D1/2021/fut/config/companion/teamconfig.json?_=21016
from typing import Optional


@dataclass
class Player:
    asset_id: int
    name: str
    rating: int
    loyalty_bonus: bool
    team: str
    league: str
    nation: str
    position: str


class PlayersStore:
    def __init__(self, src_file: str):
        self._src_file = src_file
        self._load()

    def _load(self):
        _data = json.loads(self._src_file)

        self._db = {}
        for player in _data["LegendsPlayers"] + _data["Players"]:
            self._db[player["id"]] = f'{player["f"]}, {player["l"]} [{player["r"]}]'

    def get_name(self, asset_id: int) -> Optional[str]:
        return self._db.get(asset_id)


class Importer:
    def __init__(self, src_file: str, players_store: PlayersStore):
        self._src_file = src_file
        self._players_store = players_store

    def _read_data(self):
        with open(self._src_file, 'r') as f:
            for idx, ln in enumerate(f, 1):
                try:
                    data = json.loads(ln)
                except (TypeError, ValueError):
                    print(f"Skipping ln {idx}, not json")
                    continue

                if "itemData" not in data:
                    print(f"Skipping ln {idx}, no itemData")
                    continue

                for item_idx, item in enumerate(data["itemData"]):
                    try:
                        self._parse_player(item)
                    except TypeError as e:
                        print(f"Skipping item {item_idx} from ln {idx}, {e}")
                        continue


    def _parse_player(self, player_data: dict) -> Player:
        if not player_data.get("itemType") == "player":
            raise TypeError(f"Not a player itemType: {player_data.get('itemType')}")

        return Player(
            asset_id=player_data["assetId"],
            name=self._get_player_name(player_data["assetId"]),
            rating=player_data["rating"],
            loyalty_bonus=bool(player_data["loyaltyBonus"]),
            team=self._get_team(player_data["teamid"]),
            league=self._get_league(player_data["teamid"]),
            nation=self._get_nation(player_data["nation"]),
            position=player_data["preferredPosition"],
        )

    def _get_player_name(self, asset_id: int) -> str:
        name = self._players_store.get_name(asset_id)
        return name or str(asset_id)

    @staticmethod
    def _get_team(team_id: int) -> str:
        return str(team_id)

    @staticmethod
    def _get_league(team_id: int) -> str:
        return f"of_team_{team_id}"

    @staticmethod
    def _get_nation(nation_id: int) -> str:
        return str(nation_id)

    def do(self):
        self._read_data()





if __name__ == '__main__':
    data_filename = "/home/ekirill/projects/mitproxy/fut.txt"
    players_filename = "/home/ekirill/projects/mitproxy/fut_db.json"
    players_store = PlayersStore(players_filename)
    importer = Importer(data_filename, players_store)
    importer.do()
