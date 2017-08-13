#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# encoding=utf8
from bs4 import BeautifulSoup
import urllib.request as urllib2
#import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import platform
from selenium import webdriver
import codecs, sys
import json
import sqlite3
from collections import defaultdict
import logging


class football_event:
    logging.basicConfig(filename='logfile.log', level=logging.DEBUG)
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
        "1 drużyna strzeli gola":{"name":"1st_team_to_score"},
        "2 drużyna strzeli gola":{"name": "2nd_team_to_score"},
        "obie drużyny strzelą gola":{"name": "btts"},
        "handicap 0:1": {"name": "eh-1"},
        "handicap 1:0": {"name": "eh+1"},
        "handicap (-2.5)": {"name":"eh-2.5"},
        "handicap (-3.5)": {"name": "eh-3.5"},
        "handicap (-4.5)": {"name": "eh-4.5"},
        "dokładny wynik (1)": {"name": "cs"},
        "dokładny wynik (2)": {"name": "cs"},
        "dokładny wynik (3)": {"name": "cs"},
        "liczba goli 2.5/wynik meczu": {"name": "goal2.5/result"},
        "wynik meczu/obie drużyny strzelą": {"name": "game/btts"},
        "obie drużyny strzelą gola/ilość goli 2.5": {"name": "btts/o2.5"},
        "pierwszy gol w meczu": {"name": "1st_goal"},
        "podwójna szansa": {"name": "dc"},
        "w której połowie więcej goli": {"name": "ht_more"},
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
        "1 drużyna : liczba strzelonych goli 1.5 poniżej/powyżej": {"name": "1st_team_over1.5"},
        "1 drużyna : liczba strzelonych goli 2.5 poniżej/powyżej": {"name": "1st_team_over2.5"},
        "2 drużyna : liczba strzelonych goli 1.5 poniżej/powyżej": {"name": "2nd_team_over1.5"},
        "2 drużyna : liczba strzelonych goli 2.5 poniżej/powyżej": {"name": "2nd_team_over2.5"},
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
        "rzuty rożne - kto wykona więcej ?  (remis zwrot)": {"name": "corners_which_team_dnb"},
        "rzuty rożne - kto wykona więcej (handicap)": {"name": "corners_which_team_eh"},
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
        "1 drużyna : liczba strzałów w światło bramki mniej/więcej": {"name": "1st_team_shots_on_target"},
        "2 drużyna : liczba strzałów w światło bramki mniej/więcej": {"name": "2nd_team_shots_on_target"},
        "procentowe posiadanie piłki   (remis zwrot)": {"name": "ball_possesion_dnb"},
        "1 drużyna : procentowe posiadanie piłki mniej/więcej": {"name": "1st_team_ball_possesion"},
        "padnie bramka w doliczonym czasie gry (1p. lub 2p.)?": {"name": "added_time_goal_1_or_2_half"},
        "będzie wykorzystany limit zmian zaw.  (6)": {"name": "subs_number"},
        "zawodnik : strzeli gola" : {"name":"scorer"},
        "zawodnik : strzeli przynajmniej dwa gole" : {"name": "2goals_scorer"},
        "zawodnik : strzeli przynajmniej trzy gole" : {"name": "3goals_scorer"},
        "zawodnik : strzeli i jego zespół wygra" : {"name": "scorer_team_win"},
        "zawodnik : otrzyma kartkę" : {"name": "card_who"}


    }
    discipline='football'
    def map(self,__events_mapping):
        print (self.__events_mapping)
        return self.__events_mapping

    def get_name(self,data):
        soup = BeautifulSoup(data, "html.parser")
        # get all the games
        games = soup.find_all('table', {'class': 'col3'})
        game_teams = soup.find('div', {'class': 'shadow_box support_bets_offer'}).h2.text.strip()
        self.home=game_teams.split(' - ')[0]
        self.away = game_teams.split(' - ')[1]
        self.date = game_teams.split(' - ')[2]
        self.time = game_teams.split(' - ')[3]
        self.league=soup.find('h2', {'class':'headline'}).text.strip().split(',')[0]
        self.country=soup.find('h2', {'class':'headline'}).text.strip().split(',')[1]
        logging.info(game_teams)
        self.names=self.__events_mapping.values()
        return game_teams
    def correct_name(self,name):
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
        self.odds = {}
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
                name = self.fix_for_cup(name)
                self.odd_type=self.__events_mapping[name]["name"]
            except:
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
                    x = col.text.strip().replace(' ','').split('\n')
                #print x
                    try:
                        x[0]=self.correct_name(x[0])
                        self.odds[self.odd_type][x[0]]=float(x[1])
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
                self.odd_type=self.__events_mapping[odd_t.tr.th.span.text.strip()]["name"]
            except:
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
                x = col.text.strip().replace(' ','').split('\n')
                #print ("X: ",x)
                try:
                    self.odds[self.odd_type][x[0]]=float(x[1])
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
            x = cols.text.strip().replace(' ', '').split('\n')
            #print ("X: ",x)
            try:
                self.odds[self.odd_type][self.sub_name] = float(x[1])
            except:
                    # print ("nieznany zaklad:")
                    # print (col.text.strip().replace(' ','').split('\n'))
                continue
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
                logging.warning("Nie znalazlem kursu: ")
                return ''
        home = self.get_name(data).split(" - ")[0].strip().replace(' ', '')
        away = self.get_name(data).split(" - ")[1].strip().replace(' ','')
        self.dict_sql['home']=self.get_name(data).split(" - ")[0].strip().replace(' ','')
        self.dict_sql['away']=away = self.get_name(data).split(" - ")[1].strip().replace(' ','')
        self.dict_sql['_1']=self.odds['game'][home]
        self.dict_sql['_0']=self.odds['game']['X']
        self.dict_sql['_2']=self.odds['game'][away]
        self.dict_sql['_10']=self.odds['game'][home + '/X']
        self.dict_sql['_02']=self.odds['game'][away + '/X']
        self.dict_sql['_12']=self.odds['game'][home + '/' + away]
        self.dict_sql['data']=self.date.split(' ')[1].split('.')[2]+'-'+self.date.split(' ')[1].split('.')[1]+'-'+self.date.split(' ')[1].split('.')[0]
        self.dict_sql['Sport']=self.discipline
        self.dict_sql['League']=self.league
        self.dict_sql['country']=self.country
        self.dict_sql['dnb_1']=get_odd_2(self.odds['dnb'],home)
        self.dict_sql['dnb_2']=get_odd_2(self.odds['dnb'],away)
        self.dict_sql['o_05']=get_odd_2(self.odds['over0.5'],'+')
        self.dict_sql['u_05'] = get_odd_2(self.odds['over0.5'], '-')
        self.dict_sql['o_15'] = get_odd_2(self.odds['over1.5'],'+')
        self.dict_sql['u_15'] = get_odd_2(self.odds['over1.5'], '-')
        self.dict_sql['o_25'] = get_odd_2(self.odds['over2.5'],'+')
        self.dict_sql['u_25'] = get_odd_2(self.odds['over2.5'], '-')
        self.dict_sql['o_35'] = get_odd_2(self.odds['over3.5'],'+')
        self.dict_sql['u_35'] = get_odd_2(self.odds['over3.5'], '-')
        self.dict_sql['o_45'] = get_odd_2(self.odds['over4.5'],'+')
        self.dict_sql['u_45'] = get_odd_2(self.odds['over4.5'], '-')
        self.dict_sql['o_55'] = get_odd_2(self.odds['over5.5'],'+')
        self.dict_sql['u_55'] = get_odd_2(self.odds['over5.5'], '-')
        self.dict_sql['o_65'] = get_odd_2(self.odds['over6.5'],'+')
        self.dict_sql['u_65'] = get_odd_2(self.odds['over6.5'], '-')
        self.dict_sql['o_75'] = get_odd_2(self.odds['over7.5'],'+')
        self.dict_sql['u_75'] = get_odd_2(self.odds['over7.5'], '-')
        self.dict_sql['o_85'] = get_odd_2(self.odds['over8.5'],'+')
        self.dict_sql['u_85'] = get_odd_2(self.odds['over8.5'], '-')
        self.dict_sql['o_95'] = get_odd_2(self.odds['over9.5'],'+')
        self.dict_sql['u_95'] = get_odd_2(self.odds['over9.5'], '-')
        self.dict_sql['ht_ft_11'] = get_odd_2(self.odds['half/end'], '1/1')
        self.dict_sql['ht_ft_1x'] = get_odd_2(self.odds['half/end'], '1/X')
        self.dict_sql['ht_ft_2x'] = get_odd_2(self.odds['half/end'], '2/X')
        self.dict_sql['ht_ft_21'] = get_odd_2(self.odds['half/end'], '2/1')
        self.dict_sql['ht_ft_22'] = get_odd_2(self.odds['half/end'], '2/2')
        self.dict_sql['ht_ft_x1'] = get_odd_2(self.odds['half/end'], 'X/1')
        self.dict_sql['ht_ft_x2'] = get_odd_2(self.odds['half/end'], 'X/2')
        self.dict_sql['ht_ft_12'] = get_odd_2(self.odds['half/end'], '1/2')
        self.dict_sql['ht_ft_xx'] = get_odd_2(self.odds['half/end'], 'X/X')
        self.dict_sql['_1st_half_1']= get_odd_2(self.odds['1st_half'], home)
        self.dict_sql['_1st_half_x'] = get_odd_2(self.odds['1st_half'], 'X')
        self.dict_sql['_1st_half_2'] = get_odd_2(self.odds['1st_half'], away)
        self.dict_sql['_1st_half_10'] = get_odd_2(self.odds['1st_half'],[home + '/X'])
        self.dict_sql['_1st_half_02'] = get_odd_2(self.odds['1st_half'],[away + '/X'])
        self.dict_sql['_1st_half_12'] = get_odd_2(self.odds['1st_half'],[home + '/' + away])
        self.dict_sql['eh-1_1'] = get_odd_2(self.odds['eh-1'],home + '(-1)')
        self.dict_sql['eh-1_x2'] = get_odd_2(self.odds['eh-1'],away + '/X')
        self.dict_sql['u_25_1'] = get_odd_2(self.odds['goal2.5/result'],'-2.5/1')
        self.dict_sql['o_25_1'] = get_odd_2(self.odds['goal2.5/result'],'+2.5/1')
        self.dict_sql['u_25_x'] = get_odd_2(self.odds['goal2.5/result'],'-2.5/X')
        self.dict_sql['o_25_x'] = get_odd_2(self.odds['goal2.5/result'],'+2.5/X')
        self.dict_sql['u_25_2'] = get_odd_2(self.odds['goal2.5/result'],'-2.5/2')
        self.dict_sql['o_25_2'] = get_odd_2(self.odds['goal2.5/result'],'+2.5/2')
        self.dict_sql['1_st_goal_1'] = get_odd_2(self.odds['1st_goal'],home)
        self.dict_sql['1_st_goal_2'] = get_odd_2(self.odds['1st_goal'],away)
        self.dict_sql['1_st_goal_0'] = get_odd_2(self.odds['1st_goal'],'nikt')



        print ("DICT: ", self.dict_sql)
        return self.dict_sql

    def save_to_db(meczyk):
        database_name = 'db.sqlite'
        db = sqlite3.connect(database_name)
        home = meczyk.get_name(data).split(" - ")[0].strip().replace(' ','')
        print ("Home:", home)
        away = meczyk.get_name(data).split(" - ")[1].strip().replace(' ','')
        print ("Away:", away)
        date = meczyk.get_name(data).split(" - ")[2]
        print ("Date:", date)
        try:
            o_05=meczyk.odds.get('over0.5','-')['+']
        except:
            o_05 = '-'
        sqldate=meczyk.date.split(' ')[1].split('.')[2]+'-'+meczyk.date.split(' ')[1].split('.')[1]+'-'+meczyk.date.split(' ')[1].split('.')[0]
        table='"db_sts"'
        columns_string = '("' + '","'.join(meczyk.dict_sql.keys()) + '")'
        values_string = '("' + '","'.join(map(str, meczyk.dict_sql.values())) + '")'
        sql = """INSERT INTO %s %s
             VALUES %s""" % (table, columns_string, values_string)
        print (sql)
        db.execute(sql)
        db.commit()


    def __init__(self):
        self.name=self.get_name(data)
        #self.home=self.get_home(self.name)
        print ("SELF NAME:")
        print (self.name)
        print ("SELF HOME:")
        print (self.home)
        print ("SELF AWAY:")
        print (self.away)
        print ("SELF DATE:")
        print (self.date)
        print ("SELF TIME:")
        print (self.time)
        self.get_odds(data)
        #print (self.odds)
        self.prepare_dict_to_sql()
        file=open('odd','w')
        file.write(str(self.odds))


