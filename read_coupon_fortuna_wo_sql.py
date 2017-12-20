import codecs
from bs4 import BeautifulSoup
from dictionaries import *
from collections import defaultdict
import logging
import datetime
import urllib.request as urllib2

from sqlalchemy.sql import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column
from sqlalchemy.sql import and_, or_, not_
def read_coupon(adres):
#adres1='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id=OTk5MDQ3NzA4NDg0MzMwMDp5D0b%2BhWJvXFEHkRg%3D&kind=MAIN'
#adres2='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id=OTQxMzI3NzA5MzUzMTEwMDrsspzQo7BGblqFRrA%3D&kind=MAIN'
#adres='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id=Mzk5MDM3NzA5NDA1MjkwMDqZs952+IomQH8BbOE%3D&kind=MAIN'
    kupon=urllib2.urlopen(adres).read()

    soup = BeautifulSoup(kupon,"html.parser")
    table=soup.find('div', {'class': 'ticket_container_inner'})
    head=table.find('thead')
    head_text=[]
    for th in head.find('tr').find_all('th'):
        head_text.append(th.text)

    #print (head_text)
    body=table.find('tbody')
    game=[]
    odds=[]
    all_events=[]
    for tr in body.find_all('tr'):
        name=tr.find('span',{'class':'bet_item_name'})
        discipline=name.text.split(' - ')[0]
    #    league=unify_name(name.text.split(' - ')[1].strip(),leagues,logging)
        home=unify_name(name.text.split(' - ')[2].strip(),teams,logging)
        away = unify_name(name.text.split(' - ')[3].strip(),teams,logging)
        #print ("Home:",home," Away:",away)
        tds=tr.find_all('td')
        raw_date=tds[3].text.strip()
        current_time = datetime.datetime.now()
        full_date = datetime.datetime(current_time.year, int(raw_date.split('.')[1]), int(raw_date.split('.')[0]),
                                      int((raw_date.split('.')[2]).split(':')[0]),
                                      int((raw_date.split('.')[2]).split(':')[1]))
        date = str(full_date.year) + '-' + str('{:02d}'.format(full_date.month)) + '-' + str(
            '{:02d}'.format(full_date.day))
        #print (date)
        type = tds[0].find('div', {'class': 'matchComment'}).text.split(' / ')[0].strip()
        typ=tds[1].text.strip()
    #    print (type)
    #    print (typ)
    #    print ("TypeTyp:",type+typ)
        #print ("Szukam:",events_mapping_fortuna[type]["name"]+typ)
        znajdz_typ = unify_name(type +'_'+ typ, sql_map_fortuna, logging)
     #   print (znajdz_typ+"::::::::::::::::")
        ####wyciaga z bazy:
        #print (home, away)
        one_event=[home,away,znajdz_typ]
        #print (home,away,znajdz_typ)
        all_events.append(one_event)
    #print (all_events)
    return (all_events)

adres='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id=Mzk5MDM3NzA5NDA1MjkwMDqZs952+IomQH8BbOE%3D&kind=MAIN'
print(read_coupon(adres))
read_coupon(adres)
