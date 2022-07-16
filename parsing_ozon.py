import re
import time

from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import Column, Integer, String, DateTime, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

#
#  DATABASE
#
Base = declarative_base()


class Price(Base):
    __tablename__ = "price"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    name = Column(String)
    price = Column(Numeric(10, 2))
    url = Column(String)

    def __repr__(self):
        return f'{self.name} | {self.price} | {self.url[:20]}...'


engine = create_engine("sqlite:///database.sqlite")
Base.metadata.create_all(engine)
session = Session(bind=engine)


def parsing_url(url, category=None, pages=1):
    '''С помощью Selenium парсит ссылку с небольшой зайдержкой по атрибутам'''

    driver = webdriver.Chrome('chromedriver')
    driver.get(url)
    time.sleep(3)  # Юзер не робот и делает задержку, поставил на всякий случай

    soup = BeautifulSoup(driver.page_source, "lxml")
    product_title, product_price = '', ''

    if category != None:
        page = 1

        while page <= pages:
            urls_hrefs = soup.find_all('a', attrs={'class': 't2j tile-hover-target'})
            urls_list = []
            if len(urls_hrefs) != 0:
                for urls in urls_hrefs:
                    urls_list.append('https://www.ozon.ru' + urls.attrs['href'])

                for urls in urls_list:
                    title, price = parsing_url(urls)
                    add_to_db(title, price, urls)
            else:
                driver.quit()
                print('На этой странице нет больше товаров')
                break

            driver.quit()
            page += 1
            driver = webdriver.Chrome('chromedriver')
            driver.get(url + f'?&page={page}')
            print(url + f'?&page={page}')
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "lxml")

    else:
        try:
            product_title = soup.find('div', attrs={'data-widget': "webProductHeading"}).h1.get_text()
            product_price = soup.find('span', attrs={'class': 'm9t'}).get_text()
            product_price = re.search(r'(?:\d+)(?: \d*)*', product_price)[0]
        except:
            print(f'Товар по ссылке:\n{url}\nNOT PARSED.')

    driver.quit()

    return product_title, product_price


def add_to_db(product_title, product_price, url):
    '''Добавляет элемент в базу данных Price'''
    product_price = int(product_price.replace(' ', ''))
    is_exist = session.query(Price).filter(
        Price.name == product_title
    ).order_by(Price.datetime.desc()).first()

    if not is_exist:
        session.add(
            Price(
                name=product_title,
                datetime=datetime.now(),
                price=product_price,
                url=url,
            )
        )
        print(f'Товар {product_title} добавлен в DB!')
    else:
        if is_exist.price != product_price:
            session.add(
                Price(
                    name=product_title,
                    datetime=datetime.now(),
                    price=product_price,
                    url=url,
                )
            )
            print(f'Цена у товара {product_title} обновлена!')
    session.commit()


def main():
    #  Читает файл urls.txt
    #  Каждая ссылка в новой строке
    #  Есть возможность запарсить категории, но без подкатегорий!

    #  Если парсите категорию ставим перед ней число и разделяем пробелом
    #  Никакие ковычи и т.п. не нужны!
    #  Прим строки:
    #  4 www.ozon.ru/category/...
    #  Единичку можно не ставить
    #  Если хотите все страницы категории пишите просто большое число (9999)
    #  Однако это зйамет целую вечность...

    urls_list = open('urls.txt').readlines()

    items = session.query(Price).all()

    if len(urls_list) != 0:
        for url in urls_list:
            if re.search(r'www\.ozon\.ru/category/', url) is not None:
                pages = re.match(r'(?:\d*)(?= )', url)
                if pages == None:
                    pages = [1]
                url = url.replace(pages[0]+' ', '', 1)
                parsing_url(url, True, int(pages[0]))
            else:
                title, price = parsing_url(url)
                add_to_db(title, price, url)

    items_new = session.query(Price).all()
    if len(items) == len(items_new):
        print('В базу ничего не добавленно.')

    for item in items_new:
        print(item)


if __name__ == '__main__':
    main()
