import datetime
import re
import time

import requests
from selenium import webdriver
from bs4 import BeautifulSoup as BS
from selenium.webdriver import DesiredCapabilities
from sqlalchemy.orm import session

import models


def add_to_db(lst, city_id):
    session.add(
        models.Weather(
            datetime=datetime.now(),
            city=city_id,
            weather_day=lst[0],
            weather_night=lst[1],
            precipitation=lst[2],
            humidity=lst[3],
            wind=lst[4],
            pressure=lst[5],
        )
    )
    session.commit()


def yandex(city, urls):
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    URL = urls['yandex'] + city
    print(URL)
    driver = webdriver.Chrome(desired_capabilities=caps, executable_path='chromedriver')
    driver.get(URL)
    time.sleep(3)

    soup = BS(driver.page_source, "lxml")

    try:
        weather = soup.find("li", attrs={
            'class': 'forecast-briefly__day swiper-slide swiper-slide-next',
        }).get_text()
    except:
        print(False)
        return False

    weather_day = int(re.search(r'(?<=днём\+)(?:\d+)', weather)[0])

    weather_night = int(re.search(r'(?<=ночью\+)(?:\d+)', weather)[0])

    wind = soup.find("div", attrs={
        'class': 'title-icon title-icon_without-content',
    }).get_text()
    wind = int(re.search(r'(?<=ветер )(\d)', wind)[0])

    pressure = soup.find("div", attrs={
        'class': 'term term_orient_v fact__pressure',
    }).get_text()

    pressure = int(re.search(r'(?<=: )(?:\d+)', pressure)[0])
    precipitation = None
    humidity = None

    print(weather_day, weather_night, precipitation, humidity, wind, pressure)
    return [weather_day, weather_night, precipitation, humidity, wind, pressure]


def google(city, headers, urls):
    URL = urls['google'] + city
    print(URL)
    page = requests.get(url=URL, headers=headers)
    soup = BS(page.content, "lxml")

    try:
        weather_day = soup.find("span", attrs={
            'id': 'wob_tm'
        }).get_text()
        weather_day = int(weather_day)
    except:
        print(False)
        return False

    weather_night = soup.find("div", attrs={
        'class': 'QrNVmd ZXCv8e'
    }).span.get_text()
    weather_night = int(weather_night)

    precipitation = soup.find("span", attrs={
        'id': 'wob_pp'
    }).get_text()
    precipitation = int(precipitation.replace('%', ''))

    humidity = soup.find("span", attrs={
        'id': 'wob_hm'
    }).get_text()
    humidity = int(humidity.replace('%', ''))

    wind = soup.find("span", attrs={
        'id': 'wob_ws'
    }).get_text()
    wind = int(wind.replace(' м/с', ''))

    pressure = None
    print(weather_day, weather_night, precipitation, humidity, wind, pressure)
    return [weather_day, weather_night, precipitation, humidity, wind, pressure]


def gismeteo(city, headers, urls):
    URL = urls['gismeteo'] + city
    page = requests.get(url=URL, headers=headers)
    soup = BS(page.content, "lxml")

    try:
        link = soup.find("a", attrs={
            'class': 'link-item'
        })
        link = re.search(r'(?<=href=")(?:.+)(?="><i)', str(link))[0]
    except:
        print(False)
        return False

    URL = "https://www.gismeteo.ru" + link
    print(URL)
    page = requests.get(url=URL, headers=headers)
    soup = BS(page.content, "lxml")

    weather_night = soup.find("div", attrs={
        'class': 'tab-temp tab-charts'
    }).div.div.div.span.get_text().replace('+', '')
    weather_night = int(weather_night)

    weather_day = soup.find("div", attrs={
        'class': 'tab-temp tab-charts'
    }).div.div.div.span.next_element.next_element.next_element.next_element.next_element.get_text().replace('+', '')
    weather_day = int(weather_day)

    find_wind = soup.find_all("span", attrs={
        'class': 'wind-unit unit unit_wind_m_s'
    })
    find_wind = [int(el.get_text().split('-')[0]) for el in find_wind[5:13]]
    wind = 0
    for el in find_wind:
        wind += el
    wind /= len(find_wind)
    wind = round(wind)

    find_hum = soup.find_all("div", attrs={
        'class': 'widget-row widget-row-humidity'
    })
    find_hum = [str(el.get_text()) for el in find_hum][0]
    find_hum = [find_hum[i:i + 2] for i in range(0, len(find_hum), 2)]
    humidity = 0
    for el in find_hum:
        humidity += int(el)
    humidity /= len(find_hum)
    humidity = round(humidity)

    find_pressure = soup.find_all("span", attrs={
        'class': 'unit unit_pressure_mm_hg_atm'
    })[1:]
    find_pressure= [int(el.get_text()) for el in find_pressure]
    pressure = 0
    for el in find_pressure:
        pressure += el
    pressure /= len(find_pressure)
    pressure = round(pressure)

    precipitation = None
    print(weather_day, weather_night, precipitation, humidity, wind, pressure)
    return [weather_day, weather_night, precipitation, humidity, wind, pressure]
