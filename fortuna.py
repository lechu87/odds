# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import pandas as pd
import sqlite3
from sqlalchemy import create_engine


data=urllib2.urlopen('https://www.efortuna.pl/pl/strona_glowna/serwis_sportowy/ekstraklasa/index.html').read()

soup = BeautifulSoup(data,'lxml',from_encoding='utf-8')

tables=soup.find_all('table')[2]
table_head=tables.find('thead')
head2=[]
game=[]
games={}
for head in table_head:
    try:
        if len(head.text)>0:
            head2.append(head.text.strip().replace("\n",' '))
    except:
        continue

table_body = tables.find('tbody')
rows=table_body.find_all('tr')
sport='data-gtm-enhanced-ecommerce-sport'
league='data-gtm-enhanced-ecommerce-league'

for tr in rows:
    cols=tr.find_all('td')
    tmp = []
    sport_name = tr.get(sport)
    league_name = tr.get(league)
    additional_info=[sport_name,league_name]
    print "Additional info:"
    print additional_info
    for td in cols:
        try:
            #print ahref[0].text
            #print td.text
            #print td.div.span.a.text
            #print td.text
            if len(td.text)>0 or len(td.text)<=0:
                #print "TD.text"
                #print td.text
                #x=str(td.text.strip().replace("\n",' '))
                x=str(td.text[0:100].strip().replace("\n",' ')) #brzydkie obejście
                #print x
                y=x.find('  ')
                if y>0:
                    z=x[0:y]
                else:
                    z=x
                tmp.append(z)
                #print z
            else:
                print "Nie poszlo:"
                print td
                print td.text.strip()
                continue
            #print i.text
            #print td.div.a.text
            tmp2=tuple(tmp)
        except:
            continue
        #tmp2=tuple(tmp)
    #print tmp
#    print "LEN TMP2"
#    print len(tmp2)
    tmp3=list(tmp2)+additional_info
    game.append(tmp3)
print("/////////////////")
head2=head2[0].replace('  ',' ').replace('  ',' ').split(' ')
head2.append("Sport")
head2.append("League")
#print head2
#print game
#print len(head2)


#for i in game:
#    print i
print head2
print game
x=pd.DataFrame(game, columns=head2)
print x
engine = create_engine('sqlite:///db.sqlite')
x.to_sql('db_fortuna', engine)
#x.to_sql('sqlite:///db_table2', sqlite3)
