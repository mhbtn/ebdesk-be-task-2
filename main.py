from selenium import webdriver
from bs4 import BeautifulSoup
import datetime as dt
import sqlite3

def main():

    # connection to database
    connection = sqlite3.connect("youtube.db")
    cursor = connection.cursor()
    cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='trending_youtube' ''')
    if cursor.fetchone()[0] == 1:
        # table exist
        cursor.execute('DELETE FROM trending_youtube')
        cursor.execute('DELETE FROM sqlite_sequence WHERE name=\'trending_youtube\'')
        connection.commit()
    else:
        cursor.execute("CREATE TABLE trending_youtube (id INTEGER CONSTRAINT id_trending PRIMARY KEY AUTOINCREMENT, channel_id TEXT, title TEXT, channel_name TEXT, publish_date INTEGER)")

    option = webdriver.ChromeOptions()
    option.add_argument('headless')
    driver = webdriver.Chrome("chromedriver.exe", options=option)
    driver.get("https://www.youtube.com/feed/trending")
    content = driver.page_source.encode('utf-8').strip()
    soup = BeautifulSoup(content, 'lxml')

    judul_dan_url_video = soup.findAll('a', id='video-title')
    channel_dan_url_channel = soup.findAll('a', class_='yt-simple-endpoint style-scope yt-formatted-string')

    chan_count = 0
    for content in judul_dan_url_video[:20]:
        judul = content.text.strip('\n').strip()
        judul = judul.replace("'", "`")
        link_video = content.get('href').strip('\n').strip()
        link_video = "https://youtube.com{}".format(link_video)

        # get tanggal
        driver.get(link_video)
        get_content = driver.page_source.encode('utf-8').strip()
        soup_get_content = BeautifulSoup(get_content, 'lxml')
        simpan_tanggal = soup_get_content.findAll('meta', {"itemprop":"datePublished"})[0].get('content')
        split_tanggal = simpan_tanggal.split('-')
        publish_date = dt.date(int(split_tanggal[0]), int(split_tanggal[1]), int(split_tanggal[2]))
        publish_date += dt.timedelta(days=1)

        # get channel name
        channel_name = channel_dan_url_channel[chan_count].text.strip('\n').strip()

        # get channel id
        channel_link = channel_dan_url_channel[chan_count].get('href').strip('\n').strip()
        channel_link = "https://youtube.com{}".format(channel_link)
        driver.get(channel_link)
        get_channel = driver.page_source.encode('utf-8').strip()
        soup_get_channel_id = BeautifulSoup(get_channel, 'lxml')
        channel_id = soup_get_channel_id.findAll('meta', {"itemprop":"channelId"})[0].get('content')

        print('\nchannel id : {} |\t{} |\t{} |\t{}'.format(channel_id, judul, channel_name, publish_date))

        cursor.execute("INSERT INTO trending_youtube(channel_id, title, channel_name, publish_date) VALUES('{}','{}','{}','{}')".format(channel_id, judul, channel_name, publish_date))
        connection.commit()

        chan_count += 2

main()