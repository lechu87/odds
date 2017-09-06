#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import pprint
import urllib.request as urllib2
import sqlite3
import codecs
import logging
import datetime
from collections import defaultdict
from dictionaries import *
import re
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
        self.raw_home = game_teams[0].text
        self.raw_away = game_teams[1].text
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

    events_mapping_iforbet = defaultdict(str)
    events_mapping_iforbet = {
        "1X2": {"name": "game"},
        "Remis - nie ma zakładu (remis=zwrot)": {"name": "dnb"},
        "Podwójna szansa": {"name": "dc"},
        "Strzeli pierwszego gola": {"name": "1st_goal"},
        "Strzeli ostatniego gola": {"name": "last_goal"},
        "Wynik do przerwy/Wynik końcowy": {"name": "half/end"},
        'Dokładny wynik': {"name": "cs"},
        "Obie drużyny strzelą bramkę": {"name": "btts"},
        "Zdobędzie 1. gola w 1 połowie": {"name": "1st_goal_1st_team_1st_half"},
        "Zdobędzie 1. gola w 2 połowie": {"name": "1st_goal_1st_team_2nd_half"},
        '1 wygra do zera': {"name": "1st_team_win_to_0"},
        '2 wygra do zera': {"name": "2nd_team_win_to_0"},
        '10 minuta spotkania': {"name": "10min"},
        "Pierwsze 10 minut - wynik":{"name":"10min"},
        "Liczba goli": {"name": "goals"},
        "Drużyna ze zdobyczą bramkową":{"name":"teams_to_score"},
        "Różnica zwycięstwa":{"name":"win_diff"},
        "1 strzeli / nie strzeli":{"name": "1st_team_to_score"},
        "2 strzeli / nie strzeli": {"name": "2nd_team_to_score"},
        "Wynik 1 połowy": {"name": "1st_half"},
        "Podwójna szansa - 1 połowa": {"name": "1st_half_dc"},
        "Obie drużyny strzelą w 1. połowie": {"name": "1st_half_btts"},
        'Dokładny wynik po 1 połowie': {"name": "1st_half_cs"},
        "Liczba goli w 1 połowie": {"name": "1st_half_goals"},
        "Remis nie ma zakładu - 1 połowa": {"name": "1st_half_dnb"},
        "Wynik 2 połowy": {"name": "2nd_half"},
        "Podwójna szansa - 2 połowa": {"name": "2nd_half_dc"},
        "Poniżej/Powyżej x gola w 2 połowie": {"name": "2nd_half_goals"},
        "Obie drużyny strzelą w 2. połowie": {"name": "1st_half_btts"},
        "Liczba goli w 2 połowie":{"name":"2nd_half_goals"},
        "Remis nie ma zakładu - 2 połowa": {"name": "2nd_half_dnb"},
        "Poniżej/Powyżej x goli w 1 połowie" : {"name":"1st_half_goals"},
        "Poniżej/Powyżej x goli":{"name":"goals"},
        "Powyżej 1.5 gola w obu połowach":{"name":"o15_both_half"},
        "Poniżej 1.5 gola w obu połowach": {"name": "u15_both_half"},
        "1 Poniżej/Powyżej 1.5 gola":{"name":"1_o15"},
        "1 Poniżej/Powyżej 0.5 gola": {"name": "1_o05"},
        "1 Poniżej/Powyżej 2.5 gola": {"name": "1_o25"},
        "1 Poniżej/Powyżej 3.5 gola": {"name": "1_o35"},
        "1 Poniżej/Powyżej 4.5 gola": {"name": "1_o45"},
        "2 Poniżej/Powyżej 1.5 gola": {"name": "2_o15"},
        "2 Poniżej/Powyżej 0.5 gola": {"name": "2_o05"},
        "2 Poniżej/Powyżej 2.5 gola": {"name": "2_o25"},
        "2 Poniżej/Powyżej 3.5 gola": {"name": "2_o35"},
        "2 Poniżej/Powyżej 4.5 gola": {"name": "2_o45"},
        "1 Poniżej/Powyżej 0.5 gola w 1 połowie":{"name":"1_o05_1st_half"},
        "1 Poniżej/Powyżej 1.5 gola w 1 połowie": {"name": "1_o15_1st_half"},
        "1 Poniżej/Powyżej 2.5 gola w 1 połowie": {"name": "1_o25_1st_half"},
        "1 Poniżej/Powyżej 3.5 gola w 1 połowie": {"name": "1_o35_1st_half"},
        "1 Poniżej/Powyżej 4.5 gola w 1 połowie": {"name": "1_o45_1st_half"},
        "2 Poniżej/Powyżej 0.5 gola w 1 połowie": {"name": "2_o05_1st_half"},
        "2 Poniżej/Powyżej 1.5 gola w 1 połowie": {"name": "2_o15_1st_half"},
        "2 Poniżej/Powyżej 2.5 gola w 1 połowie": {"name": "2_o25_1st_half"},
        "2 Poniżej/Powyżej 3.5 gola w 1 połowie": {"name": "2_o35_1st_half"},
        "2 Poniżej/Powyżej 4.5 gola w 1 połowie": {"name": "2_o45_1st_half"},
        "1 Poniżej/Powyżej 0.5 gola w 2 połowie": {"name": "1_o05_2nd_half"},
        "1 Poniżej/Powyżej 1.5 gola w 2 połowie": {"name": "1_o15_2nd_half"},
        "1 Poniżej/Powyżej 2.5 gola w 2 połowie": {"name": "1_o25_2nd_half"},
        "1 Poniżej/Powyżej 3.5 gola w 2 połowie": {"name": "1_o35_2nd_half"},
        "1 Poniżej/Powyżej 4.5 gola w 2 połowie": {"name": "1_o45_2nd_half"},
        "2 Poniżej/Powyżej 0.5 gola w 2 połowie": {"name": "2_o05_2nd_half"},
        "2 Poniżej/Powyżej 1.5 gola w 2 połowie": {"name": "2_o15_2nd_half"},
        "2 Poniżej/Powyżej 2.5 gola w 2 połowie": {"name": "2_o25_2nd_half"},
        "2 Poniżej/Powyżej 3.5 gola w 2 połowie": {"name": "2_o35_2nd_half"},
        "2 Poniżej/Powyżej 4.5 gola w 2 połowie": {"name": "2_o45_2nd_half"},
        "Handicap (1X2) 0:x":{"name":"ah-"},
        "Handicap (1X2) x:0":{"name":"ah+"},
        "Handicap -0.5/+0.5":{"name":"eh-05"},
        "Handicap +0.5/-0.5":{"name":"eh+05"},
        "Handicap +1.5/-1.5":{"name":"eh+15"},
        "Handicap +2.5/-2.5": {"name": "eh+25"},
        "Handicap +3.5/-3.5": {"name": "eh+35"},
        "Handicap +4.5/-4.5": {"name": "eh+45"},
        "Handicap +5.5/-5.5": {"name": "eh+55"},
        "Handicap +6.5/-6.5": {"name": "eh+65"},
        "Handicap -1.5/+1.5": {"name": "eh-15"},
        "Handicap -2.5/+2.5": {"name": "eh-25"},
        "Handicap -3.5/+3.5": {"name": "eh-35"},
        "Handicap -4.5/+4.5": {"name": "eh-45"},
        "Handicap -5.5/+5.5": {"name": "eh-55"},
        "Handicap -6.5/+6.5": {"name": "eh-65"},
        "Suma goli (1)":{"name":"1st_team_goals"},
        "Suma goli (2)": {"name": "2nd_team_goals"},
        "1 strzeli w obu połowach":{"name":"1_to_score_both_half"},
        "2 strzeli w obu połowach":{"name":"2_to_score_both_half"},
        "1 wygra obie połowy":{"name":"1_to_win_both_half"},
        "2 wygra obie połowy": {"name": "2_to_win_both_half"},
        "1 wygra 1 lub 2 połowę" : {"name": "1_to_win_any_half"},
        "2 wygra 1 lub 2 połowę": {"name": "2_to_win_any_half"},
        "Połowa z większą liczbą bramek":{"name":"half_more_goals"},
        "Czas pierwszego gola":{"name":"1st_goal_time"},
        "Pierwszy gol i wynik końcowy": {"name": "1st_goal/game"},
        "Do przerwy/Cały mecz - Dokładny wynik":{"name":"1st_half/2nd_half_cs"},
        "1 - połowa z większą ilością goli" :{"name":"1_half_more_goals"},
        "2 - połowa z większą ilością goli": {"name": "2_half_more_goals"},
        "Wynik końcowy i Poniżej/Powyżej x gola":{"name":"game/goals"},
        "Dokładny wynik (w tym inny)":{"name":"cs_other"},
        "Wynik końcowy i obie drużyny strzelą":{"name":"game/btts"},
        "1 - czyste konto w 1 połowie": {"name": "1_clean_1st_half"},
        "2 - czyste konto w 1 połowie": {"name": "2_clean_1st_half"},
        "1 - czyste konto w 2 połowie": {"name": "1_clean_2nd_half"},
        "2 - czyste konto w 2 połowie": {"name": "2_clean_2nd_half"},
        "Gospodarz wygra = zwrot" :{"name":"hnb"},
        "Gość wygra = zwrot":{"name":"anb"},
        "Wynik 1 połowy i Poniżej/Powyżej 1.5 goli w 1 połowie":{"name":"1st_half_and_o05"},
        "Obie drużyny strzelą i Poniżej/Powyżej 2.5 gola":{"name":"btts_and_25"},
        "Handicap 0:1 w 1 połowie":{"name":"1st_half_ah-1"},
        "Handicap 0:1 w 2 połowie": {"name": "2nd_half_ah-1"},
        "Handicap 1:0 w 1 połowie":{"name":"1st_half_ah+"},
        "Handicap 1:0 w 2 połowie": {"name": "2nd_half_ah+1"},
        "Wynik 1 połowy i obie strzelą w 1 połowie":{"name":"1st_half_and_btts_1st_half"},
        "Suma goli (nieparzyste/parzyste)":{"name":"goals_odd_even"},
        "Ilość goli w 1 połowie - Nieparzysta/Parzysta":{"name":"1st_half_goals_odd_even"},
        "Ilośc goli w 2 połowie - Nieparzysta/Parzysta":{"name":"2nd_half_goals_odd_even"},
        "1 - suma goli - Nieparzyste/Parzyste":{"name":"1_goals_odd_even"},
        "2 - suma goli - Nieparzyste/Parzyste":{"name":"2_goals_odd_even"},
        "Zdobędzie gola w meczu":{"name":"scorer"},
        "Strzelec ostatniego gola":{"name":"scorer_last_goal"},
        "Strzelec 1 gola":{"name":"scorer_first_goal"},

    }

    def extract_team_name(self,x, home, away):
        if len(re.findall(home, x)) > 0 and len(re.findall(away, x)) > 0:
            x2=re.sub(home, '1', x)
            x3=re.sub(away, '2', x2)
            return x3
        elif len(re.findall(home, x)) > 0:
            return re.sub(home, '1', x)
        elif len(re.findall(away, x)) > 0:
            return re.sub(away, '2', x)
        else:
            return x
    def get_odds2(self):
        soup = BeautifulSoup(data, "html.parser")
        self.odds = defaultdict(str)
        tables = soup.find_all('div', {'class': 'games-panel'})
        print ("Home:",self.home)
        print ("Away:", self.away)
        for table in tables:
            odd_tittle=table.find('div',{'class':'game-title'})
            #print(self.extract_team_name(odd_tittle.text, self.home, self.away))
            try:
                name=self.extract_team_name(odd_tittle.text,self.raw_home,self.raw_away)
                if name not in self.events_mapping_iforbet.keys():
                    logging.warning("Nieznany zaklad: "+odd_tittle.text)
                self.odds[self.events_mapping_iforbet[name]["name"]]={}
                #print (odd_tittle.text)
            except:
                pass
            odd_values=table.find_all('div',{'class':'event-rate'})
