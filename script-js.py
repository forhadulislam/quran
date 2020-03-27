from bs4 import BeautifulSoup
from urllib2 import urlopen, Request, quote
import dryscrape
import sqlite3
from sqlite3 import Error

lastSurah = 114

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.text_factory = str
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

    sql = " INSERT INTO quran_tafsir (surah_number, surah_name, sid, tafsir_title, tafsir_content, tafsir_content_html) VALUES(?,?,?,?,?,?) "
    cur = conn.cursor()
    cur.execute(sql, data)
    return cur.lastrowid

dbLocation = r"./quranTafsir.db"
dbConn = create_connection(dbLocation)

sql_create_translation_table = """CREATE TABLE IF NOT EXISTS quran_tafsir (
                                    id integer PRIMARY KEY,
                                    surah_number text NOT NULL,
                                    surah_name text NOT NULL,                                    
                                    sid text NOT NULL,
                                    tafsir_title text NOT NULL,
                                    tafsir_content text NOT NULL,
                                    tafsir_content_html text NOT NULL
                                );"""

if dbConn is not None:
    create_table(dbConn, sql_create_translation_table)
else:
    print("Error! cannot create the database connection.")


SPECIAL_CHARS = ["`", "'", "(", ")", "\""]
REPLACE_SPECIAL_CHARS = ["%60", "%27", "%28", "%29", "%22"]

def filterSpecialChars(data):
    output = data
    if (output[0] in SPECIAL_CHARS):
        ind = SPECIAL_CHARS.index(output[0])
        output[0] = output.replace(SPECIAL_CHARS[ind], REPLACE_SPECIAL_CHARS[ind])

    for ch in SPECIAL_CHARS:
        output = output.split(ch)[0]
        #output = output.replace(specialChars[i], replacespecialChars[i])

    output = output.replace(" ", "-")
    return output

def shortenTitle(title):
    spl = title.split(' ')
    dtTafsir = spl[:3]
    return "-".join(dtTafsir)

session = dryscrape.Session()

url = "http://mq.com/"
session.visit(url)
response = session.body()
soup = BeautifulSoup(response, 'html.parser')
surahs = soup.find("div", {"class": "ui-content"}).findAll("li")

failure_count = 0

# Looping through surah names
for surahNumber in range(0, len(surahs)):
    print(surahNumber)
    surahNameContent = surahs[surahNumber]
    surahName = surahNameContent.find("a").string
    dt = surahName.replace(" ", "-")
    surahUrl = url + dt
    session.visit(surahUrl)
    surahBody = session.body()
    soups = BeautifulSoup(surahBody, 'html.parser')
    surahPart = soups.find(id='ShowC').findAll("li")

    with dbConn:
        # Looping through tafsir page
        emptyContent = 0
        for countSurahTafsir in range(0, len(surahPart)):
            surahTafsirAllListContent = surahPart[countSurahTafsir]
            surahTafTitle = surahTafsirAllListContent.find("a").string

            # Looping through tafsir page & Scrapping content
            try:
                contentUrl = surahUrl + "/" + filterSpecialChars(surahTafTitle)

                session.visit(contentUrl.encode('utf-8'))
                contentBody = session.body()
                contentSoup = BeautifulSoup(contentBody, 'html.parser')
                contentTextHTML = contentSoup.find(id='ShowT')
                sid = 0
                try:
                    sid = contentTextHTML.attrs['sid']
                except:
                    pass

                contentText = contentTextHTML.get_text()
                if contentText == "" :
                    emptyContent += 1
                    print(shortenTitle(surahTafTitle))
                    print(contentUrl.encode('utf-8'))
                    contentText = "EMPTY"

                dt = (str(surahNumber+1), str(surahName), str(sid), str(surahTafTitle), str(contentText.encode('utf-8')), str(contentTextHTML.encode('utf-8')))
                newId = create_entry(dbConn, dt)
                print(newId)
            except:
                failure_count += 1
                print("failed")

    print(" Surah ", surahNumber)
    print(" Epmty content ", emptyContent)

print(" Failed times ", failure_count)
