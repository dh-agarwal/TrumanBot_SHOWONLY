import sys
sys.path.insert(1,'src/dining')
from bs4 import BeautifulSoup
import requests
from datetime import date
import calendar

def getTimesDict(URL):
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    timestable = (((soup.find(class_="textwidget")).text).replace("Date\nHours", "").strip().split("\n\n\n"))

    timesdict = {}

    for day in timestable:
        timesdict[day[:day.find("\n")]] = day[day.find("\n")+1:]

    for time in timesdict:
        timesdict[time] = timesdict[time].replace(")", ")\n\n")
        val = timesdict[time]
        for chr in range(len(val) - 1):
            if ((val[chr].isalpha()) and val[chr+1].isdigit()):
                timesdict[time] = val[:chr+1] + "\n\n" + val[chr+1:]

    return timesdict

def getMenuDict(URL):
    shorten = ["https://dining.missouri.edu/locations/catalyst-cafe/", "https://dining.missouri.edu/locations/morts/", "https://dining.missouri.edu/locations/wheatstone-bistro/"]
    if (URL == "https://dining.missouri.edu/locations/subway-hitt-street/"):
        return {"\u200b": ["Visit the [Subway Website](https://order.subway.com/en-US) for a full menu"]}
    if (URL == "https://dining.missouri.edu/locations/starbucks-memorial-union/"):
        return {"\u200b": ["Visit the [Starbucks Website](https://www.starbucks.com/) for a full menu"]}

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    if (URL == "https://dining.missouri.edu/locations/the-mark-on-5th-street/"):
        return (getChangingMenu(soup))

    if (URL == "https://dining.missouri.edu/locations/plaza-900-dining/"):
        return (getChangingMenu(soup))

    text = soup.find_all("td")
    i = 0
    allitemslist = []
    for item in text:
        if (i%2 == 0):
            allitemslist.append((item.text).replace("\n", "").replace("\t", ""))
        i += 1
    allitemslist = allitemslist[:-7]
    alltext = soup.text.replace("\n", "").replace("\t", "")
    menudict = {}
    headers = soup.find_all("button", class_="miz-button miz-button--primary miz-button--light accordion__button")

    for header in range(len(headers)):
        txt1 = headers[header].text.replace("\n", "").replace("\t", "").replace("add", "").replace("search", "").replace("menu", "").replace("Dining Plansarrow_drop_down", "")
        if header != len(headers)-1:
            txt2 = headers[header+1].text.replace("\n", "").replace("\t", "").replace("add", "").replace("search", "").replace("menu", "").replace("Dining Plansarrow_drop_down", "")
        foodlist = []
        if header != len(headers)-1:
            for food in allitemslist:
                if food in alltext[alltext.find(txt1)-2:alltext.find(txt2)+3]:
                    for char in range(len(food)-1):
                        if food[char].islower() and food[char+1] != ' ' and food[char+1].isupper():
                            if URL not in shorten:
                                food = (food[:char+1]) + ':\n- ' + food[char+1:]
                            else:
                                food = (food[:char+1])
                                break
                    foodlist.append(food)
                    menudict[txt1] = foodlist
        else:
            for food in allitemslist:
                if food in alltext[alltext.find(txt1)-2:]:
                    for char in range(len(food)-1):
                        if food[char].islower() and food[char+1] != ' ' and food[char+1].isupper():
                            if URL not in shorten:
                                food = (food[:char+1]) + ':\n- ' + food[char+1:]
                            else:
                                food = (food[:char+1])
                                break
                    foodlist.append(food)
                    menudict[txt1] = foodlist
    return menudict

