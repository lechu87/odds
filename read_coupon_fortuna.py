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
Base=declarative_base()
class db_fortuna(Base):
    __tablename__='db_fortuna'
    rowid=Column(primary_key=True)
    home=Column()
    away=Column()
    data=Column()
    _1=Column()
    _0 = Column()
    _2 = Column()
    _10 = Column()
    _02 = Column()
    _12 = Column()
    o_35 = Column()
    dnb_1 = Column()
    dnb_2 = Column()
    o_05 = Column()
    u_05 = Column()
    o_15 = Column()
    u_15 = Column()
    o_25 = Column()
    u_25 = Column()
    u_35 = Column()
    o_45 = Column()
    u_45 = Column()
    o_55 = Column()
    u_55 = Column()
    o_65 = Column()
    u_65 = Column()
    o_75 = Column()
    u_75 = Column()
    o_85 = Column()
    u_85 = Column()
    o_95 = Column()
    u_95 = Column()
    ht_ft_11 = Column()
    ht_ft_1x = Column()
    ht_ft_2x = Column()
    ht_ft_21 = Column()
    ht_ft_22 = Column()
    ht_ft_x1 = Column()
    ht_ft_x2 = Column()
    ht_ft_12 = Column()
    ht_ft_xx = Column()
    _1st_half_1 = Column()
    _1st_half_x = Column()
    _1st_half_2 = Column()
    _1st_half_10 = Column()
    _1st_half_02 = Column()
    _1st_half_12 = Column()
    #'eh-1_1' = Column()
    #eh-1=Column()
    #_x2 = Column()
    u_25_1 = Column()
    o_25_1 = Column()
    u_25_x = Column()
    o_25_x = Column()
    u_25_2 = Column()
    o_25_2 = Column()
    u_35_1 = Column()
    o_35_1 = Column()
    u_35_x = Column()
    o_35_x = Column()
    u_35_2 = Column()
    o_35_2 = Column()
    def __init__(self,home,away,_1):
        self.home=home
        self.away=away
        self._1=_1

    def __repr__(self):
        return "<db_sts('%s','%s','%s')>" % (self.home, self.away,self._1)
engine=create_engine('sqlite:///db.sqlite',echo=False)
Base.metadata.create_all(engine)
Session=sessionmaker(bind=engine)
session=Session

#s=engine.execute("SHOW TABLES;")

conn=engine.connect()
logging.basicConfig(filename='logfile_fortuna_read_coupon.log', level=logging.DEBUG)

#print (events_mapping_fortuna)
#kupon=codecs.open('fortuna_kupon2.html',mode='r',encoding='utf-8').read()
kupon=urllib2.urlopen('https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id=MzQyMDI3NjM4MzYyMzcwMDpv3ANXpNu4VC7+SgQ%3D&kind=MAIN').read()
soup = BeautifulSoup(kupon,"html.parser")
table=soup.find('div', {'class': 'ticket_container_inner'})
head=table.find('thead')
head_text=[]
for th in head.find('tr').find_all('th'):
    head_text.append(th.text)

#print (head_text)
body=table.find('tbody')
game=[]
for tr in body.find_all('tr'):
    name=tr.find('span',{'class':'bet_item_name'})
    discipline=name.text.split(' - ')[0]
    league=unify_name(name.text.split(' - ')[1].strip(),leagues,logging)
    home=unify_name(name.text.split(' - ')[2].strip(),teams,logging)
    away = unify_name(name.text.split(' - ')[3].strip(),teams,logging)

    tds=tr.find_all('td')
    raw_date=tds[3].text.strip()
    current_time = datetime.datetime.now()
    full_date = datetime.datetime(current_time.year, int(raw_date.split('.')[1]), int(raw_date.split('.')[0]),
                                  int((raw_date.split('.')[2]).split(':')[0]),
                                  int((raw_date.split('.')[2]).split(':')[1]))
    date = str(full_date.year) + '-' + str('{:02d}'.format(full_date.month)) + '-' + str(
        '{:02d}'.format(full_date.day))
    #print (date)
    type = tds[0].find('div', {'class': 'matchComment'}).text.split('/')[0].strip()
    typ=tds[1].text.strip()
    #print (type)
    #print (typ)
    for sql_name, name in sql_map_fortuna.items():
        if name==unify_name(events_mapping_fortuna[type]["name"]+typ,sql_map_fortuna,logging):
            x=sql_name

    znajdz_typ = unify2(events_mapping_fortuna[type]["name"] + typ, sql_map_fortuna, logging)
    ####wyciaga z bazy:
    #print (home, away)
    try:
        s = select([db_fortuna]).where(and_(db_fortuna.home == home,db_fortuna.away == away,db_fortuna.data == date))
        result = conn.execute(s)
        for r in result:
            print (r.home, r.away, r.data, r[znajdz_typ])
    except:
        print ("Nie znaleziono kursu",home,away)
    ###########


    #znajdz_typ = unify_name('game2', sql_map_fortuna, logging)
    #print ("Znajdz TYP:",znajdz_typ)

    #print(events_mapping_fortuna[type]["name"])

    #print (discipline, league, home, away,date,type)
    for td in tr.find_all('td'):

        game.append(td.text.strip())
league=(game[0].split(' - ')[1])


print ("MECZ:")
print (home)
print (away)

