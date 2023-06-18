import contextlib
import sqlite3

from django.http import HttpResponse
from django.shortcuts import render
import openpyxl
from datetime import datetime
from openpyxl.workbook import Workbook

now = datetime.now().strftime("%Y%m%d_%H-%M-%S")
wb: Workbook = openpyxl.Workbook()
ws = wb.active


class DB:

    @staticmethod
    def select_all(query: str):
        """
        Show all datas on DB (SQLite3)!
        """
        with contextlib.closing(sqlite3.connect('database/database.db')) as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None:
                raise Exception("Not have proposes")
            return rows

    @staticmethod
    def insert_to_db(query: str, value: tuple) -> bool:
        """
        Insert "Product" to DB (SQLite3)!
        """
        with contextlib.closing(sqlite3.connect('database/database.db')) as connection:
            cursor = connection.cursor()
            status = False
            try:
                cursor.execute(query, value)
            except Exception as error:
                print("error", error)
                connection.rollback()
            else:
                connection.commit()
                status = True
            finally:
                return status


# def create_sql(): with contextlib.closing(sqlite3.connect("../database/database.db")) as conn: with conn as cur:
# cur.execute("CREATE TABLE products(_id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL, title TEXT NOT NULL,
# description TEXT)") # cur.execute("INSERT INTO products (title, description, price, count) VALUES ('Bananas',
# 'african bananas', 570.52, 300.2)")


def home(request):
    return render(request=request, template_name="home.html")


def offer(request):
    if request.method == "GET":
        return render(request=request, template_name="offer.html")

    elif request.method == "POST":
        name = str(request.POST.get("name"))
        title = str(request.POST.get("title"))
        proposes = str(request.POST.get("proposes"))
        ws.append([name, title, proposes])
        DB.insert_to_db("INSERT INTO products (name, title, description) VALUES (?, ?, ?)", (name, title, proposes))
        return render(request=request, template_name="success.html")


def download(request):
    row = DB.select_all("SELECT name, title, description FROM products")
    for datas in row:
        ws.append(datas)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Proposes_for_{now}.xlsx"'
    wb.save(response)
    return response


def all_list(request):
    row = DB.select_all("SELECT name, title, description FROM products")
    context = [
        {"name": x[0],
         "title": x[1],
         "description": x[2]
         } for x in row
    ]
    return render(request=request, template_name="all_list.html", context={'context': context})


if __name__ == "__main__":
    # create_sql()
    pass
