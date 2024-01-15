import contextlib
import logging
import multiprocessing
import random
import sys
from multiprocessing import Process

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

faker = Faker()

countries = {

    "South America": ["Brazil"],
    "North America": ["United States"],
    "Australia": ["Australia"],
    "Africa": ["Ethiopia"],
    "Asia": ["China"],
    "Europe": ["Finland", "France"]}


@contextlib.contextmanager
def connect_to_db():
    conn = None
    engine = None
    try:
        engine = create_engine('postgresql+psycopg2://postgres:salasana@localhost/olt_store_example')
        session = sessionmaker(bind=engine)
        conn = session()

        yield conn
    except Exception as e:
        print(e)
    finally:

        if conn is not None:
            conn.close()
        if engine is not None:
            engine.dispose()


def seed_zip_and_address(_db, customer_id, city_id):
    stmt = text('INSERT INTO zip_code(zip_code, city_id) VALUES(:zip, :city_id) RETURNING id')
    zip_id = _db.execute(stmt, {'zip': faker.street_address().split(' ')[0], 'city_id': city_id}).first()[0]
    stmt = text('INSERT INTO address(id, street, zip_code_id) VALUES (:customer_id, :street, :zip_id)')
    _db.execute(stmt, {'customer_id': customer_id, 'street': faker.street_name(), 'zip_id': zip_id})


def _seed_cities(_db, country_id):
    for _ in range(10):
        stmt = text('INSERT INTO city(city_name, country_id) VALUES(:city, :country_id)')
        _db.execute(stmt, {'city': faker.city(), 'country_id': country_id})


def _seed_countries(_db, continent_id, continent):
    for country in countries[continent]:
        stmt = text('INSERT INTO country(country_name, continent_id) VALUES(:country, :continent_id) RETURNING id')
        country_id = _db.execute(stmt, {'country': country, 'continent_id': continent_id}).first()[0]
        _seed_cities(_db, country_id)


def seed_continents(_db):
    for c in ['Asia', 'Africa', 'North America', 'South America', 'Europe', 'Australia']:
        stmt = text('INSERT INTO continent(continent_name) VALUES(:c) RETURNING id')
        result = _db.execute(stmt, {'c': c}).first()[0]
        _seed_countries(_db, result, c)
    _db.commit()


def flush(_db):
    _db.execute(text('DELETE FROM address'))
    _db.execute(text('DELETE FROM category'))
    _db.execute(text('DELETE FROM zip_code'))
    _db.execute(text('DELETE FROM city'))

    _db.execute(text('DELETE FROM client'))

    _db.execute(text('DELETE FROM country'))
    _db.execute(text('DELETE FROM continent'))
    _db.execute(text('DELETE FROM public.order'))
    _db.execute(text('DELETE FROM order_state'))
    _db.execute(text('DELETE FROM product'))
    _db.commit()


def seed_customers(num_of_customers):

    with connect_to_db() as _db:
        cities = []
        res = _db.execute(text('SELECT id FROM city')).all()
        for r in res:
            cities.append(r[0])

        for _ in range(num_of_customers):
            stmt = text('INSERT INTO client(first_name, last_name) VALUES(:first_name, :last_name) RETURNING id')
            customer_id = _db.execute(stmt, {'first_name': faker.first_name(), 'last_name': faker.last_name()}).first()[
                0]
            rand_city_id = random.randint(0, len(cities) - 1)
            seed_zip_and_address(_db, customer_id, cities[rand_city_id])


        _db.commit()




if __name__ == '__main__':
    flush_first = input("tyhjennä kanta ensin (k/e): ")
    ps = []
    with connect_to_db() as db:
        if flush_first == 'k':
            flush(db)
            seed_continents(db)

    for _ in range(5):
        p = multiprocessing.Process(target=seed_customers, args=(30000,))
        p.start()

        ps.append(p)

    for p in ps:
        p.join()
