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
    __events_mapping={
        "mecz":{"name":"game"},
        "mecz  (w Niecieczy)":{"name":"game"},
        "zakład bez remisu (remis=zwrot)":{"name":"dnb"},
        "liczba goli w meczu 0.5 - poniżej/powyżej": {"name": "over0.5"},
        "liczba goli w meczu 1.5 - poniżej/powyżej":{"name":"over1.5"},
        "liczba goli w meczu 2.5 - poniżej/powyżej": {"name": "over2.5"},
        "liczba goli w meczu 3.5 - poniżej/powyżej": {"name": "over3.5"},
        "liczba goli w meczu 4.5 - poniżej/powyżej": {"name": "over4.5"},
        "liczba goli w meczu 5.5 - poniżej/powyżej": {"name": "over5.5"},
        "liczba goli w meczu 6.5 - poniżej/powyżej": {"name": "over6.5"},
        "liczba goli w meczu 7.5 - poniżej/powyżej": {"name": "over7.5"},
        "liczba goli w meczu 8.5 - poniżej/powyżej": {"name": "over8.5"},
        "liczba goli w meczu 9.5 - poniżej/powyżej": {"name": "over9.5"},
        "liczba goli : nieparzysta/parzysta": {"name":"goals_odd_even"},
        "1 drużyna strzeli gola":{"name":"1st_team_to_score"},
        "2 drużyna strzeli gola":{"name": "2nd_team_to_score"},
        "obie drużyny strzelą gola":{"name": "btts"},
        "zakład bez zwycięstwa 1 drużyny (zw.1dr.=zwrot)":{"name":"1nb"},
        "zakład bez zwycięstwa 2 drużyny (zw.2dr.=zwrot)": {"name": "2nb"},
        "handicap 0:1": {"name": "eh-1"},
        "handicap 1:0": {"name": "eh+1"},
        "handicap (-2.5)": {"name":"eh-2.5"},
        "handicap (-3.5)": {"name": "eh-3.5"},
        "handicap (-4.5)": {"name": "eh-4.5"},
        "handicap (+2.5)": {"name": "eh+2.5"},
        "handicap (+3.5)": {"name": "eh+3.5"},
        "handicap (+4.5)": {"name": "eh+4.5"},
        "handicap (-5.5)": {"name":"eh-5.5"},
        "handicap (+5.5)": {"name": "eh+5.5"},
        "handicap (-6.5)": {"name": "eh-6.5"},
        "handicap (+6.5)": {"name": "eh+6.5"},
        "handicap (-7.5)": {"name": "eh-7.5"},
        "handicap (+7.5)": {"name": "eh+7.5"},
        "handicap (-8.5)": {"name": "eh-8.5"},
        "handicap (+8.5)": {"name": "eh+8.5"},
        "dokładny wynik (1)": {"name": "cs"},
        "dokładny wynik (2)": {"name": "cs"},
        "dokładny wynik (3)": {"name": "cs"},
        "liczba goli 2.5/wynik meczu": {"name": "goal2.5/result"},
        "wynik meczu/obie drużyny strzelą": {"name": "game/btts"},
        "obie drużyny strzelą gola/ilość goli 2.5": {"name": "btts/o2.5"},
        "pierwszy gol w meczu": {"name": "1st_goal"},
        "podwójna szansa": {"name": "dc"},
        "w której połowie więcej goli": {"name": "ht_more"},
        "1 gol:minuta":{"name":"1st_goal_minute"},
        " 1 gol:minuta": {"name": "1st_goal_minute"},
        "wynik do 15 minuty": {"name": "to_15_min"},
        "wynik do 30 minuty": {"name": "to_30_min"},
        "wynik do 60 minuty": {"name": "to_60_min"},
        "wynik do 75 minuty": {"name": "to_75_min"},
        "1 połowa": {"name": "1st_half"},
        "dokładny wynik do przerwy": {"name": "1st_half_cs"},
        "1 połowa/wynik końcowy": {"name": "half/end"},
        "2 połowa": {"name": "2nd_half"},
        "1 drużyna : połowa z najw. ilością strzel. goli": {"name": "1st_team_half_more"},
        "2 druzyna : połowa z najw. ilością strzel. goli": {"name": "2nd_team_half_more"},
        "1 gol : minuta": {"name": "1st_goal_time"},
        "która drużyna otrzyma więcej zółtych kartek": {"name": "yellow_more"},
        "jakie wydarzenie odbędzie się jako pierwsze (2)": {"name": "1st_event"},
        "kto wykona pierwszy rzut rożny":{"name":"1st_corner"},
        "kto wykona ostatni rzut rożny":{"name":"last_corner"},
        "wyścig do 3. rzutów rożnych":{"name":"race_to_3_corners"},
        "1 połowa : zakład bez remisu (remis=zwrot)": {"name": "1st_half_dnb"},
        "1 połowa : liczba goli 0.5 - poniżej/powyżej": {"name": "1st_half_over0.5"},
        "1 połowa : liczba goli 1.5 - poniżej/powyżej": {"name": "1st_half_over1.5"},
        "1 połowa : liczba goli 2.5 - poniżej/powyżej": {"name": "1st_half_over2.5"},
        "1 połowa handicap (-1.5)": {"name": "1st_half_eh-1.5"},
        "1 połowa handicap (+1.5)": {"name": "1st_half_eh+1.5"},
        "2 połowa : zakład bez remisu (remis=zwrot)": {"name": "2nd_half_dnb"},
        "2 połowa : liczba goli 0.5 - poniżej/powyżej": {"name": "2nd_half_over0.5"},
        "2 połowa : liczba goli 1.5 - poniżej/powyżej": {"name": "2nd_half_over1.5"},
        "2 połowa : liczba goli 2.5 - poniżej/powyżej": {"name": "2nd_half_over2.5"},
        "2 połowa handicap (-1.5)": {"name": "2nd_half_eh-1.5"},
        "2 połowa handicap (+1.5)": {"name": "2nd_half_eh+1.5"},
        "1 drużyna : liczba strzelonych goli":{"name":"1st_team_goal_number"},
        "2 drużyna : liczba strzelonych goli": {"name": "2nd_team_goal_number"},
        "1 drużyna : liczba strzelonych goli 1.5 poniżej/powyżej": {"name": "1st_team_over1.5"},
        "1 drużyna : liczba strzelonych goli 2.5 poniżej/powyżej": {"name": "1st_team_over2.5"},
        "1 drużyna : liczba strzelonych goli 3.5 poniżej/powyżej": {"name": "1st_team_over3.5"},
        "1 drużyna : liczba strzelonych goli 4.5 poniżej/powyżej": {"name": "1st_team_over4.5"},
        "2 drużyna : liczba strzelonych goli 1.5 poniżej/powyżej": {"name": "2nd_team_over1.5"},
        "2 drużyna : liczba strzelonych goli 2.5 poniżej/powyżej": {"name": "2nd_team_over2.5"},
        "2 drużyna : liczba strzelonych goli 3.5 poniżej/powyżej": {"name": "2nd_team_over3.5"},
        "2 drużyna : liczba strzelonych goli 4.5 poniżej/powyżej": {"name": "2nd_team_over4.5"},
        "1 drużyna : strzeli gola w obu połowach": {"name": "1st_team_both_half_to_score"},
        "2 drużyna : strzeli gola w obu połowach": {"name": "2nd_team_both_half_to_score"},
        "1 drużyna strzeli gola w 1 połowie": {"name": "1st_team_1st_half_to_score"},
        "2 drużyna strzeli gola w 1 połowie": {"name": "2nd_team_2nd_half_to_score"},
        "oba zespoły strzelą gola w 1 połowie": {"name": "1st_half_btts"},
        "1 drużyna strzeli gola w 2 połowie": {"name": "1st_team_2nd_half_to_score"},
        "2 drużyna strzeli gola w 2 połowie": {"name": "2nd_team_2nd_half_to_score"},
        "oba zespoły strzelą gola w 2 połowie": {"name": "2nd_half_btts"},
        "1 drużyna : wygra do zera": {"name": "1st_team_win_to_0"},
        "2 drużyna : wygra do zera": {"name": "2nd_team_win_to_0"},
        "1 drużyna : wygra obie połowy meczu": {"name": "1st_team_both_half_to_win"},
        "2 drużyna : wygra obie połowy meczu": {"name": "2nd_team_both_half_to_win"},
        "1 drużyna : wygra przynajmniej jedną połowę": {"name": "1st_team_lose_one_half"},
        "2 drużyna : wygra przynajmniej jedną połowę": {"name": "2nd_team_lose_one_half"},
        "obie połowy powyżej 1.5 gola": {"name": "both_half_over1.5"},
        "obie połowy poniżej 1.5 gola": {"name": "both_half_under1.5"},
        "będzie gol do 27 minuty": {"name": "goal_bf_27min"},
        "będzie gol po 72 minucie": {"name": "goal_af_72_min"},
        "liczba rzutów rożnych 8.5 - poniżej/powyżej": {"name": "corners_over8.5"},
        "liczba rzutów rożnych 9.5 - poniżej/powyżej": {"name": "corners_over9.5"},
        "liczba rzutów rożnych 10.5 - poniżej/powyżej": {"name": "corners_over10.5"},
        "liczba rzutów rożnych 11.5 - poniżej/powyżej": {"name": "corners_over11.5"},
        "liczba rzutów rożnych 12.5 - poniżej/powyżej": {"name": "corners_over12.5"},
        "liczba rzutów rożnych - nieparzysta/parzysta": {"name": "corners_odd_even"},
        "liczba rzutów rożnych w meczu": {"name": "corners"},
        "rzuty rożne - kto wykona więcej ?  (remis zwrot)": {"name": "corners_which_team_dnb"},
        "rzuty rożne - kto wykona więcej ? (remis zwrot)": {"name": "corners_which_team_dnb"},
        "rzuty rożne - kto wykona więcej ?  (remis = zwrot)": {"name": "corners_which_team_dnb"},
        "rzuty rożne - kto wykona więcej ? (remis = zwrot)": {"name": "corners_which_team_dnb"},
        "rzuty rożne - kto wykona więcej (handicap)": {"name": "corners_which_team_eh"},
        "rzuty rożne - kto wykona więcej ?": {"name": "corners_which_team"},
        "1 drużyna : liczba rz. rożnych mniej/więcej": {"name": "1st_team_corners"},
        "2 drużyna : liczba rz. rożnych mniej/więcej": {"name": "2nd_team_corners"},
        "liczba żółtych kartek w meczu": {"name": "yellow_cards_number"},
        "liczba żółtych kartek w meczu": {"name": "yellow_cards_number"},
        "liczba żółtych kartek w meczu": {"name": "yellow_cards_number"},
        "1 drużyna : liczba żółtych kartek mniej/więcej": {"name": "1st_team_yellow_cards_number"},
        "2 drużyna : liczba żółtych kartek mniej/więcej": {"name": "2nd_team_yellow_cards_number"},
        "czy będzie czerwona kartka ?": {"name": "red_card"},
        "czy będzie rzut karny ?": {"name": "penalty"},
        "czy bedzie gol rezerwowego ?": {"name": "subs_to_score"},
        "czy będzie gol samobójczy ?": {"name": "own_goal"},
        "liczba spalonych w meczu": {"name": "offsides_number"},
        "liczba fauli w meczu": {"name": "fouls_number"},
        "liczba strzałów w światło bramki": {"name": "shots_on_target"},
        "strzały w światło bramki - która drużyna więcej  (remis zwrot)": {"name": "shots_on_target_which_team_dnb"},
        "strzały w światło bramki - która drużyna więcej":{"name": "shots_on_target_which_team"},
        "1 drużyna : liczba strzałów w światło bramki mniej/więcej": {"name": "1st_team_shots_on_target"},
        "2 drużyna : liczba strzałów w światło bramki mniej/więcej": {"name": "2nd_team_shots_on_target"},
        "procentowe posiadanie piłki   (remis zwrot)": {"name": "ball_possesion_dnb"},
        "1 drużyna : procentowe posiadanie piłki mniej/więcej": {"name": "1st_team_ball_possesion"},
        "padnie bramka w doliczonym czasie gry (1p. lub 2p.)?": {"name": "added_time_goal_1_or_2_half"},
        "będzie wykorzystany limit zmian zaw.  (6)": {"name": "subs_number"},
        "będzie zmiana w 1. połowie meczu" : {"name":"1st_half_subs"},
        "zawodnik : strzeli gola" : {"name":"scorer"},
        "zawodnik : strzeli przynajmniej dwa gole" : {"name": "2goals_scorer"},
        "zawodnik : strzeli przynajmniej trzy gole" : {"name": "3goals_scorer"},
        "zawodnik : strzeli i jego zespół wygra" : {"name": "scorer_team_win"},
        "zawodnik : otrzyma kartkę" : {"name": "card_who"},
        "która drużyna popełni więcej fauli?":{"name":"more_fouls"},
        "1 drużyna : liczba fauli mniej/więcej":{"name":"1st_team_fouls"},
        "2 drużyna : liczba fauli mniej/więcej": {"name": "2nd_team_fouls"},
        "procentowe posiadanie piłki   (Remis zwrot)":{"name":"ball_possesion_dnb"},
        "doliczony czas 1. połowy (1.5 minuty)":{"name":"added_time_1_st_half_15_min"},
        "doliczony czas 1. połowy (3.5 minuty)": {"name": "added_time_1_st_half_35_min"},
        "doliczony czas 2. połowy (1.5 minuty)": {"name": "added_time_2nd_half_15_min"},
        "doliczony czas 2. połowy (3.5 minuty)": {"name": "added_time_2nd_half_35_min"},
        "R. Lewandowski strzeli bramkę z rzutu karnego":{"name":"lewy_to_score"},
        "M. Pazdan otrzyma czerwoną kartkę":{"name":"pazdan_red"},
        "procentowe posiadanie piłki":{"name":"ball_possesion"},
        "2 drużyna : procentowe posiadanie piłki mniej/więcej":{"name":"2nd_team_ball_possesion"},
        "1 drużyna : procentowe posiadanie piłki mniej/więcej": {"name": "2nd_team_ball_possesion"},


    }

    discipline='football'
    def map(self,__events_mapping):
        #print (self.__events_mapping)
        return self.__events_mapping

    def get_name(self,data):
        soup = BeautifulSoup(data, "html.parser")
        # get all the games
        games = soup.find_all('table', {'class': 'col3'})
        game_teams = soup.find('div', {'class': 'shadow_box support_bets_offer'}).h2.text.strip()
        current_time=datetime.datetime.now()
        self.update_time=str('{:04d}'.format(current_time.year))+'-'+str('{:02d}'.format(current_time.month))+'-'+str('{:02d}'.format(current_time.day))+ \
                         '-' + str('{:02d}'.format(current_time.hour)) + '-' + str('{:02d}'.format(current_time.minute)) + '-' + str('{:02d}'.format(current_time.second))
        self.home=unify_name(game_teams.split(' - ')[0].strip(),teams,logging)
        self.away = unify_name(game_teams.split(' - ')[1].strip(), teams, logging)
        self.home_all_names=teams[self.home]
        self.away_all_names=teams[self.away]
        print ("ALL_NAMES_HOME",sorted(self.home_all_names,key=len,reverse=True), self.home)
        print ("ALL_NAMES_AWAY",sorted(self.away_all_names, key=len, reverse=True), self.away)

        self.home_raw=game_teams.split(' - ')[0].strip()
        self.away_raw=game_teams.split(' - ')[1].strip()
        self.date = game_teams.split(' - ')[2]
        self.hour = game_teams.split(' - ')[3]
        #print ("TIME",self.hour)
        self.league=unify_name(soup.find('h2', {'class':'headline'}).text.strip().split(',')[0]+soup.find('h2', {'class':'headline'}).text.strip().split(',')[1],leagues,logging)
        self.country=soup.find('h2', {'class':'headline'}).text.strip().split(',')[1]
        #logging.info(game_teams)
        self.names=self.__events_mapping.values()
        return game_teams
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
        #for key in self.__events_mapping.values():
        #    dict[key]=''
        #ADD MISSING ODDS TO DICT:

        for i in self.names:
            if i['name'] not in self.odds.keys():
                self.odds[i['name']]=''
        def get_odd_2(napis,x):
            try:
                return napis.get(x,'')
            except:
                pass
        home = self.get_name(data).split(" - ")[0].strip().replace(' ', '')
        away = self.get_name(data).split(" - ")[1].strip().replace(' ','')
        print(home)
        print(away)
        print ("SELF.HOME",self.home)
        #self.dict_sql['home']=self.get_name(data).split(" - ")[0].strip().replace(' ','')
        self.dict_sql['home'] = self.home
        #self.dict_sql['away']=away = self.get_name(data).split(" - ")[1].strip().replace(' ','')
        self.dict_sql['away'] = self.away
        self.dict_sql['sts_game_1']=self.odds['game'][self.home]
        self.dict_sql['sts_game_0']=self.odds['game']['X']
        self.dict_sql['sts_game_2']=self.odds['game'][self.away]
        home_pos=self.home_all_names.index(self.home)
        away_pos=self.away_all_names.index(self.away)
        try:
            self.dict_sql['sts_game_10']=self.odds['game'][self.home_all_names[home_pos] + '/X']
        except:
            self.dict_sql['sts_game_10'] = self.odds['game'][self.home_all_names[home_pos] + 'X']
        try:
            self.dict_sql['sts_game_02']=self.odds['game'][self.away_all_names[away_pos] + '/X']
        except:
            self.dict_sql['sts_game_02'] = self.odds['game'][self.away_all_names[away_pos] + 'X']
        try:
            self.dict_sql['sts_game_12'] = self.odds['game'][self.home_all_names[home_pos] + '/' + self.away]
        except:
            self.dict_sql['sts_game_12'] = self.odds['game'][self.home_all_names[home_pos] + self.away]
        self.dict_sql['data']=self.date.split(' ')[1].split('.')[2]+'-'+self.date.split(' ')[1].split('.')[1]+'-'+self.date.split(' ')[1].split('.')[0]
        self.dict_sql['Sport']=self.discipline
        self.dict_sql['League']=self.league
        self.dict_sql['country']=self.country
        self.dict_sql['sts_update_time']=self.update_time
        self.dict_sql['hour']=self.hour
        self.dict_sql['sts_dnb_1'] = get_odd_2(self.odds['dnb'], home)
        self.dict_sql['sts_dnb_2'] = get_odd_2(self.odds['dnb'], away)
        self.dict_sql['sts_o_05'] = get_odd_2(self.odds['over0.5'], '+')
        self.dict_sql['sts_u_05'] = get_odd_2(self.odds['over0.5'], '-')
        self.dict_sql['sts_o_15'] = get_odd_2(self.odds['over1.5'], '+')
        self.dict_sql['sts_u_15'] = get_odd_2(self.odds['over1.5'], '-')
        self.dict_sql['sts_o_25'] = get_odd_2(self.odds['over2.5'], '+')
        self.dict_sql['sts_u_25'] = get_odd_2(self.odds['over2.5'], '-')
        self.dict_sql['sts_o_35'] = get_odd_2(self.odds['over3.5'], '+')
        self.dict_sql['sts_u_35'] = get_odd_2(self.odds['over3.5'], '-')
        self.dict_sql['sts_o_45'] = get_odd_2(self.odds['over4.5'], '+')
        self.dict_sql['sts_u_45'] = get_odd_2(self.odds['over4.5'], '-')
        self.dict_sql['sts_o_55'] = get_odd_2(self.odds['over5.5'], '+')
        self.dict_sql['sts_u_55'] = get_odd_2(self.odds['over5.5'], '-')
        self.dict_sql['sts_o_65'] = get_odd_2(self.odds['over6.5'], '+')
        self.dict_sql['sts_u_65'] = get_odd_2(self.odds['over6.5'], '-')
        self.dict_sql['sts_o_75'] = get_odd_2(self.odds['over7.5'], '+')
        self.dict_sql['sts_u_75'] = get_odd_2(self.odds['over7.5'], '-')
        self.dict_sql['sts_o_85'] = get_odd_2(self.odds['over8.5'], '+')
        self.dict_sql['sts_u_85'] = get_odd_2(self.odds['over8.5'], '-')
        self.dict_sql['sts_o_95'] = get_odd_2(self.odds['over9.5'], '+')
        self.dict_sql['sts_u_95'] = get_odd_2(self.odds['over9.5'], '-')
        self.dict_sql['sts_ht_ft_11'] = get_odd_2(self.odds['half/end'], '1/1')
        self.dict_sql['sts_ht_ft_1x'] = get_odd_2(self.odds['half/end'], '1/X')
        self.dict_sql['sts_ht_ft_2x'] = get_odd_2(self.odds['half/end'], '2/X')
        self.dict_sql['sts_ht_ft_21'] = get_odd_2(self.odds['half/end'], '2/1')
        self.dict_sql['sts_ht_ft_22'] = get_odd_2(self.odds['half/end'], '2/2')
        self.dict_sql['sts_ht_ft_x1'] = get_odd_2(self.odds['half/end'], 'X/1')
        self.dict_sql['sts_ht_ft_x2'] = get_odd_2(self.odds['half/end'], 'X/2')
        self.dict_sql['sts_ht_ft_12'] = get_odd_2(self.odds['half/end'], '1/2')
        self.dict_sql['sts_ht_ft_xx'] = get_odd_2(self.odds['half/end'], 'X/X')
        self.dict_sql['sts_first_half_1'] = get_odd_2(self.odds['1st_half'], home)
        self.dict_sql['sts_first_half_x'] = get_odd_2(self.odds['1st_half'], 'X')
        self.dict_sql['sts_first_half_2'] = get_odd_2(self.odds['1st_half'], away)
        self.dict_sql['sts_first_half_10'] = get_odd_2(self.odds['1st_half'], home + '/X')
        self.dict_sql['sts_first_half_02'] = get_odd_2(self.odds['1st_half'], away + '/X')
        self.dict_sql['sts_first_half_12'] = get_odd_2(self.odds['1st_half'], home + '/' + away)
        self.dict_sql['sts_eh_min_1_1'] = get_odd_2(self.odds['eh-1'], home + '(-1)')
        self.dict_sql['sts_eh_min_1_x'] = get_odd_2(self.odds['eh-1'], 'X')
        self.dict_sql['sts_eh_min_1_x2'] = get_odd_2(self.odds['eh-1'], away + '/X')
        # self.dict_sql['sts_eh-1_2'] = get_odd_2(self.odds['eh-1'], home + '(-1)')
        self.dict_sql['sts_u_15_1'] = get_odd_2(self.odds['goal1.5/result'], '-1.5/1')
        self.dict_sql['sts_o_15_1'] = get_odd_2(self.odds['goal1.5/result'], '+1.5/1')
        self.dict_sql['sts_u_25_1'] = get_odd_2(self.odds['goal2.5/result'], '-2.5/1')
        self.dict_sql['sts_o_25_1'] = get_odd_2(self.odds['goal2.5/result'], '+2.5/1')
        self.dict_sql['sts_u_25_x'] = get_odd_2(self.odds['goal2.5/result'], '-2.5/X')
        self.dict_sql['sts_o_25_x'] = get_odd_2(self.odds['goal2.5/result'], '+2.5/X')
        self.dict_sql['sts_u_15_x'] = get_odd_2(self.odds['goal1.5/result'], '-1.5/X')
        self.dict_sql['sts_o_15_x'] = get_odd_2(self.odds['goal1.5/result'], '+1.5/X')
        self.dict_sql['sts_u_25_2'] = get_odd_2(self.odds['goal2.5/result'], '-2.5/2')
        self.dict_sql['sts_o_25_2'] = get_odd_2(self.odds['goal2.5/result'], '+2.5/2')
        self.dict_sql['sts_u_25_1'] = get_odd_2(self.odds['goal1.5/result'], '-1.5/2')
        self.dict_sql['sts_o_25_1'] = get_odd_2(self.odds['goal1.5/result'], '+1.5/2')
        self.dict_sql['sts_first_goal_1'] = get_odd_2(self.odds['1st_goal'], home)
        self.dict_sql['sts_first_goal_2'] = get_odd_2(self.odds['1st_goal'], away)
        self.dict_sql['sts_first_goal_0'] = get_odd_2(self.odds['1st_goal'], 'nikt')
        self.dict_sql['sts_btts_1'] = get_odd_2(self.odds['game/btts'], '1/tak')
        self.dict_sql['sts_btts_2'] = get_odd_2(self.odds['game/btts'], '2/tak')
        self.dict_sql['sts_btts_x'] = get_odd_2(self.odds['game/btts'], 'X/tak')
        self.dict_sql['sts_btts_no_1'] = get_odd_2(self.odds['game/btts'], '1/nie')
        self.dict_sql['sts_btts_no_2'] = get_odd_2(self.odds['game/btts'], '2/nie')
        self.dict_sql['sts_btts_no_x'] = get_odd_2(self.odds['game/btts'], 'X/nie')
        self.dict_sql['sts_btts_yes'] = get_odd_2(self.odds['btts'], 'tak')
        self.dict_sql['sts_btts_no'] = get_odd_2(self.odds['btts'], 'nie')
        self.dict_sql['sts_corners_o_65'] = get_odd_2(self.odds['corners_over6.5'], '+')
        self.dict_sql['sts_corners_u_65'] = get_odd_2(self.odds['corners_over6.5'], '-')
        self.dict_sql['sts_corners_o_75'] = get_odd_2(self.odds['corners_over7.5'], '+')
        self.dict_sql['sts_corners_u_75'] = get_odd_2(self.odds['corners_over7.5'], '-')
        self.dict_sql['sts_corners_o_85'] = get_odd_2(self.odds['corners_over8.5'], '+')
        self.dict_sql['sts_corners_u_85'] = get_odd_2(self.odds['corners_over8.5'], '-')
        self.dict_sql['sts_corners_o_95'] = get_odd_2(self.odds['corners_over9.5'], '+')
        self.dict_sql['sts_corners_u_95'] = get_odd_2(self.odds['corners_over9.5'], '-')
        self.dict_sql['sts_corners_o_105'] = get_odd_2(self.odds['corners_over10.5'], '+')
        self.dict_sql['sts_corners_u_105'] = get_odd_2(self.odds['corners_over10.5'], '-')
        self.dict_sql['sts_corners_o_115'] = get_odd_2(self.odds['corners_over11.5'], '+')
        self.dict_sql['sts_corners_u_115'] = get_odd_2(self.odds['corners_over11.5'], '-')
        self.dict_sql['sts_corners_o_125'] = get_odd_2(self.odds['corners_over12.5'], '+')
        self.dict_sql['sts_corners_u_125'] = get_odd_2(self.odds['corners_over12.5'], '-')
        self.dict_sql['sts_corners_o_135'] = get_odd_2(self.odds['corners_over13.5'], '+')
        self.dict_sql['sts_corners_u_135'] = get_odd_2(self.odds['corners_over13.5'], '-')
        self.dict_sql['sts_corners_o_145'] = get_odd_2(self.odds['corners_over14.5'], '+')
        self.dict_sql['sts_corners_u_145'] = get_odd_2(self.odds['corners_over14.5'], '-')
        self.dict_sql['sts_corners_o_155'] = get_odd_2(self.odds['corners_over15.5'], '+')
        self.dict_sql['sts_corners_u_155'] = get_odd_2(self.odds['corners_over15.5'], '-')
        self.dict_sql['sts_corners_o_165'] = get_odd_2(self.odds['corners_over16.5'], '+')
        self.dict_sql['sts_corners_u_165'] = get_odd_2(self.odds['corners_over16.5'], '-')
        self.dict_sql['sts_corners_o_175'] = get_odd_2(self.odds['corners_over17.5'], '+')
        self.dict_sql['sts_corners_u_175'] = get_odd_2(self.odds['corners_over17.5'], '-')

        #print ("DICT: ", self.dict_sql)
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


    def __init__(self):
        self.name=self.get_name(data)
        #self.home=self.get_home(self.name)
        self.get_odds(data)
        #print (self.odds)
        self.prepare_dict_to_sql()
        self.date2 = "'" + self.date.split(' ')[1].split('.')[2] + '-' + self.date.split(' ')[1].split('.')[1] + '-' + \
               self.date.split(' ')[1].split('.')[0] + "'"
        file=open('odd','w')
        file.write(str(self.odds))


