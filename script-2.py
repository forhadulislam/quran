from bs4 import BeautifulSoup
from urllib2 import urlopen, Request
import sqlite3
from sqlite3 import Error
import json

firstSurah = 1
lastSurah = 114

jsonData = ""
with open('metadata/surah.json') as f:
  jsonData = json.load(f)

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

    sql = ''' INSERT INTO quran_words (surah_number, ayah_position, ayah, is_arabic, english_translation)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    return cur.lastrowid

dbLocation = r"./quranTafseer-Ibn-Katheer.db"
dbConn = create_connection(dbLocation)

sql_create_translation_table = """CREATE TABLE IF NOT EXISTS quran_words (
                                    id integer PRIMARY KEY,
                                    surah_number string NOT NULL,
                                    ayah_position string NOT NULL,
                                    ayah string NOT NULL,
                                    is_arabic integer NOT NULL,
                                    english_translation string NOT NULL
                                );"""

if dbConn is not None:
    create_table(dbConn, sql_create_translation_table)
else:
    print("Error! cannot create the database connection.")

filterWordInSurahName = "Quran >"

## Start looping
with dbConn:
    for count in range(firstSurah, len(jsonData) + 1):
        indx = count-1
        totalAyahs = jsonData[indx]["count"]
        surahNumber = jsonData[indx]["index"]
        print(totalAyahs)    
        
        for ayah in range(1, totalAyahs + 1):
            reg_url = "https://quranx.com/Tafsir/Kathir/" + str(count) + "." + str(ayah)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}
            req = Request(url=reg_url, headers=headers)
            req.encoding = "utf-8"
            page = urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')
            content = soup.find("dl", {"class": "boxed"}).findAll("dd")
            print(surahNumber + " - Ayah - " + str(ayah))
            contentSeq = 0
            for txt in content:
                fullText = txt.text
                contentSeq = contentSeq + 1
                isArabicText = 0
                if txt.has_attr('class') and txt['class'][0] == 'arabic':
                    isArabicText = 1
                dt = (surahNumber, str(contentSeq), str(ayah), isArabicText, fullText)
                newId = create_entry(dbConn, dt)
            break
        break

