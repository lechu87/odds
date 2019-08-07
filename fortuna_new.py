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
import urllib.parse

data=urllib2.urlopen('https://www.efortuna.pl/pl/strona_glowna/serwis_sportowy/ekstraklasa/index.html').read()
#data=codecs.open('fortuna.html',mode='r',encoding='utf-8').read()

class football_event:
    soup = BeautifulSoup(data,"html.parser")
    logging.basicConfig(filename='logfile_fortuna.log', level=logging.DEBUG)
    def get_events_mapping(self):
        return self.__events_mapping
    def get_name(self):
        soup = BeautifulSoup(data, "html.parser")
        self.game=soup.find('title')
        print (soup.html.head.title)
        #self.game=soup.html.head.tiitle
        print(self.game.text)
        #self.raw_date = soup.find('span', {'class': 'betItemDetailDate'}).text
        current_time=datetime.datetime.now()
        self.update_time=str('{:04d}'.format(current_time.year))+'-'+str('{:02d}'.format(current_time.month))+'-'+str('{:02d}'.format(current_time.day))+\
        '-' + str('{:02d}'.format(current_time.hour))+'-'+str('{:02d}'.format(current_time.minute))+'-'+str('{:02d}'.format(current_time.second))
        #full_date = datetime.datetime(current_time.year, int(self.raw_date.split('.')[1]), int(self.raw_date.split('.')[0]),
         #                             int((self.raw_date.split('.')[2]).split(':')[0]), int((self.raw_date.split('.')[2]).split(':')[1]))
        #self.date=str(full_date.year)+'-'+str('{:02d}'.format(full_date.month))+'-'+str('{:02d}'.format(full_date.day))
        #self.hour=str('{:02d}'.format(full_date.hour))+':'+str('{:02d}'.format(full_date.minute))
        self.home=unify_name(self.game.text.split('|')[0].split('-')[0].strip(),teams,logging)
        self.away =unify_name(self.game.text.split('|')[0].split('-')[1].strip(),teams,logging)
        self.sport = self.game.text.split('|')[2].strip()
        self.league = unify_name(self.game.text.split('|')[1].strip(),leagues,logging)
        print (self.league)
    def correct_name(self, name):
        try:
            return name.split('(')[1].split(')')[0]
        except:
            return name

    def get_odds(self):
        soup = BeautifulSoup(data, "html.parser")
        self.odds = defaultdict(str)
        def getText(parent):
            return ''.join(parent.find_all(text=True, recursive=False)).strip()

        tables = soup.find('ul', {'class': 'events-list'}).find_all('li',{'class':'event'})
#        print(tables)
        for i in tables:
            name=getText(i).strip().lower()
            tip=i.find_all('span',{'class':'tip'})
            odd=i.find_all('span',{'class':'odd'})
            rows=i.find_all('div',{'class':'row'})
            #for row in rows:
            #    tips=row.find_all('span')
 #           print("name:",name,"tip: ",tip,"odd ",odd)
            if name not in self.__events_mapping.keys():
