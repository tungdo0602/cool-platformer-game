import requests

def updateLevels():
    data = requests.get("https://api.github.com/repos/tungdo0602/cool-platformer-game/contents/levels")

    if data.status_code == 200:
        for i in data.json():
            level = requests.get(i["download_url"])
            if level.status_code == 200:
                with open("./levels/" + i["name"], "w") as  f:
                    f.write(level.text)