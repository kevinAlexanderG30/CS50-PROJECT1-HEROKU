import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgresql://ffrkfknqbahajw:d84315a7a8fb07644553f98cbd4b1c36db4e4d7a8a78dbe7acc16f4cf8297944@ec2-3-225-213-67.compute-1.amazonaws.com:5432/dc3l910adjg8ve")
db = scoped_session(sessionmaker(bind=engine))

def main(): 
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()

if __name__ == "__main__":
    main()