#            print ("NAME:",name)
            for odd in odd_values:
                rows=odd.find_all('div',{'class':'outcome-row'})
                if len(rows)==0:
                    odd_name = odd.find('div', {'class': 'outcome-name'})
                    print ("ODD_name: ", odd_name.text)
                    odd_rate = odd.find('span', {'class': 'rate-value'})
                    print ("ODD_rate: ", odd_rate.text)
                    odd_name_corr=self.extract_team_name(odd_name.text,self.raw_home,self.raw_away)
                    # self.odds[name][odd_name.text]={}
                    self.odds[self.events_mapping_iforbet[name]["name"]][odd_name_corr] = odd_rate.text
                else:
                    for row in rows:
                        odd_name=row.find('div',{'class':'outcome-name'})
                        print ("ODD_name: ",odd_name.text)
                        odd_rate=row.find('span',{'class':'rate-value'})
                        print ("ODD_rate: ", odd_rate.text)
                    #self.odds[name][odd_name.text]={}
                        odd_name_corr = self.extract_team_name(odd_name.text, self.raw_home, self.raw_away)
                        self.odds[self.events_mapping_iforbet[name]["name"]][odd_name_corr]=odd_rate.text
        import json
        print (json.dumps(self.odds, indent=4, sort_keys=False))
        #pp = pprint.PrettyPrinter(depth=3)
        #pp.pprint(self.odds)
        #pprint (self.odds,)
        #pprint

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
        self.get_odds2()

        #self.prepare_dict_to_sql()
        #print ("ODDS:",self.odds)
data = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/449457',None,headers)).read() # The data u need
meczyk=football_event(events_mapping_fortuna)
#exit()


url='https://www.iforbet.pl/oferta/8/199,511,168,282,2432,321,159,269,223,147,122,273,660,2902,558,641,289'

def get_links(url):
    data = urllib2.urlopen(urllib2.Request(url, None, headers)).read()
    soup = BeautifulSoup(data, "html.parser")
    linki = []
    links=soup.find_all('div',{'class':'event-more'})
    for link in links:
        linki.append(str(link).split("'")[1])
    #self.game = soup.find('div', {'class': 'event-data'})
    return linki
linki=get_links(url)
print (linki)
for link in linki:
    data = urllib2.urlopen(
        urllib2.Request('https://www.iforbet.pl'+link, None, headers)).read()  # The data u need
#get_links(url)
    #data = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers)).read() # The data u need
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


