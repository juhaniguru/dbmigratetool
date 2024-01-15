import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import models

if __name__ == '__main__':
    print("################## Tietokantojen pitää olla käynnissä oletusporteissa ##############")
    print("Postgres: 5432")
    print("Mysql: 3306")

    mysql_name = input("Anna tietokannan nimi: ")

    #  sqlacodegen_v2 mysql://root:@localhost/fullstack3002mvp --outfile models.py

    try:
        os.system(f"sqlacodegen_v2 mysql://root:@localhost/{mysql_name} --outfile models.py")

        engine1 = create_engine(f'postgresql+psycopg2://postgres:salasana@localhost/postgres')
        ses = sessionmaker(bind=engine1, autoflush=True)

        conn = ses()
        conn.execute(text('commit'))
        stmt = text(f'CREATE DATABASE {mysql_name}')
        conn.execute(stmt)

        conn.close()

        engine = create_engine(f'postgresql+psycopg2://postgres:salasana@localhost/{mysql_name}')
        ses = sessionmaker(bind=engine)

        conn = ses()

        models.Base.metadata.create_all(bind=engine)

        conn.close()

    except Exception as e:
        print(e)

