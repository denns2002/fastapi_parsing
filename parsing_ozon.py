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
    name = Column(String)
    datetime = Column(DateTime)
    price = Column(Numeric(10, 2))

    def __repr__(self):
        return f'{self.name} | {self.price}'


engine = create_engine("sqlite:///database.sqlite")
Base.metadata.create_all(engine)
session = Session(bind=engine)


def add_to_db(product_title, product_price):
    is_exist = session.query(Price).filter(
        Price.name == product_title
    ).order_by(Price.datetime.desc()).first()

    if not is_exist:
        session.add(
            Price(
                name=product_title,
                datetime=datetime.now(),
                price=product_price
            )
        )
        session.commit()
    else:
        if is_exist.price != product_price:
            session.add(
                Price(
                    name=product_title,
                    datetime=datetime.now(),
                    price=product_price,
                )
            )
            session.commit()


def main():
    urls_list = open('urls.txt').readlines()
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }
    for el in urls_list:
        url = f'https://www.ozon.ru/product/{el}'
        driver = webdriver.Chrome('chromedriver')
        driver.get(url)
        time.sleep(5)

        #
        # SOUP EAT
        #

        soup = BeautifulSoup(driver.page_source, "lxml")

        try:
            product_title = soup.find('div', attrs={'data-widget': "webProductHeading"}).h1.get_text()
            product_price = soup.find('span', attrs={'class': 'm7u'}).get_text()
        except:
            continue

        product_price = re.search(r'\d+', product_price)[0]

        driver.quit()
        add_to_db(product_title, product_price)

    items = session.query(Price).all()
    for item in items:
        print(item)


if __name__ == '__main__':
    main()