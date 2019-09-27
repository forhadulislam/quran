from bs4 import BeautifulSoup
from urllib2 import urlopen, Request
import sqlite3
from sqlite3 import Error

firstSurah = 1
lastSurah = 114

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_entry(conn, data):

    sql = ''' INSERT INTO quran_words (surahname, ayahposition, ayah, arabic_word, english_translation)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    return cur.lastrowid

dbLocation = r"./qWordDB.db"
dbConn = create_connection(dbLocation)

sql_create_translation_table = """CREATE TABLE IF NOT EXISTS quran_words (
                                    id integer PRIMARY KEY,
                                    surahname string NOT NULL,
                                    ayahposition string NOT NULL,
                                    ayah string NOT NULL,
                                    arabic_word string NOT NULL,
                                    english_translation string NOT NULL
                                );"""

if dbConn is not None:
    create_table(dbConn, sql_create_translation_table)
else:
    print("Error! cannot create the database connection.")

filterWordInSurahName = "Quran >"

## Start looping
for count in range(firstSurah, lastSurah + 1):
    url = "http://quran.net/word/" + str(count) + "/"
    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    words = soup.find("div", {"class": "ayahs rtl"}).findAll("p")
    surah = soup.find("div", {"class": "location"}).find("p")
    surahName = surah.text.replace(filterWordInSurahName, '').strip()
    print(surahName)
    with dbConn:
        for x in words:
            spans = x.find("span")
            classes = x["class"]
            id = x["id"]
            classes.remove('ayah')
            print(id)
            if spans != -1:
                spans = x.find("span")
                for span in spans:
                    arabicText = span.find("span", {"class": "ar quranText top first rtl"})
                    englishText = span.find("span", {"class": "en second ltr"})
                    dt = (surahName, str(classes[0]), str(id), arabicText.text, englishText.text)
                    newId = create_entry(dbConn, dt)

                    #print(staticWord.text)
                    #print(quranText.text)
