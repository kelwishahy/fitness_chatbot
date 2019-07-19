# Pull all chest exercises from bodybuilder.com,
# and store exercise names in a json file for easy entity updating

import requests, bs4, json
exercises = []
data={}
items = []

for i in range(1, 6):
    url = 'https://www.bodybuilding.com/exercises/finder/' + str(i) + '?muscleid=2'
    searchResults = requests.get(url)
    searchResults.raise_for_status()
    html = bs4.BeautifulSoup(searchResults.text, features="html.parser")

    flexContainer = html.find_all(class_="ExResult-row flexo-container flexo-between")

    for ex in flexContainer:
        name = ex.find(class_='ExHeading ExResult-resultsHeading').find('a').text
        name = name.replace("\n                ", "")
        name = name.replace("\n              ", "")
        name = name.replace("-", " ")
        name = name.lower()
        name = name.replace("(", "")
        name = name.replace(")", "")
        exercises.append(name)

        payload = \
            {
                "value": name,
                "synonyms": [
                    name
                ]
            }

        items.append(payload)

for i in range(1, 6):
    url = 'https://www.bodybuilding.com/exercises/finder/' + str(i) + '?muscleid=10'
    searchResults = requests.get(url)
    searchResults.raise_for_status()
    html = bs4.BeautifulSoup(searchResults.text, features="html.parser")

    flexContainer = html.find_all(class_="ExResult-row flexo-container flexo-between")

    for ex in flexContainer:
        name = ex.find(class_='ExHeading ExResult-resultsHeading').find('a').text
        name = name.replace("\n                ", "")
        name = name.replace("\n              ", "")
        name = name.replace("-", " ")
        name = name.lower()
        name = name.replace("(", "")
        name = name.replace(")", "")
        exercises.append(name)

        payload = \
            {
                "value": name,
                "synonyms": [
                    name
                ]
            }

        items.append(payload)

for i in range(1, 6):
    url = 'https://www.bodybuilding.com/exercises/finder/' + str(i) + '?muscleid=15'
    searchResults = requests.get(url)
    searchResults.raise_for_status()
    html = bs4.BeautifulSoup(searchResults.text, features="html.parser")

    flexContainer = html.find_all(class_="ExResult-row flexo-container flexo-between")

    for ex in flexContainer:
        name = ex.find(class_='ExHeading ExResult-resultsHeading').find('a').text
        name = name.replace("\n                ", "")
        name = name.replace("\n              ", "")
        name = name.replace("-", " ")
        name = name.lower()
        name = name.replace("(", "")
        name = name.replace(")", "")
        exercises.append(name)

        payload = \
            {
                "value": name,
                "synonyms": [
                    name
                ]
            }

        items.append(payload)

data['name']='arms'
data['entries']=items
with open('arms.json', 'w+') as outfile:
    json.dump(data, outfile)

print(items)