data=codecs.open('www.sts.pl.htm',mode='r',encoding='utf-8').read()
#data=urllib2.urlopen('https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6507&league=4013&oppty=130931499').read()
#url='https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6527&league=4074&oppty=149243022'
#user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
#headers = {'User-Agent': user_agent, }
#request = urllib2.Request(url, None, headers)
#data=urllib2.urlopen(request).read()
#meczyk=football_event()
#print (meczyk.odds)
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
for site in sites2:
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib2.Request(site, None, headers)
    response = urllib2.urlopen(request)
    strona = response.read()
    print (site)

    #strona=urllib2.urlopen(site).read()
    soup = BeautifulSoup(strona, "html.parser")
    #print (soup)
    more_bets=soup.find_all('td', {'class': 'support_bets'})
    more_bets = soup.find_all('td')
    print("MORE",more_bets)
    print ("JESTEM TU")
    #more_bets=['https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6499&league=3903&oppty=152636192']
    for a in more_bets:
    #    print ("A: ",a)
        try:
            link=a.find('a', href = True)
            #link={}
            #link['href']='https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6499&league=3903&oppty=152636192'
    #    print ("LINK: ", link['href'])
            print("JESTEM TU TEŻ")
            request = urllib2.Request(link['href'], None, headers)
            data=urllib2.urlopen(request).read()

            meczyk=football_event()
            save_to_db_common(meczyk,meczyk.date2)
        except:
            logging.basicConfig(filename='logfile.log', level=logging.DEBUG)
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