#                logging.warning(self.game.text.strip())
#                logging.warning("Nieznany zaklad: " + name)
                continue
            if self.__events_mapping[name]["name"] not in self.odds:
                     self.odds[self.__events_mapping[name]["name"]] = defaultdict(str)
            for i in range(0,len(tip)):
                self.odds[self.__events_mapping[name]["name"]][tip[i].text.strip()]=odd[i].text.strip()
        # for table in tables:
        #     try:
        #         head = table.find('thead').find_all('th')
        #         name = head[0].text.strip()
        #         #print ("NAME",name)
        #         if name not in self.__events_mapping.keys():
        #             logging.warning(self.game.text.strip())
        #             logging.warning("Nieznany zaklad: " + name)
        #         if self.__events_mapping[name]["name"] not in self.odds:
        #             self.odds[self.__events_mapping[name]["name"]] = defaultdict(str)
        #         odd_tittle = []
        #         for th in head[1:]:
        #             #print ("TH.TEXT.STRIP:", th.text.strip())
        #             odd_tittle.append(th.text.strip())
        #             self.odds[self.__events_mapping[name]["name"]][th.text.strip()]=defaultdict(str)
        #     except:
        #         pass
        #         #logging.warning('Nie ma head')
        #     rows = table.find('tbody').find_all('tr')
        #     for row in rows:
        #         tds = row.find_all('td')
        #         #print ("TD.TEXT.STRIP:", tds[0].a.text.strip())
        #         #wywalalo sie m.in na lidze europejskiej, stad dodany drugi warunek
        #         if tds[0].text.strip().find('(')>-1 and (tds[0].text.strip().find('spotk')==-1 or tds[0].text.strip().find('mecz')==-1) and len(tds[0].text.strip())<50:
        #             subtable=1
        #         else:
        #             subtable=0
        #         if subtable==1:
        #             subname = self.correct_name(tds[0].text.strip())
        #             #print ("TDS0:",tds[0].a.text.strip())
        #
        #         i=0
        #         odds = []
        #         for td in tds[1:]:
        #             odds.append(td.text.strip())
        #             #print ("TD.TEXT.STRIP:",td.text.strip())
        #             if subtable==1:
        #                 if KeyError:
        #                     try:
        #                         #self.odds[self.__events_mapping[name]["name"]][odd_tittle[i]][subname] = defaultdict(str)
        #                         self.odds[self.__events_mapping[name]["name"]][odd_tittle[i]][subname] = odds[i]
        #                     except:
        #                         #logging.info('Nieznany zaklad'+td.text.strip())
        #                         pass
        #                 else:
        #                     self.odds[self.__events_mapping[name]["name"]][odd_tittle[i]][subname] = odds[i]
        #             else:
        #                 try:
        #                     self.odds[self.__events_mapping[name]["name"]][odd_tittle[i]] = odds[i]
        #                 except:
        #                     #logging.warning('Nieznany zaklad'+td.text.strip())
        #                     #logging.warning('Tu sie wywalilo'+str(td.text.strip()))
        #                     pass
        #             i = i + 1
        #             #for l in len(odds)
        #         #print("SKLEJONE:",zipped)
        #         #odd_tittle.append(head.text.strip())
        #         #if head.text.strip() not in self.__events_mapping.keys():
        #         #    logging.warning(self.game.text.strip())
        #         #    logging.warning("Nieznany zaklad: " + head.text.strip())

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
        if '+' not in self.odds['corners_number'].keys():
            self.odds['corners_number']['+']=defaultdict(str)
        if '-' not in self.odds['corners_number'].keys():
            self.odds['corners_number']['-']=defaultdict(str)
        self.dict_sql['home']=self.home
        self.dict_sql['away']=self.away
        self.dict_sql['fortuna_game_1']=self.odds['game']['1']
        self.dict_sql['fortuna_game_0']=self.odds['game']['0']
        self.dict_sql['fortuna_game_2']=self.odds['game']['2']
        self.dict_sql['fortuna_game_10']=self.odds['game']['10']
        self.dict_sql['fortuna_game_02']=self.odds['game']['02']
        self.dict_sql['fortuna_game_12']=self.odds['game']['12']
        #self.dict_sql['fortuna_data']=self.date.split(' ')[1].split('.')[2]+'-'+self.date.split(' ')[1].split('.')[1]+'-'+self.date.split(' ')[1].split('.')[0]
        #self.dict_sql['Sport']=self.sport
        self.dict_sql['League']=self.league
        #self.dict_sql['data']=self.date
        #self.dict_sql['hour']=self.hour
        self.dict_sql['fortuna_update_time']=self.update_time
        self.dict_sql['fortuna_o_35'] = self.odds['goals']['+ (3.5)']
        #self.dict_sql['fortuna_country']=self.
        self.dict_sql['fortuna_dnb_1']=self.odds['dnb']['1']
        self.dict_sql['fortuna_dnb_2']=self.odds['dnb']['2']
        self.dict_sql['fortuna_o_05'] = self.odds['goals']['+ (0.5)']
        self.dict_sql['fortuna_u_05'] = self.odds['goals']['- (0.5)']
        self.dict_sql['fortuna_o_15'] = self.odds['goals']['+ (1.5)']
        self.dict_sql['fortuna_u_15'] = self.odds['goals']['- (1.5)']
        self.dict_sql['fortuna_o_25'] = self.odds['goals']['+ (2.5)']
        self.dict_sql['fortuna_u_25'] = self.odds['goals']['- (2.5)']
        self.dict_sql['fortuna_u_35'] = self.odds['goals']['- (3.5)']
        self.dict_sql['fortuna_o_45'] = self.odds['goals']['+ (4.5)']
        self.dict_sql['fortuna_u_45'] = self.odds['goals']['- (4.5)']
        self.dict_sql['fortuna_o_55'] = self.odds['goals']['+ (5.5)']
        self.dict_sql['fortuna_u_55'] = self.odds['goals']['- (5.5)']
        self.dict_sql['fortuna_o_65'] = self.odds['goals']['+ (6.5)']
        self.dict_sql['fortuna_u_65'] = self.odds['goals']['- (6.5)']
        self.dict_sql['fortuna_o_75'] = self.odds['goals']['+ (7.5)']
        self.dict_sql['fortuna_u_75'] = self.odds['goals']['- (7.5)']
        self.dict_sql['fortuna_o_85'] = self.odds['goals']['+ (8.5)']
        self.dict_sql['fortuna_u_85'] = self.odds['goals']['- (8.5)']
        self.dict_sql['fortuna_o_95'] = self.odds['goals']['+ (9.5)']
        self.dict_sql['fortuna_u_95'] = self.odds['goals']['- (9.5)']
        self.dict_sql['fortuna_ht_ft_11'] = self.odds['half/end'][ '1/1']
        self.dict_sql['fortuna_ht_ft_1x'] = self.odds['half/end'][ '1/0']
        self.dict_sql['fortuna_ht_ft_2x'] = self.odds['half/end'][ '2/0']
        self.dict_sql['fortuna_ht_ft_21'] = self.odds['half/end'][ '2/1']
        self.dict_sql['fortuna_ht_ft_22'] = self.odds['half/end'][ '2/2']
        self.dict_sql['fortuna_ht_ft_x1'] = self.odds['half/end'][ '0/1']
        self.dict_sql['fortuna_ht_ft_x2'] = self.odds['half/end'][ '0/2']
        self.dict_sql['fortuna_ht_ft_12'] = self.odds['half/end'][ '1/2']
        self.dict_sql['fortuna_ht_ft_xx'] = self.odds['half/end'][ '0/0']
        self.dict_sql['fortuna_first_half_1']= self.odds['1st_half'][ '1']
        self.dict_sql['fortuna_first_half_x'] = self.odds['1st_half'][ '0']
        self.dict_sql['fortuna_first_half_2'] = self.odds['1st_half'][ '2']
        self.dict_sql['fortuna_first_half_10'] = self.odds['1st_half']['10']
        self.dict_sql['fortuna_first_half_02'] = self.odds['1st_half']['02']
        self.dict_sql['fortuna_first_half_12'] = self.odds['1st_half']['12']
        self.dict_sql['fortuna_eh_min_1_1'] = self.odds['eh-1']['1']
        self.dict_sql['fortuna_eh_min_1_x2'] = self.odds['eh-1']['02']
        self.dict_sql['fortuna_eh_min_1_2'] = self.odds['eh-1']['2']
        self.dict_sql['fortuna_eh_min_1_x'] = self.odds['eh-1']['0']
        self.dict_sql['fortuna_eh_min_1_x1'] = self.odds['eh-1']['10']
        self.dict_sql['fortuna_eh_plus_1_1'] = self.odds['eh+1']['1']
        self.dict_sql['fortuna_eh_plus_1_x2'] = self.odds['eh+1']['02']
        self.dict_sql['fortuna_eh_plus_1_2'] = self.odds['eh+1']['2']
        self.dict_sql['fortuna_eh_plus_1_x'] = self.odds['eh+1']['0']
        self.dict_sql['fortuna_eh_plus_1_x1'] = self.odds['eh+1']['10']
        self.dict_sql['fortuna_u_15_1'] = self.odds['game/goals']['1/-1.5']
        self.dict_sql['fortuna_o_15_1'] = self.odds['game/goals']['1/+1.5']
        self.dict_sql['fortuna_u_25_1'] = self.odds['game/goals']['1/-2.5']
        self.dict_sql['fortuna_o_25_1'] = self.odds['game/goals']['1/+2.5']
        self.dict_sql['fortuna_u_25_x'] = self.odds['game/goals']['0/-2.5']
        self.dict_sql['fortuna_o_25_x'] = self.odds['game/goals']['0/+2.5']
        self.dict_sql['fortuna_u_25_2'] = self.odds['game/goals']['2/-2.5']
        self.dict_sql['fortuna_o_25_2'] = self.odds['game/goals']['2/+2.5']
        self.dict_sql['fortuna_u_15_2'] = self.odds['game/goals']['2/-1.5']
        self.dict_sql['fortuna_o_15_2'] = self.odds['game/goals']['2/+1.5']
        self.dict_sql['fortuna_u_35_1'] = self.odds['game/goals']['1/-3.5']
        self.dict_sql['fortuna_o_35_1'] = self.odds['game/goals']['1/+3.5']
        self.dict_sql['fortuna_u_35_x'] = self.odds['game/goals']['0/-3.5']
        self.dict_sql['fortuna_o_35_x'] = self.odds['game/goals']['0/+3.5']
        self.dict_sql['fortuna_u_35_2'] = self.odds['game/goals']['2/-3.5']
        self.dict_sql['fortuna_o_35_2'] = self.odds['game/goals']['2/+3.5']
        self.dict_sql['fortuna_u_15_x'] = self.odds['game/goals']['0/-1.5']
        self.dict_sql['fortuna_o_15_x'] = self.odds['game/goals']['0/+1.5']
        self.dict_sql['fortuna_btts_1'] = self.odds['game/btts']['1/Tak']
        self.dict_sql['fortuna_btts_2'] = self.odds['game/btts']['2/Tak']
        self.dict_sql['fortuna_btts_x'] = self.odds['game/btts']['0/Tak']
        self.dict_sql['fortuna_btts_no_1'] = self.odds['game/btts']['1/Nie']
        self.dict_sql['fortuna_btts_no_2'] = self.odds['game/btts']['2/Nie']
        self.dict_sql['fortuna_btts_no_x'] = self.odds['game/btts']['0/Nie']
        self.dict_sql['fortuna_btts_yes'] = self.odds['btts']['Tak']
        self.dict_sql['fortuna_btts_no'] = self.odds['btts']['Nie']
        self.dict_sql['fortuna_corners_o_65'] = self.odds['corners_number']['+ (6.5)']
        self.dict_sql['fortuna_corners_u_65'] = self.odds['corners_number']['- (6.5)']
        self.dict_sql['fortuna_corners_o_75'] = self.odds['corners_number']['+ (7.5)']
        self.dict_sql['fortuna_corners_u_75'] = self.odds['corners_number']['- (7.5)']
        self.dict_sql['fortuna_corners_o_85'] = self.odds['corners_number']['+ (8.5)']
        self.dict_sql['fortuna_corners_u_85'] = self.odds['corners_number']['- (8.5)']
        self.dict_sql['fortuna_corners_o_95'] = self.odds['corners_number']['+ (9.5)']
        self.dict_sql['fortuna_corners_u_95'] = self.odds['corners_number']['- (9.5)']
        self.dict_sql['fortuna_corners_o_105'] = self.odds['corners_number']['+ (10.5)']
        self.dict_sql['fortuna_corners_u_105'] = self.odds['corners_number']['- (10.5)']
        self.dict_sql['fortuna_corners_o_115'] = self.odds['corners_number']['+ (11.5)']
        self.dict_sql['fortuna_corners_u_115'] = self.odds['corners_number']['- (11.5)']
        self.dict_sql['fortuna_corners_o_125'] = self.odds['corners_number']['+ (12.5)']
        self.dict_sql['fortuna_corners_u_125'] = self.odds['corners_number']['- (12.5)']
        self.dict_sql['fortuna_corners_o_135'] = self.odds['corners_number']['+ (13.5)']
        self.dict_sql['fortuna_corners_u_135'] = self.odds['corners_number']['- (13.5)']
        self.dict_sql['fortuna_corners_o_145'] = self.odds['corners_number']['+ (14.5)']
        self.dict_sql['fortuna_corners_u_145'] = self.odds['corners_number']['- (14.5)']
        self.dict_sql['fortuna_corners_o_155'] = self.odds['corners_number']['+ (15.5)']
        self.dict_sql['fortuna_corners_u_155'] = self.odds['corners_number']['- (15.5)']
        self.dict_sql['fortuna_corners_o_165'] = self.odds['corners_number']['+ (16.5)']
        self.dict_sql['fortuna_corners_u_165'] = self.odds['corners_number']['- (16.5)']
        self.dict_sql['fortuna_corners_o_175'] = self.odds['corners_number']['+ (17.5)']
        self.dict_sql['fortuna_corners_u_175'] = self.odds['corners_number']['- (17.5)']
        self.dict_sql['fortuna_first_goal_1'] = self.odds['1st_goal']['1']
        self.dict_sql['fortuna_first_goal_2'] = self.odds['1st_goal']['2']
        self.dict_sql['fortuna_first_goal_0'] = self.odds['1st_goal']['Nikt']

        return self.dict_sql
    def save_to_db(meczyk):
        database_name = 'db.sqlite'
        db = sqlite3.connect(database_name)
        home = meczyk.home
        print ("Home:", home)
        away = meczyk.away
        print ("Away:", away)
        #date = meczyk.date
        #print ("Date:", date)
        #sqldate=meczyk.date.split(' ')[1].split('.')[2]+'-'+meczyk.date.split(' ')[1].split('.')[1]+'-'+meczyk.date.split(' ')[1].split('.')[0]
        table='"db_bets"'
        league=meczyk.league
        columns_string = '("' + '","'.join(meczyk.dict_sql.keys()) + '")'
        values_string = '("' + '","'.join(map(str, meczyk.dict_sql.values())) + '")'
        try:
            #sql_command="DELETE FROM %s WHERE home=%s and away=%s and data=%s" % (table,"'"+home+"'","'"+away+"'","'"+date+"'")
            sql_command = "DELETE FROM %s WHERE home=%s and away=%s and League=%s" % (
            table, "'" + home + "'", "'" + away + "'", "'" + league + "'")

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
        self.__events_mapping=events_mapping_fortuna
        self.get_name()
        self.get_odds()
        print ("ODDS:",self.odds)
        self.prepare_dict_to_sql()



