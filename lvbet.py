from bs4 import BeautifulSoup
import urllib.request as urllib2
import sqlite3
import codecs
import logging
import datetime
from collections import defaultdict
from dictionaries import *
from selenium import webdriver
import time

#driver = webdriver.Chrome()
#driver.get('https://lvbet.pl/pl/zaklady-bukmacherskie/5/448/669/1797570')
#time.sleep(5)
#data = driver.page_source
#print (htmlSource)
#exit()
#user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
#url = "http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers"
#headers={'User-Agent':user_agent,}
#data=urllib2.Request('https://www.iforbet.pl/zdarzenie/460411',None,headers)
#response = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers))
#data = urllib2.urlopen(urllib2.Request('https://lvbet.pl/pl/zaklady-bukmacherskie/5/448/669/1797564',None,headers)).read() # The data u need
#data=codecs.open('fortuna.html',mode='r',encoding='utf-8').read()
#data=urllib2.urlopen('https://lvbet.pl/pl/zaklady-bukmacherskie/5/448/669/1797564').read()
data=codecs.open('lvbet_examplr.html',mode='r',encoding='utf-8').read()
soup = BeautifulSoup(data, "html.parser")
game=soup.find('h1',{'class':'bet_table_title'})
#print (soup)

class football_event:
    soup = BeautifulSoup(data,"html.parser")
    logging.basicConfig(filename='logfile_lvbet.log', level=logging.DEBUG)
    def get_events_mapping(self):
        return self.__events_mapping
    def get_name(self):
        soup = BeautifulSoup(data, "html.parser")
        #self.game=soup.find('h1',{'class':'bet_table_title'})
        self.game = soup.find('div',{'class':'scoreboard-mini'}).text
        self.home = unify_name(self.game.split('VS')[0].strip(),teams,logging)
        self.away = unify_name(self.game.split('VS')[1].strip(),teams,logging)
        self.league_raw = unify_name(soup.find_all('span',{'class':'additional'})[-3].text+' '+soup.find_all('span',{'class':'additional'})[-1].text,leagues,logging)
        #for el in self.league_raw:
        #    print (el.text)
        print (self.league_raw)
        print (self.home)
        print(self.away)
        #print (self.date)
    def get_odds(self):
        soup = BeautifulSoup(data, "html.parser")
        self.odds = defaultdict(str)
        rows=soup.find_all('div',{'class':'row lv-table-entry live-view'})
        #print ("ROW1",rows[0])
        #z=rows[0].find('div',{'class':'row'})
        #print(z)
        for row in rows:
            print (row)
            name=row.find('div',{'class':'col-d-4 col-t-12 teams live-event'}).text.strip()
            #odd_tittle=odd_t.text
            if name not in self.__events_mapping.keys():
                logging.warning(self.home + ' ' + self.away)
                logging.warning("Nieznany zaklad: " + name)
                continue

            self.odds[self.__events_mapping[name]["name"]] = defaultdict(str)

            print ('ODDS:',self.odds)
        #tables = soup.find_all('table', {'class': 'bet_table last_table'})


    def __init__(self, events_mapping_lvbet):
        self.__events_mapping=events_mapping_lvbet
        self.get_name()
        self.get_odds()
        #self.get_odds()
        #self.prepare_dict_to_sql()


meczyk = football_event(events_mapping_lvbet)
