#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib.request as urllib2
import sqlite3
import codecs
import logging
import datetime
from collections import defaultdict
from dictionaries import *
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
url = "http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers"
headers={'User-Agent':user_agent,}
#data=urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers)
#response = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers))
data = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers)).read() # The data u need
#data=codecs.open('fortuna.html',mode='r',encoding='utf-8').read()

class football_event:
    soup = BeautifulSoup(data,"html.parser")
    logging.basicConfig(filename='logfile_iforbet.log', level=logging.DEBUG)
    def get_events_mapping(self):
        return self.__events_mapping
    def get_name(self):
        soup = BeautifulSoup(data, "html.parser")
        self.game=soup.find('div',{'class':'event-data'})
        game_teams=self.game.find_all('h2')
        self.home=unify_name(game_teams[0].text,teams,logging)
        self.away=unify_name(game_teams[1].text,teams,logging)
        print(self.game.text)
        print (self.home,self.away)
        #self.raw_date = soup.find('span', {'class': 'betItemDetailDate'}).text
        current_time=datetime.datetime.now()
        self.update_time=str('{:04d}'.format(current_time.year))+'-'+str('{:02d}'.format(current_time.month))+'-'+str('{:02d}'.format(current_time.day))+\
        '-' + str('{:02d}'.format(current_time.hour))+'-'+str('{:02d}'.format(current_time.minute))+'-'+str('{:02d}'.format(current_time.second))
        #full_date = datetime.datetime(current_time.year, int(self.raw_date.split('.')[1]), int(self.raw_date.split('.')[0]),
        #                              int((self.raw_date.split('.')[2]).split(':')[0]), int((self.raw_date.split('.')[2]).split(':')[1]))
        #self.date=str(full_date.year)+'-'+str('{:02d}'.format(full_date.month))+'-'+str('{:02d}'.format(full_date.day))
        #self.hour=str('{:02d}'.format(full_date.hour))+':'+str('{:02d}'.format(full_date.minute))
        #self.home=unify_name(self.game.text.split('|')[2].split('-')[0].strip(),teams,logging)
        #self.away =unify_name(self.game.text.split('|')[2].split('-')[1].strip(),teams,logging)
        #self.sport = self.game.text.split('|')[0].strip()
        #self.league = unify_name(self.game.text.split('|')[1].strip(),leagues,logging)

    def correct_name(self, name):
        try:
            return name.split('(')[1].split(')')[0]
        except:
            return name

    def get_odds(self):
        soup = BeautifulSoup(data, "html.parser")
        self.odds = defaultdict(str)
        tables = soup.find_all('div', {'class': 'games-panel'})

        for table in tables:
            try:
                head = table.find('thead').find_all('th')
                name = head[0].text.strip()
                if name not in self.__events_mapping.keys():
                    logging.warning(self.game.text.strip())
                    logging.warning("Nieznany zaklad: " + name)
                self.odds[self.__events_mapping[name]["name"]] = defaultdict(str)
                odd_tittle = []
                for th in head[1:]:
                    odd_tittle.append(th.text.strip())
                    self.odds[self.__events_mapping[name]["name"]][th.text.strip()]=defaultdict(str)
            except:
                pass
                #logging.warning('Nie ma head')
            rows = table.find('tbody').find_all('tr')
            for row in rows:
                tds = row.find_all('td')
                #wywalalo sie m.in na lidze europejskiej, stad dodany drugi warunek
                if tds[0].text.strip().find('(')>-1 and tds[0].text.strip().find('spotk')==-1:
                    subtable=1
                else:
                    subtable=0
                if subtable==1:
                    subname = self.correct_name(tds[0].text.strip())
                i=0
                odds = []
                for td in tds[1:]:
                    odds.append(td.text.strip())
                    if subtable==1:
                        if KeyError:
                            try:
                                #self.odds[self.__events_mapping[name]["name"]][odd_tittle[i]][subname] = defaultdict(str)
                                self.odds[self.__events_mapping[name]["name"]][odd_tittle[i]][subname] = odds[i]
                            except:
                                #logging.info('Nieznany zaklad'+td.text.strip())
                                pass
                        else:
                            self.odds[self.__events_mapping[name]["name"]][odd_tittle[i]][subname] = odds[i]
                    else:
                        try:
                            self.odds[self.__events_mapping[name]["name"]][odd_tittle[i]] = odds[i]
                        except:
                            #logging.warning('Nieznany zaklad'+td.text.strip())
                            #logging.warning('Tu sie wywalilo'+str(td.text.strip()))
                            pass
                    i = i + 1
                    #for l in len(odds)
                #print("SKLEJONE:",zipped)
                #odd_tittle.append(head.text.strip())
                #if head.text.strip() not in self.__events_mapping.keys():
                #    logging.warning(self.game.text.strip())
                #    logging.warning("Nieznany zaklad: " + head.text.strip())

    def prepare_dict_to_sql(self):
        self.dict_sql=defaultdict(str)
        for i in self.__events_mapping.values():
            if i['name'] not in self.odds.keys():
                self.odds[i['name']]=defaultdict(str)

        #Poprawia na potrzeby ubogich meczy:
        if '+' not in self.odds['goals'].keys():
            self.odds['goals']['+']=defaultdict(str)
        if '-' not in self.odds['goals'].keys():
            self.odds['goals']['-']=defaultdict(str)
        self.dict_sql['home']=self.home
        self.dict_sql['away']=self.away
        self.dict_sql['_1']=self.odds['game']['1']
        self.dict_sql['_0']=self.odds['game']['0']
        self.dict_sql['_2']=self.odds['game']['2']
        self.dict_sql['_10']=self.odds['game']['10']
        self.dict_sql['_02']=self.odds['game']['02']
        self.dict_sql['_12']=self.odds['game']['12']
        #self.dict_sql['data']=self.date.split(' ')[1].split('.')[2]+'-'+self.date.split(' ')[1].split('.')[1]+'-'+self.date.split(' ')[1].split('.')[0]
        self.dict_sql['Sport']=self.sport
        self.dict_sql['League']=self.league
        self.dict_sql['data']=self.date
        self.dict_sql['hour']=self.hour
        self.dict_sql['update_time']=self.update_time
        self.dict_sql['o_35'] = self.odds['goals']['+']['3.5']
        #self.dict_sql['country']=self.
        self.dict_sql['dnb_1']=self.odds['dnb']['1']
        self.dict_sql['dnb_2']=self.odds['dnb']['2']
        self.dict_sql['o_05'] = self.odds['goals']['+']['0.5']
        self.dict_sql['u_05'] = self.odds['goals']['-']['0.5']
        self.dict_sql['o_15'] = self.odds['goals']['+']['1.5']
        self.dict_sql['u_15'] = self.odds['goals']['-']['1.5']
        self.dict_sql['o_25'] = self.odds['goals']['+']['2.5']
        self.dict_sql['u_25'] = self.odds['goals']['-']['2.5']
        self.dict_sql['u_35'] = self.odds['goals']['-']['3.5']
        self.dict_sql['o_45'] = self.odds['goals']['+']['4.5']
        self.dict_sql['u_45'] = self.odds['goals']['-']['4.5']
        self.dict_sql['o_55'] = self.odds['goals']['+']['5.5']
        self.dict_sql['u_55'] = self.odds['goals']['-']['5.5']
        self.dict_sql['o_65'] = self.odds['goals']['+']['6.5']
        self.dict_sql['u_65'] = self.odds['goals']['-']['6.5']
        self.dict_sql['o_75'] = self.odds['goals']['+']['7.5']
        self.dict_sql['u_75'] = self.odds['goals']['-']['7.5']
        self.dict_sql['o_85'] = self.odds['goals']['+']['8.5']
        self.dict_sql['u_85'] = self.odds['goals']['-']['8.5']
        self.dict_sql['o_95'] = self.odds['goals']['+']['9.5']
        self.dict_sql['u_95'] = self.odds['goals']['-']['9.5']
        self.dict_sql['ht_ft_11'] = self.odds['half/end'][ '1/1']
        self.dict_sql['ht_ft_1x'] = self.odds['half/end'][ '1/0']
        self.dict_sql['ht_ft_2x'] = self.odds['half/end'][ '2/0']
        self.dict_sql['ht_ft_21'] = self.odds['half/end'][ '2/1']
        self.dict_sql['ht_ft_22'] = self.odds['half/end'][ '2/2']
        self.dict_sql['ht_ft_x1'] = self.odds['half/end'][ '0/1']
        self.dict_sql['ht_ft_x2'] = self.odds['half/end'][ '0/2']
        self.dict_sql['ht_ft_12'] = self.odds['half/end'][ '1/2']
        self.dict_sql['ht_ft_xx'] = self.odds['half/end'][ '0/0']
        self.dict_sql['_1st_half_1']= self.odds['1st_half'][ '1']
        self.dict_sql['_1st_half_x'] = self.odds['1st_half'][ '0']
        self.dict_sql['_1st_half_2'] = self.odds['1st_half'][ '2']
        self.dict_sql['_1st_half_10'] = self.odds['1st_half']['10']
        self.dict_sql['_1st_half_02'] = self.odds['1st_half']['02']
        self.dict_sql['_1st_half_12'] = self.odds['1st_half']['12']
        self.dict_sql['eh-1_1'] = self.odds['eh-1']['1']
        self.dict_sql['eh-1_x2'] = self.odds['eh-1']['02']
        self.dict_sql['u_25_1'] = self.odds['game/goals']['1/-2.5']
        self.dict_sql['o_25_1'] = self.odds['game/goals']['1/+2.5']
        self.dict_sql['u_25_x'] = self.odds['game/goals']['0/-2.5']
        self.dict_sql['o_25_x'] = self.odds['game/goals']['0/+2.5']
        self.dict_sql['u_25_2'] = self.odds['game/goals']['2/-2.5']
        self.dict_sql['o_25_2'] = self.odds['game/goals']['2/+2.5']
        self.dict_sql['u_35_1'] = self.odds['game/goals']['1/-3.5']
        self.dict_sql['o_35_1'] = self.odds['game/goals']['1/+3.5']
        self.dict_sql['u_35_x'] = self.odds['game/goals']['0/-3.5']
        self.dict_sql['o_35_x'] = self.odds['game/goals']['0/+3.5']
        self.dict_sql['u_35_2'] = self.odds['game/goals']['2/-3.5']
        self.dict_sql['o_35_2'] = self.odds['game/goals']['2/+3.5']
        #self.dict_sql['1_st_goal_1'] = self.odds['1st_goal'][sehome]
        #self.dict_sql['1_st_goal_2'] = self.odds['1st_goal'][away]
        #self.dict_sql['1_st_goal_0'] = self.odds['1st_goal']['nikt']

        return self.dict_sql
    def save_to_db(meczyk):
        database_name = 'db.sqlite'
        db = sqlite3.connect(database_name)
        home = meczyk.home
        print ("Home:", home)
        away = meczyk.away
        print ("Away:", away)
        date = meczyk.date
        print ("Date:", date)
        #sqldate=meczyk.date.split(' ')[1].split('.')[2]+'-'+meczyk.date.split(' ')[1].split('.')[1]+'-'+meczyk.date.split(' ')[1].split('.')[0]
        table='"db_fortuna"'
        columns_string = '("' + '","'.join(meczyk.dict_sql.keys()) + '")'
        values_string = '("' + '","'.join(map(str, meczyk.dict_sql.values())) + '")'
        try:
            sql_command="DELETE FROM %s WHERE home=%s and away=%s and data=%s" % (table,"'"+home+"'","'"+away+"'","'"+date+"'")
            print ("SQL COMMAND:",sql_command)
            db.execute(sql_command)
            print ("USUNIĘTO")
        except:
            pass
        sql = """INSERT INTO %s %s
             VALUES %s""" % (table, columns_string, values_string)
        print (sql)
        db.execute(sql)
        db.commit()

    def __init__(self, events_mapping_fortuna):
        #self.__events_mapping=events_mapping_fortuna
        self.get_name()
        #self.get_odds()
        #self.prepare_dict_to_sql()
        #print ("ODDS:",self.odds)


data = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers)).read() # The data u need
meczyk=football_event(events_mapping_fortuna)
#meczyk.prepare_dict_to_sql()
##meczyk.save_to_db()
exit()
comment="""


       """
sites=[
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/premier-league-premiership',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-europy',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/kwalifikacje-mistrzostw-swiata-europa',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/kwalifikacje-mistrzostw-swiata-ameryka-poludniowa',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/kwalifikacje-mistrzostw-swiata-azja',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/kwalifikacje-mistrzostw-swiata-afryka',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/spotkania-towarzyskie',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/puchar-polski',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/ekstraklasa',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-mistrzow',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/primera-division',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/1-liga-polska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/2-liga-polska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-austriacka',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-belgijska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-bialoruska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-brazylijska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-bulgarska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-chilijska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-chorwacka',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-czeska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-dunska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/ligue-1',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-grecka',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/eredivisie',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/bundesliga',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-portugalska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-rumunska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-rosyjska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-slowacka',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-serbska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-szkocka',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-szwedzka',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-szwajcarska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-turecka',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-walijska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/liga-wegierska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/serie-a',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/2-liga-angielska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/2-liga-hiszpanska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/bundesliga-2',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/2-liga-wloska',
       'https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/ligue-2',
       ]
sites2=['https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/puchar-polski']
for site in sites:
    try:
        strona=urllib2.urlopen(site).read()
    except:
        print (site)
        logging.WARNING("404: ")
        continue
    soup = BeautifulSoup(strona, "html.parser")
    more_bets=soup.find('table',{'class':'bet_table'}).find_all('span', {'class': 'bet_item_main_text'})
    #print ("MORE BETS:", more_bets)
    names=[]
    for a in more_bets:
        #print ("A: ",a)
        link=a.find('a', href = True)
        print ("LINK: ", link['href'])
        #https: // www.efortuna.pl / pl / strona_glowna / pilka - nozna / 2017 - 0
        #8 - 18 - lechia - g - ---sandecja - n - s - -14014159
        try:
            data=urllib2.urlopen('https://www.efortuna.pl'+link['href']).read()
            meczyk = football_event(events_mapping_fortuna)
            names.append(meczyk.home)
            names.append(meczyk.away)
            #meczyk=football_event()
            meczyk.save_to_db()
        except:
            logging.WARNING("ERROR dla: "+link['href'])
            continue