#data=urllib2.urlopen('https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/2019-03-17-wisla-k----cracovia-17273234').read()
#url='https://gm.efortuna.pl/zaklady_bukmacherskie/piłka-nozna/1-niemcy/wolfsburg-eint-frankfurt-MPL17434830'

#url = urllib.parse.urlsplit(url)
#url = list(url)
#url[2] = urllib.parse.quote(url[2])
#url = urllib.parse.urlunsplit(url)
#data=urllib2.urlopen(url).read()
#meczyk=football_event(events_mapping_fortuna)
#print (meczyk.odds)
#meczyk.prepare_dict_to_sql()
#save_to_db_common(meczyk,league=meczyk.league)
#exit()
sites3=['https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/ekstraklasa-polska']
sites=[
       'https://www.efortuna.pl/pl/strona_glowna/ms-pilka-nozna',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-anglia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/liga-europy',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/kwalifikacje-mistrzostw-swiata-europa',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/kwalifikacje-mistrzostw-swiata-ameryka-poludniowa',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/kwalifikacje-mistrzostw-swiata-azja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/kwalifikacje-mistrzostw-swiata-afryka',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/spotkania-towarzyskie',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/polska-puchar',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/ekstraklasa-polska',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/liga-mistrzow',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-hiszpania',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/fortuna-1-liga-polska',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/2-polska',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-austria',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-belgia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-bialorus',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-brazylia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-bulgaria',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-chile',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-chorwacja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-czechy',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-dania',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-francja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-grecja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-holandia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-niemcy',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-portugalia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-rumunia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-rosja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-slowacja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-serbia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-szkocja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-szwecja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-szwajcaria',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-turcja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-walia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-wegry',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/1-wlochy',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/2-anglia',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/2-hiszpania',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/2-niemcy',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/2-wlochy',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/2-francja',
       'https://gm.efortuna.pl/zaklady_bukmacherskie/pi%C5%82ka-nozna/liga-narodow-uefa',

       ]
