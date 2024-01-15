import contextlib
import multiprocessing
import random

from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@contextlib.contextmanager
def connect_to_db():
    conn = None
    engine = None
    try:
        engine = create_engine('postgresql+psycopg2://postgres:salasana@localhost/advanced_index_test1')
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


def seed_employees(num_of_rows):
    fake = Faker()
    DEPARTMENTS = [

        'it',
        'software development',
        'ai',
        'rdi',
        'sanitation',
        'food services',
        'faculty'
    ]

    with connect_to_db() as _db:
        for _ in range(num_of_rows):
            rand_dep_index = random.randint(0, len(DEPARTMENTS) - 1)
            dep = DEPARTMENTS[rand_dep_index]
            stmt = text(
                'INSERT INTO employee_with_index(first_name, last_name, department) VALUES(:first_name, :last_name, :department)')
            _db.execute(stmt, {'first_name': fake.first_name(), 'last_name': fake.last_name(), 'department': dep})

        _db.commit()


if __name__ == '__main__':

    with connect_to_db() as db:
        ps = []
        for _ in range(50):
            p = multiprocessing.Process(target=seed_employees, args=(150000,))
            p.start()

            ps.append(p)

        for p in ps:
            p.join()