strona=urllib2.urlopen('https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6482&league=4079').read()
soup = BeautifulSoup(strona, "html.parser")
more_bets=soup.find_all('td', {'class': 'support_bets'})
for a in more_bets:
#    print ("A: ",a)
    link=a.find('a', href = True)
#    print ("LINK: ", link['href'])
    data=urllib2.urlopen(link['href']).read()
    try:
        meczyk=football_event()
        meczyk.save_to_db()
    except:
        logging.basicConfig(filename='logfile.log', level=logging.DEBUG)
        logging.warning("ERROR dla: "+link.text)
        continue


data=codecs.open('www.sts.pl.htm',mode='r',encoding='utf-8').read()
#data=urllib2.urlopen('https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6535&league=3994&oppty=85142253').read()

meczyk=football_event()
meczyk.prepare_dict_to_sql()
#print (meczyk.odds)
meczyk.save_to_db()
###DOROBIC DC###





#if platform.system() == 'Windows':
#    PHANTOMJS_PATH = './phantomjs.exe'
#else:
#    PHANTOMJS_PATH = './phantomjs'

#browser = webdriver.PhantomJS(PHANTOMJS_PATH)
#browser = webdriver.Firefox()

#browser.get('https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6502&league=4163')

#soup = BeautifulSoup(browser.page_source, "html.parser")