sites2=['https://www.efortuna.pl/pl/strona_glowna/pilka-nozna/ekstraklasa']
for site in sites:
    try:
        strona=urllib2.urlopen(site).read()
    except:
        print (site)
        logging.WARNING("404: ")
        continue
    soup = BeautifulSoup(strona, "html.parser")
    try:
        more_bets=soup.find('ul',{'class':'events-list'}).find_all('li', {'class': 'event'})
    except:
        continue
#    print ("MORE BETS:", more_bets)
    names=[]
    for a in more_bets:
        #print ("A: ",a)
        #https: // www.efortuna.pl / pl / strona_glowna / pilka - nozna / 2017 - 0
        #8 - 18 - lechia - g - ---sandecja - n - s - -14014159
        try:
            link = a.find('a', href=True)
            print ("LINK: ", link['href'])
            print ('https://gm.efortuna.pl/'+link['href'])
            url='https://gm.efortuna.pl/'+link['href']
            url = urllib.parse.urlsplit(url)
            url = list(url)
            url[2] = urllib.parse.quote(url[2])
            url = urllib.parse.urlunsplit(url)
            data=urllib2.urlopen(url).read()
            print("przeczytane")
            meczyk = football_event(events_mapping_fortuna)
            names.append(meczyk.home)
            names.append(meczyk.away)
           #meczyk=football_event()
            save_to_db_common(meczyk, league=meczyk.league)
            #save_to_db_common(meczyk,"'"+meczyk.date+"'")
            #meczyk.save_to_db()
        except:
            logging.warning("ERROR dla: "+str(link['href']))
            continue


