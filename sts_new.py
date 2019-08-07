#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib.request as urllib2
#import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import platform
#from selenium import webdriver
import codecs, sys
import json
import sqlite3
from collections import defaultdict
import logging
from dictionaries import *
import datetime
import re


class football_event:
    logging.basicConfig(filename='logfile_sts.log', level=logging.DEBUG)

    discipline='football'

    def get_name(self,data):
        soup = BeautifulSoup(data, "html.parser")

        game_teams = soup.find('div', {'id': 'content'})
        details = game_teams.h1.get_text("\n").strip().replace('-', '\n').split('\n')
        self.home = unify_name(details[0].strip(), teams, logging)
        self.away = unify_name(details[1].strip(), teams, logging)
        self.date = details[2].split(' ')[0]
        self.hour = details[2].split(' ')[1]
        print(self.date)
        print(self.hour)


        # get all the games
        current_time=datetime.datetime.now()
        self.update_time=str('{:04d}'.format(current_time.year))+'-'+str('{:02d}'.format(current_time.month))+'-'+str('{:02d}'.format(current_time.day))+ \
                         '-' + str('{:02d}'.format(current_time.hour)) + '-' + str('{:02d}'.format(current_time.minute)) + '-' + str('{:02d}'.format(current_time.second))
        self.home_all_names=teams[self.home]
        self.away_all_names=teams[self.away]
        print ("ALL_NAMES_HOME",sorted(self.home_all_names,key=len,reverse=True), self.home)
        print ("ALL_NAMES_AWAY",sorted(self.away_all_names, key=len, reverse=True), self.away)

        self.home_raw=details[0].strip()
        self.away_raw=details[1].strip()
        return game_teams

    def odds_get(self,data):
        soup = BeautifulSoup(data, "html.parser")
        game_teams = soup.find('div', {'id': 'content'})
        details = game_teams.h1.get_text("\n").strip().replace('-', '\n').split('\n')
        print(details)
        home = unify_name(details[0].strip(), teams, logging)
        away = unify_name(details[1].strip(), teams, logging)
        date = details[2].split(' ')[0]
        hour = details[2].split(' ')[1]
        print(date)
        self.date_format = str(date.split('.')[2] + '-' + date.split('.')[1] + '-' + date.split('.')[0])
        print(self.date_format)
        print(hour)
        odds = {}

        ########działało:
        # bets_main=soup.find_all('a',{'class':'preventDefault'})
        bb = soup.find('dd')
        bets_main = bb.find_all('div', {'class': 'sidebet_6'})
        name = 'game'
        odds[name] = {}
        for bet in bets_main:
            typ = bet.p.a.get_text("\n", strip=True).replace(' ', '\n').strip().split('\n')
            odds[name][typ[0]] = typ[1]
            # print(typ)

        bets = soup.find_all('a', {'class': 'open preventDefault'})

        for bet in bets:
            name = bet.text.strip()
            name = name.replace(details[0].strip(), "111")
            name = name.replace(details[1].strip(), "222")
            # print(bet.text.strip())
            odds[name] = {}
            next_td_tag = bet.findNext('dd')
            typ = next_td_tag.get_text("\n", strip=True).strip().split('\n')
            typ = [t.replace(details[0].strip(), "111") for t in typ]
            typ = [t.replace(details[1].strip(), "222") for t in typ]
            for i, k in zip(typ[0::2], typ[1::2]):
                odds[name][i] = k
            # typ = next_td_tag.span
            # print (typ)
        #print("FUNKCJA ODDS:",odds)
        return odds

    def find_team_name(self,name):
        if '.' in name:
            name.replace('.','\.')
        for i in sorted(self.home_all_names, key=len,reverse=True):
            if len(re.findall(i,name)) > 0:
                name=re.sub(i,self.home,name)
                break
        for i in sorted(self.away_all_names, key=len,reverse=True):
            if len(re.findall(i,name)) > 0:
                name = re.sub(i, self.away, name)
                break
        return name
    def correct_name(self,name2):
        #print ("X:",name2)
        name=self.find_team_name(name2)
        if (self.home in name.split('/')[0] and '/' in name):
            return self.home+'/'+name.split('/')[1]
        elif (self.away in name.split('/')[0] and '/' in name):
            return self.away + '/' + name.split('/')[1]
        else:
            return name
    def fix_for_cup(self,name):
        if 'mecz' in name[0:5]:
            return 'mecz'
        else:
            return name
    #def get_home(self,game_teams):
    #    self.home=game_teams.split(' - ')[0]
    #    self.away=game_teams.split(' - ')[1]
    #    self.date=game_teams.split(' - ')[2]
    #    self.time=game_teams.split(' - ')[3]
    def get_odds(self,data):
        self.odds = defaultdict(str)
        soup = BeautifulSoup(data, "html.parser")

        games_col3 = soup.find_all('table', {'class': 'col3'})
        #print games
        for games in games_col3:
            odd_t=games.find('thead')
            #print odd_t
            try:
                #print ("TEXT:")
                #print (odd_t.tr.th.span.text.strip())
                #print (codecs.encode(odd_t.tr.th.span.text.strip(),encoding='utf-8'))
                name = odd_t.tr.th.span.text.strip()
                name = self.fix_for_cup(name.strip())
                self.odd_type=self.__events_mapping[name]["name"]
            except:
                logging.warning(self.home+'  '+self.away)
                logging.warning("Nieznany zaklad: "+ name)
                self.odd_type=odd_t.tr.th.span.text.strip()
                print ("Nie ma: %s", odd_t.tr.th.span.text.strip() )
            odd_t2=games.find('tbody')
            #print "TU JEST KURS:"
            tmp=games.find('tbody').find_all('tr')
            if len(tmp)>1:
                cols=tmp[1].find_all('td')
            else:
                cols = tmp[0].find_all('td')
            i=0
            #print ("COLS: ", cols)
            cols=[]
            for i in tmp:
                cols.append(i.find_all('td'))

            #cols=tmp.find_all('td')
            #POPRAW DLA HANDICAP

            self.odds[self.odd_type] = {}
            for t in tmp:
                #print col.text.strip().split(' ')[-1]
                cols=t.find_all('td')
                for col in cols:
                    x = col.text.strip().split('\n')
                #print x
                    try:
                        #print ("XO:",x[0])
                        self.odds[self.odd_type][self.correct_name(x[0].strip())]=float(x[1].strip())
                    except:
                        #print ("nieznany zaklad:")
                        #print (col.text.strip().replace(' ','').split('\n'))
                        continue



        games_col2 = soup.find_all('table', {'class': 'col2'})
        for games in games_col2:
            odd_t=games.find('thead')
            #print (odd_t.text.strip())
            try:
                #print ("TEXT:")
                #print (odd_t.tr.th.span.text.strip())
                #print (codecs.encode(odd_t.tr.th.span.text.strip(),encoding='utf-8'))
                name=odd_t.tr.th.span.text.strip()
                self.odd_type=self.__events_mapping[name]["name"]
            except:
                logging.warning(self.home+' - '+self.away)
                logging.warning("Nieznany zaklad: "+ name)
                continue
            odd_t2=games.find('tbody').find_all('tr')
            if len(odd_t2)>1:
                cols=odd_t2[-1].find_all('td')
            else:
                cols=odd_t2[0].find_all('td')
            #print "TU JEST KURS:"
            #cols=games.find('tbody').find('tr').find_all('td')
            i=0
            self.odds[self.odd_type] = {}
            for col in cols:
                #print col.text.strip().split(' ')[-1]
                x = col.text.strip().split('\n')
                #print ("X: ",x)
                try:
                    self.odds[self.odd_type][self.correct_name(x[0].strip())]=float(x[1].strip())
                except:
                    #print ("nieznany zaklad:")
                    #print (col.text.strip().replace(' ','').split('\n'))
                    continue
                i=i+1


        games_col1 = soup.find_all('table', {'class': 'col1'})
        #print ("GAMES_COL1: ", games_col1)
        for games in games_col1:
            odd_t = games.find('thead')
            #print (odd_t.text.strip())
            #print ("TEXT:", odd_t)
                # print (odd_t.tr.th.span.text.strip())
            if odd_t is not None:    # print (codecs.encode(odd_t.tr.th.span.text.strip(),encoding='utf-8'))
                self.odd_type = self.__events_mapping[odd_t.tr.th.span.text.strip()]["name"]
                self.odds[self.odd_type] = {}

            odd_t2 = games.find('tbody').find_all('tr')
            self.sub_name=odd_t2[0].text

            cols = odd_t2[1].find('td')
            # print "TU JEST KURS:"
            # cols=games.find('tbody').find('tr').find_all('td')
            i = 0

            self.odds[self.odd_type][self.sub_name] = {}
            x = cols.text.strip().split('\n')
            #print ("X: ",x)
            try:
                self.odds[self.odd_type][self.sub_name] = float(x[1].strip())
            except:
                    # print ("nieznany zaklad:")
                    # print (col.text.strip().replace(' ','').split('\n'))
                continue
        print (self.odds)
        return self.odds
    def prepare_dict_to_sql(self):
        self.dict_sql=defaultdict()

        def deep_get(napis,x):
            try:
                return napis.get(x,'')
            except:
                pass

        def deep_get(_dict, keys, default=None):
            for key in keys:
                if isinstance(_dict, dict):
                    _dict = _dict.get(key, default)
                else:
                    return default
            return _dict

        home = self.home
        away = self.away
        print(home)
        print(away)
        print ("SELF.HOME",self.home)
        #self.dict_sql['home']=self.get_name(data).split(" - ")[0].strip().replace(' ','')
        self.dict_sql['home'] = self.home
        #self.dict_sql['away']=away = self.get_name(data).split(" - ")[1].strip().replace(' ','')
        self.dict_sql['away'] = self.away
        self.dict_sql['sts_game_1']=self.odds['game']['1']
        self.dict_sql['sts_game_0']=self.odds['game']['X']
        self.dict_sql['sts_game_2']=self.odds['game']['2']
        self.dict_sql['sts_game_10']=self.odds['game']['1X']
        self.dict_sql['sts_game_02']=self.odds['game']['X2']
        self.dict_sql['sts_game_12'] = self.odds['game']['12']
        self.dict_sql['data']=str(self.date_format)
        #self.dict_sql['Sport']=self.discipline
        self.dict_sql['League']=self.league
        #self.dict_sql['country']=self.country
        self.dict_sql['sts_update_time']=self.update_time
        self.dict_sql['hour']=self.hour
        self.dict_sql['sts_dnb_1'] = deep_get(self.odds['zakład bez remisu (remis=zwrot)'], '1')
        self.dict_sql['sts_dnb_2'] = deep_get(self.odds['zakład bez remisu (remis=zwrot)'], '2')
        self.dict_sql['sts_o_05'] = deep_get(self.odds,['liczba goli w meczu 0.5 - poniżej/powyżej','+'])
        self.dict_sql['sts_u_05'] = deep_get(self.odds,['liczba goli w meczu 0.5 - poniżej/powyżej','-'])
        self.dict_sql['sts_o_15'] = deep_get(self.odds, ['liczba goli w meczu 1.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_15'] = deep_get(self.odds, ['liczba goli w meczu 1.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_o_25'] = deep_get(self.odds, ['liczba goli w meczu 2.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_25'] = deep_get(self.odds, ['liczba goli w meczu 2.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_o_35'] = deep_get(self.odds, ['liczba goli w meczu 3.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_35'] = deep_get(self.odds, ['liczba goli w meczu 3.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_o_45'] = deep_get(self.odds, ['liczba goli w meczu 4.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_45'] = deep_get(self.odds, ['liczba goli w meczu 4.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_o_55'] = deep_get(self.odds, ['liczba goli w meczu 5.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_55'] = deep_get(self.odds, ['liczba goli w meczu 5.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_o_65'] = deep_get(self.odds, ['liczba goli w meczu 6.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_65'] = deep_get(self.odds, ['liczba goli w meczu 6.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_o_75'] = deep_get(self.odds, ['liczba goli w meczu 7.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_75'] = deep_get(self.odds, ['liczba goli w meczu 7.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_o_85'] = deep_get(self.odds, ['liczba goli w meczu 8.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_85'] = deep_get(self.odds, ['liczba goli w meczu 8.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_o_95'] = deep_get(self.odds, ['liczba goli w meczu 9.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_u_95'] = deep_get(self.odds, ['liczba goli w meczu 9.5 - poniżej/powyżej', '-'])

        self.dict_sql['sts_ht_ft_11'] = deep_get(self.odds,['1. połowa/wynik końcowy', '1/1'])
        self.dict_sql['sts_ht_ft_1x'] = deep_get(self.odds,['1. połowa/wynik końcowy', '1/X'])
        self.dict_sql['sts_ht_ft_2x'] = deep_get(self.odds,['1. połowa/wynik końcowy', '2/X'])
        self.dict_sql['sts_ht_ft_21'] = deep_get(self.odds,['1. połowa/wynik końcowy', '2/1'])
        self.dict_sql['sts_ht_ft_22'] = deep_get(self.odds,['1. połowa/wynik końcowy', '2/2'])
        self.dict_sql['sts_ht_ft_x1'] = deep_get(self.odds,['1. połowa/wynik końcowy', 'X/1'])
        self.dict_sql['sts_ht_ft_x2'] = deep_get(self.odds,['1. połowa/wynik końcowy', 'X/2'])
        self.dict_sql['sts_ht_ft_12'] = deep_get(self.odds,['1. połowa/wynik końcowy', '1/2'])
        self.dict_sql['sts_ht_ft_xx'] = deep_get(self.odds,['1. połowa/wynik końcowy', 'X/X'])
        self.dict_sql['sts_first_half_1'] = deep_get(self.odds,['1 połowa','1'])
        self.dict_sql['sts_first_half_x'] = deep_get(self.odds,['1 połowa','X'])
        self.dict_sql['sts_first_half_2'] = deep_get(self.odds,['1 połowa','2'])
        self.dict_sql['sts_first_half_10'] = deep_get(self.odds,['1 połowa','1X'])
        self.dict_sql['sts_first_half_02'] = deep_get(self.odds,['1 połowa','X2'])
        self.dict_sql['sts_first_half_12'] = deep_get(self.odds,['1 połowa','12'])
        #DOROBIC#################
        self.dict_sql['sts_eh_min_1_1'] = deep_get(self.odds,['handicap: 111 (-1.0) - 222','111 (-1.0)'])
        self.dict_sql['sts_eh_min_1_x'] = deep_get(self.odds,['handicap: 111 (-1.0) - 222','X'])
        self.dict_sql['sts_eh_min_1_x2'] = deep_get(self.odds,['handicap: 111 (-1.0) - 222','X2'])
        # self.dict_sql['sts_eh-1_2'] = get_odd_2(self.odds['eh-1'], home + '(-1)')
        self.dict_sql['sts_u_15_1'] = deep_get(self.odds,['liczba goli 1.5/wynik meczu', '-1.5/1'])
        self.dict_sql['sts_o_15_1'] = deep_get(self.odds,['liczba goli 1.5/wynik meczu', '+1.5/1'])
        self.dict_sql['sts_u_25_1'] = deep_get(self.odds,['liczba goli 2.5/wynik meczu', '-2.5/1'])
        self.dict_sql['sts_o_25_1'] = deep_get(self.odds,['liczba goli 2.5/wynik meczu', '+2.5/1'])
        self.dict_sql['sts_u_25_x'] = deep_get(self.odds,['liczba goli 2.5/wynik meczu', '-2.5/X'])
        self.dict_sql['sts_o_25_x'] = deep_get(self.odds,['liczba goli 2.5/wynik meczu', '+2.5/X'])
        self.dict_sql['sts_u_15_x'] = deep_get(self.odds,['liczba goli 1.5/wynik meczu', '-1.5/X'])
        self.dict_sql['sts_o_15_x'] = deep_get(self.odds,['liczba goli 1.5/wynik meczu', '+1.5/X'])
        self.dict_sql['sts_u_25_2'] = deep_get(self.odds,['liczba goli 1.5/wynik meczu', '-2.5/2'])
        self.dict_sql['sts_o_25_2'] = deep_get(self.odds,['liczba goli 1.5/wynik meczu', '+2.5/2'])
        self.dict_sql['sts_u_15_2'] = deep_get(self.odds, ['liczba goli 1.5/wynik meczu', '-1.5/2'])
        self.dict_sql['sts_o_15_2'] = deep_get(self.odds, ['liczba goli 1.5/wynik meczu', '+1.5/2'])
        ##I TO DO POPRAWKI#########
        self.dict_sql['sts_first_goal_1'] = deep_get(self.odds,['pierwszy gol w meczu', '1 dr.'])
        self.dict_sql['sts_first_goal_2'] = deep_get(self.odds,['pierwszy gol w meczu', '2 dr.'])
        self.dict_sql['sts_first_goal_0'] = deep_get(self.odds,['pierwszy gol w meczu', 'nikt'])
        self.dict_sql['sts_btts_1'] = deep_get(self.odds,['wynik meczu/obie drużyny strzelą', '1/tak'])
        self.dict_sql['sts_btts_2'] = deep_get(self.odds,['wynik meczu/obie drużyny strzelą', '2/tak'])
        self.dict_sql['sts_btts_x'] = deep_get(self.odds,['wynik meczu/obie drużyny strzelą', 'X/tak'])
        self.dict_sql['sts_btts_no_1'] = deep_get(self.odds,['wynik meczu/obie drużyny strzelą', '1/nie'])
        self.dict_sql['sts_btts_no_2'] = deep_get(self.odds,['wynik meczu/obie drużyny strzelą', '2/nie'])
        self.dict_sql['sts_btts_no_x'] = deep_get(self.odds,['wynik meczu/obie drużyny strzelą', 'X/nie'])
        self.dict_sql['sts_btts_yes'] = deep_get(self.odds,['obie drużyny strzelą gola', 'tak'])
        self.dict_sql['sts_btts_no'] = deep_get(self.odds,['obie drużyny strzelą gola', 'nie'])
        self.dict_sql['sts_corners_o_65'] = deep_get(self.odds,['liczba rzutów rożnych 6.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_65'] = deep_get(self.odds,['liczba rzutów rożnych 6.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_75'] = deep_get(self.odds,['liczba rzutów rożnych 7.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_75'] = deep_get(self.odds,['liczba rzutów rożnych 7.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_85'] = deep_get(self.odds,['liczba rzutów rożnych 8.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_85'] = deep_get(self.odds,['liczba rzutów rożnych 8.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_95'] = deep_get(self.odds,['liczba rzutów rożnych 9.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_95'] = deep_get(self.odds,['liczba rzutów rożnych 9.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_105'] = deep_get(self.odds,['liczba rzutów rożnych 10.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_105'] = deep_get(self.odds,['liczba rzutów rożnych 10.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_115'] = deep_get(self.odds,['liczba rzutów rożnych 11.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_115'] = deep_get(self.odds,['liczba rzutów rożnych 11.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_125'] = deep_get(self.odds,['liczba rzutów rożnych 12.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_125'] = deep_get(self.odds,['liczba rzutów rożnych 12.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_135'] = deep_get(self.odds,['liczba rzutów rożnych 13.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_135'] = deep_get(self.odds,['liczba rzutów rożnych 13.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_145'] = deep_get(self.odds,['liczba rzutów rożnych 14.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_145'] = deep_get(self.odds,['liczba rzutów rożnych 14.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_155'] = deep_get(self.odds,['liczba rzutów rożnych 15.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_155'] = deep_get(self.odds,['liczba rzutów rożnych 15.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_165'] = deep_get(self.odds,['liczba rzutów rożnych 16.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_165'] = deep_get(self.odds,['liczba rzutów rożnych 16.5 - poniżej/powyżej', '-'])
        self.dict_sql['sts_corners_o_175'] = deep_get(self.odds,['liczba rzutów rożnych 17.5 - poniżej/powyżej', '+'])
        self.dict_sql['sts_corners_u_175'] = deep_get(self.odds,['liczba rzutów rożnych 17.5 - poniżej/powyżej', '-'])

        print ("DICT: ", self.dict_sql)
        return self.dict_sql

    def save_to_db(meczyk):
        database_name = 'db.sqlite'
        db = sqlite3.connect(database_name)
        table="'db_bets'"
        table2='db_bets'
        columns_string = '("' + '","'.join(meczyk.dict_sql.keys()) + '")'
        values_string = '("' + '","'.join(map(str, meczyk.dict_sql.values())) + '")'
        cur = db.cursor()
        #print ("SELECT:")
        home="'"+meczyk.home+"'"
        away = "'" + meczyk.away + "'"
        date = "'" + meczyk.date.split(' ')[1].split('.')[2]+'-'+meczyk.date.split(' ')[1].split('.')[1]+'-'+meczyk.date.split(' ')[1].split('.')[0]+ "'"
        #date = "'" + meczyk.date.split(' ')[1].split('.')[2] + '-' + meczyk.date.split(' ')[1].split('.')[1] + '-' + \
        #       meczyk.date.split(' ')[1].split('.')[0] + "'"
        #print ("select * from %s where home=%s and away=%s and data=%s" % (table,home,away,date))
        #cur.execute("select * from %s where home=%s and away=%s and data=%s" % (table,home,away,date))
        #data=cur.fetchall()
        #x=[]
        #for i in range(0, len(columns_string) - 1):
        #    x.append((str(columns_string[i]) + "=" + str(values_string[i])))
#        try:
#            sql_command="DELETE FROM %s WHERE home=%s and away=%s and data=%s" % (table,home,away,date)
#            print ("SQL COMMAND:",sql_command)
#            db.execute(sql_command)
#            print ("USUNIĘTO")
#        except:
#            pass
        #UPDATE employee SET role = 'code_monkey', name='fred' WHERE id = 1;
        sql_update_command= 'UPDATE ' + str(table) + " SET "
        print ("SQL UPDATE")
        for k,v in meczyk.dict_sql.items():
            sql_update_command = sql_update_command + '"'+str(k) + '"="' + str(v)+'",'
        #print (sql_update_command)
        sql_update_cmd=sql_update_command[:-1] + " WHERE home=" + str(home) + "and away = "+ str(away) + " and data = "+str(date)
        sql_update = """UPDADE %s SET %s = %s WHERE home = %s
                      and away = %s and data = %s""" % (table, columns_string, values_string,home,away,date)
        sql_insert = """INSERT INTO %s %s
                     VALUES %s""" % (table, columns_string, values_string)
        #if data is None:
        #    print ("NEW")
        #    sql = """INSERT INTO %s %s
        #                 VALUES %s""" % (table, columns_string, values_string)
        #else:
        #    print("UPDATE")
        #    sql = """UPDATE %s SET %s WHERE home=%s and away=%s and date=%s""" % (table, tuple(x),meczyk.home,meczyk.away,meczyk.date)
        #    print ("UPDATE",sql)
        print (sql_update_cmd)
        print ("HOME", home)
        polecenie="SELECT * FROM "+str(table2)+ " WHERE home="+str(home) +" and away=" + str(away) +" and data="+str(date)
        print(polecenie)

        try:
            x=cur.execute(polecenie).fetchone()
        except Exception as e: print(e)
        print ("Z BAZY",x)
        print (polecenie)
        try:
            if x==None:
                db.execute(sql_insert)
                db.commit()
            else:
                print("NIE UDALO SIE INS")
                db.execute(sql_update_cmd)
                db.commit()
                print("ALE UDALO SIE UP")
        except Exception as e: print(e)
            #
            #pass
        #print (sql_update)
        print (sql_insert)
#        try:
#            db.execute(sql_insert)
#            db.commit()
#        except:
#            print ("NIE UDALO SIE INSERTNAC")
#            pass


    def __init__(self,data,league):
        #print (data)
        self.league=league
        self.name=self.get_name(data)
        self.odds=self.odds_get(data)
        print("SELF_ODDS:",self.odds)
        #self.home=self.get_home(self.name)
        #self.get_odds(data)
        #print (self.odds)
        self.prepare_dict_to_sql()
        #self.date2 = "'" + self.date.split(' ')[1].split('.')[2] + '-' + self.date.split(' ')[1].split('.')[1] + '-' + \
               #self.date.split(' ')[1].split('.')[0] + "'"
        #file=open('odd','w')
        #file.write(str(self.odds))


data=codecs.open('sts_game.html',mode='r',encoding='utf-8').read()

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }


#site='https://m.sts.pl/pl/sport/184/6501/3986/158419520'
#request = urllib2.Request(site, None, headers)
#response = urllib2.urlopen(request)
#strona = response.read()
#data=strona



#data=urllib2.urlopen('https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6507&league=4013&oppty=130931499').read()
#url='https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6527&league=4074&oppty=149243022'
#user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
#headers = {'User-Agent': user_agent, }
#request = urllib2.Request(url, None, headers)
#data=urllib2.urlopen(request).read()
soup = BeautifulSoup(data, "html.parser")

logging.basicConfig(filename='logfile_sts.log', level=logging.DEBUG)

game_teams = soup.find('div', {'id': 'content'})
details=game_teams.h1.get_text("\n").strip().replace('-','\n').split('\n')
print(details)
home = unify_name(details[0].strip(), teams, logging)
away = unify_name(details[1].strip(), teams, logging)
date=details[2].split(' ')[0]
hour=details[2].split(' ')[1]
print (date)
date_format=str(date.split('.')[2]+'-'+date.split('.')[1]+'-'+date.split('.')[0])
print (date_format)
print (hour)
odds={}


print(home)
print(away)
########działało:
#bets_main=soup.find_all('a',{'class':'preventDefault'})
bb=soup.find('dd')
bets_main=bb.find_all('div',{'class':'sidebet_6'})
#print ("bets_main",bets_main)
name='game'
odds[name] = {}
for bet in bets_main:

    typ = bet.p.a.get_text("\n", strip=True).replace(' ', '\n').strip().split('\n')
    print ("TYP",typ)
    odds[name][typ[0]] = typ[1]
    #print(typ)

bets=soup.find_all('a',{'class':'open preventDefault'})

for bet in bets:
    name=bet.text.strip()
    #print(bet.text.strip())
    name = name.replace(details[0].strip(), "111")
    name = name.replace(details[1].strip(), "222")
    odds[name]={}
    next_td_tag = bet.findNext('dd')
    ######TO JEST LEPSZE DODAC DO GLOWNEGO#############
    typ = next_td_tag.get_text("\n", strip=True).strip().split('\n')
    typ = [t.replace(details[0].strip(), "111") for t in typ]
    typ = [t.replace(details[1].strip(), "222") for t in typ]
#    if details[0].strip() in typ:


    print ("TYP2",name,typ)
    for i, k in zip(typ[0::2], typ[1::2]):
        odds[name][i]=k
    #typ = next_td_tag.span
    #print (typ)
print (odds)
    #print (next_td_tag)




#meczyk=football_event()
#print (game_teams)
#meczyk.prepare_dict_to_sql()

#meczyk.save_to_db()
#exit()
sites=['https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6502&league=43461',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6507&league=4013&t=1526162250',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6521&league=4080',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=4243',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=4013',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=3944',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=4206',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=4264',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=5012',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=3903',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=3939',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6534&league=4073',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6488&league=3987',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6535&league=3994',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6490&league=4032',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6482&league=4079',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6516&league=4234',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6493&league=4000',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6501&league=3986',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6539&league=4070',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6527&league=4074',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6482&league=3954',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6500&league=4218',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6521&league=4036',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6501&league=4073',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6563&league=4121',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6565&league=4281',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6481&league=3879',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6497&league=4210',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6487&league=4132',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6485&league=3880',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6531&league=4139',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6508&league=3996',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6489&league=5641',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6538&league=4009',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6542&league=4088',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6498&league=3901',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6535&league=4015',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6488&league=4167',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6502&league=4264',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6480&league=5443',
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6480&league=5444'
'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6480&league=5538'
       'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6480&league=4750',
       'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6480&league=5441',
       'https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6480&league=4054']

sites2=['https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6502&league=43461']
sites2={'https://m.sts.pl/pl/sport/184/6502/74203':'Polska',
        'https://m.sts.pl/pl/sport/184/6502/4264':'Polska',
        'https://m.sts.pl/pl/sport/184/6521/4080':'Anglia',
        'https://m.sts.pl/pl/sport/184/6507/74188':'Belgia',
        'https://m.sts.pl/pl/sport/184/6535/74154':'Francja',
        'https://m.sts.pl/pl/sport/184/6488/3987':'Hiszpania',
        'https://m.sts.pl/pl/sport/184/6482/4079':'Niemcy',
        'https://m.sts.pl/pl/sport/184/6482/3954':'Niemcy',
        'https://m.sts.pl/pl/sport/184/6490/74202':'Holandia',
        'https://m.sts.pl/pl/sport/184/6516/74389':'Portugalia',
        'https://m.sts.pl/pl/sport/184/6508/74191':'Szkocja',
        'https://m.sts.pl/pl/sport/184/6501/74187':'Włochy',
        'https://m.sts.pl/pl/sport/184/6501/74195':'Włochy',
        'https://m.sts.pl/pl/sport/184/6527/74206':'Turcja',
        'https://m.sts.pl/pl/sport/184/6488/74380':'Hiszpania',
        'https://m.sts.pl/pl/sport/184/6521/74214':'Anglia'}
sites3={'https://m.sts.pl/pl/sport/184/6502/74203':'Polska'}
for site in sites2:
    logging.basicConfig(filename='logfile_sts.log', level=logging.DEBUG)

    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib2.Request(site, None, headers)
    response = urllib2.urlopen(request)
    strona = response.read()
    soup = BeautifulSoup(strona, "html.parser")
    try:
        league = unify_name(soup.find('div',{'id':'content'}).h1.text.strip()+' '+sites2[site],leagues,logging)
    except:
        league='default'
    print("League",league)
    country=sites2[site]
    print ("COUNTRY:",country)
    #print (soup)
    more_bets=soup.find_all('a', {'class': 'more'},href=True)
    #more_bets = soup.find_all('td')
    #more_bets=['https://m.sts.pl/pl/sport/184/6502/43461/128429980']
    print("MORE",site,sites2[site],more_bets,file=open('sts.txt','a'))
    print ("JESTEM TU")
    #more_bets=['https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6499&league=3903&oppty=152636192']
    for link in more_bets:
        print ("A: ",link)
        try:
            #link=a.find('a', href = True)
            #link=
            #link={}
            #link['href']='https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6499&league=3903&oppty=152636192'
    #    print ("LINK: ", link['href'])
            print (link['href'])
            request = urllib2.Request(link['href'], None, headers)
            data=urllib2.urlopen(request).read()
            #data = codecs.open('sts_game.html', mode='r', encoding='utf-8').read()
            meczyk=football_event(data,league)
            save_to_db_common(meczyk,str("'"+meczyk.date_format+"'"))
        except:
            print ("nie pykło")
            logging.basicConfig(filename='logfile_sts.log', level=logging.DEBUG)
            logging.warning("ERROR dla: "+link['href'])
            continue



###DOROBIC DC###





#if platform.system() == 'Windows':
#    PHANTOMJS_PATH = './phantomjs.exe'
#else:
#    PHANTOMJS_PATH = './phantomjs'

#browser = webdriver.PhantomJS(PHANTOMJS_PATH)
#browser = webdriver.Firefox()

#browser.get('https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6502&league=4163')

#soup = BeautifulSoup(browser.page_source, "html.parser")

