import codecs
from bs4 import BeautifulSoup
from dictionaries import *
from collections import defaultdict
import logging
import datetime
import urllib.request as urllib2
import sys
import re
from urllib import parse

def read_coupon(adres):
#adres1='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id=OTk5MDQ3NzA4NDg0MzMwMDp5D0b%2BhWJvXFEHkRg%3D&kind=MAIN'
#adres2='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id=OTQxMzI3NzA5MzUzMTEwMDrsspzQo7BGblqFRrA%3D&kind=MAIN'
#adres='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id=Mzk5MDM3NzA5NDA1MjkwMDqZs952+IomQH8BbOE%3D&kind=MAIN'
    logging.basicConfig(filename='logfile_fortuna_read_coupon.log', level=logging.DEBUG)
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib2.Request(adres, None, headers)
    kupon=urllib2.urlopen(request).read()
    #kupon=urllib2.urlopen(adres).read()
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
        #print (type+'_'+typ)
        znajdz_typ = unify_name(type +'_'+ typ, sql_map_fortuna, logging)
     #   print (znajdz_typ+"::::::::::::::::")
        ####wyciaga z bazy:
        #print (home, away)
        one_event=[home,away,znajdz_typ,type+"_"+typ]
        #one_event = [home, away, znajdz_typ]
        #print (home,away,znajdz_typ)
        all_events.append(one_event)
    for el in all_events:
        print (el,sep=';',end=','+'\n')
        #for el2 in el:
         #   print(el2,sep=',',end=',')

    return (all_events)
coupon_id=sys.argv[1]
url = sys.argv[1]
id=re.findall("id=.*&", coupon_id, flags=0)
if len(re.findall('http',url))>0:
    kupon=parse.parse_qs(parse.urlparse(url).query)['ticket_id'][0]
else:
    kupon=url
#adres='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id='+kupon+'&kind=MAIN'
adres='https://www.efortuna.pl/pl/strona_glowna/nahled_tiketu/index.html?ticket_id='+kupon+'=&preview=hide_code'
#print(read_coupon(adres))
read_coupon(adres)