def getChangingMenu(soup):
    my_date = date.today()
    dayOfWeek = calendar.day_name[my_date.weekday()]

    breakfastmenu = []
    lunchmenu = []
    dinnermenu = []

    dropdowns = []
    alldropdowns = (soup.find_all("button", {"class": "miz-button miz-button--primary miz-button--light accordion__button"}))
    for drop in alldropdowns:
        if dayOfWeek in str(drop):
            dropdowns.append(drop)

    drops = {
        "Breakfast": False,
        "Lunch": False,
        "Dinner": False
    }

    for meal in dropdowns:
        meal = str(meal)
        if "Breakfast" in meal:
            drops["Breakfast"] = True
        if "Lunch" in meal:
            drops["Lunch"] = True
        if "Dinner" in meal:
            drops["Dinner"] = True

    dropmeals = {}
    x = 1
    for meal in drops:
        if drops[meal] == True:
            dropmeals[meal] = "collapse-layer{}{}".format(dayOfWeek, x)
            x += 1

    if ("Breakfast" in dropmeals):
        breakfastmenu = ((soup.find("div", id=dropmeals["Breakfast"])).text.replace("\n","").split("\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"))
        while ("" in breakfastmenu):
            breakfastmenu.remove("")
        for item in range(len(breakfastmenu)):
            breakfastmenu[item] = breakfastmenu[item].strip()
    if ("Lunch" in dropmeals):
        lunchmenu = ((soup.find("div", id=dropmeals["Lunch"])).text.replace("\n","").split("\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"))
        while ("" in lunchmenu):
            lunchmenu.remove("")
        for item in range(len(lunchmenu)):
            lunchmenu[item] = lunchmenu[item].strip()
    if ("Dinner" in dropmeals):
        dinnermenu = ((soup.find("div", id=dropmeals["Dinner"])).text.replace("\n","").split("\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t"))
        while ("" in dinnermenu):
            dinnermenu.remove("")
        for item in range(len(dinnermenu)):
            dinnermenu[item] = dinnermenu[item].strip()

    menudict = {}
    if drops["Breakfast"]:
        menudict["Breakfast"] = breakfastmenu
    if drops["Lunch"]:
        menudict["Lunch"] = lunchmenu
    if drops["Dinner"]:
        menudict["Dinner"] = dinnermenu

    return menudict

    
hallInfoDict = {
    "1+5+3 Salads and Soups": ["https://dining.missouri.edu/locations/153-salads-and-soups/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/153-logo-e1615579713594.jpg"],
    "1839 Kitchen": ["https://dining.missouri.edu/locations/1839-kitchen/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/1839-768x668.jpg"],
    "Baja Grill": ["https://dining.missouri.edu/locations/baja-grill/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/BajaLogo-01.png"],
    "Bookmark Caf??": ["https://dining.missouri.edu/locations/bookmark-cafe/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Bookmark_cafe-210x300.png"],
    "Catalyst Caf??": ["https://dining.missouri.edu/locations/catalyst-cafe/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Catalyst-768x324.png"],
    "Do Mundo's": ["https://dining.missouri.edu/locations/do-mundos/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/DoMundos2-768x134.png"],
    "Emporium Caf??": ["https://dining.missouri.edu/locations/emporium-cafe/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Emporium_cafe-210x300.png"],
    "infusion": ["https://dining.missouri.edu/locations/infusion/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Infusion-300x204.png"],
    "Legacy Grill": ["https://dining.missouri.edu/locations/legacy-grill/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/LegacyGrill-300x194.png"],
    "Mort's": ["https://dining.missouri.edu/locations/morts/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Morts2.png"],
    "Olive & Oil": ["https://dining.missouri.edu/locations/olive-&-oil/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/OliveandOil.png"],
    "Panda Express": [],
    "Plaza 900 Dining": ["https://dining.missouri.edu/locations/plaza-900-dining/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Plaza900.png"],
    "Potential Energy Caf??": ["https://dining.missouri.edu/locations/potential-energy-cafe/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Potentail-Energy-Logo.jpg"],
    "Pizza & MO": ["https://dining.missouri.edu/locations/pizza-&-mo/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Pizza_MO.png"],
    "Breakfast & MO": ["https://dining.missouri.edu/locations/breakfast-&-mo/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Breakfast_MO.png"],
    "Sabai": ["https://dining.missouri.edu/locations/sabai/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/sabai.png"],
    "Starbucks": ["https://dining.missouri.edu/locations/starbucks-memorial-union/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/starbucks.png"],
    "Subway": ["https://dining.missouri.edu/locations/subway-hitt-street/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/subway.png"],
    "Sunshine Sushi": ["https://dining.missouri.edu/locations/sunshine-sushi/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/sunshinesushi-300x150.png"],
    "The MARK on 5th Street": ["https://dining.missouri.edu/locations/the-mark-on-5th-street/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/themarkon5th-01.png"],
    "Tiger Avenue Deli": ["https://dining.missouri.edu/locations/tiger-avenue-deli/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Tiger-Avenue-Deli-Logo-e1615577624599.jpg"],
    "Truffles": ["https://dining.missouri.edu/locations/truffles/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/Truffles-Logo.jpg"],
    "Wheatstone Bistro": ["https://dining.missouri.edu/locations/wheatstone-bistro/", "https://dining.missouri.edu/wp-content/uploads/sites/19/2019/05/WheatstoneBistro.png"]
}

class DiningHall:
    def __init__(self, name):
        self.name = name
        self.url = hallInfoDict[name][0]
        self.logo = hallInfoDict[name][1]
        self.menu = getMenuDict(hallInfoDict[name][0])
        self.times = getTimesDict(hallInfoDict[name][0])