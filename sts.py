#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# encoding=utf8
from bs4 import BeautifulSoup
#import urllib2
#import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import platform
from selenium import webdriver
import codecs, sys
import json


class one_event:
    __events_mapping={
        "mecz":{"name":"game"},
        "zakład bez remisu (remis=zwrot)":{"name":"dnb"},
        "liczba goli w meczu 1.5 - poniżej/powyżej ":{"name":"over1.5"},
        "liczba goli w meczu 2.5 - poniżej/powyżej ": {"name": "over2.5"},
        "liczba goli w meczu 3.5 - poniżej/powyżej ": {"name": "over3.5"},
        "liczba goli w meczu 4.5 - poniżej/powyżej ": {"name": "over4.5"},
        "liczba goli w meczu 5.5 - poniżej/powyżej ": {"name": "over5.5"},
        "liczba goli w meczu 6.5 - poniżej/powyżej ": {"name": "over6.5"},
        "liczba goli w meczu 7.5 - poniżej/powyżej ": {"name": "over7.5"},
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
    }

    def get_name(self,data):
        soup = BeautifulSoup(data, "html.parser")
        # get all the games
        games = soup.find_all('table', {'class': 'col3'})
        game_teams = soup.find('div', {'class': 'shadow_box support_bets_offer'}).h2.text.strip()
        self.home=game_teams.split(' - ')[0]
        self.away = game_teams.split(' - ')[1]
        self.date = game_teams.split(' - ')[2]
        self.time = game_teams.split(' - ')[3]
        return game_teams
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
                self.odd_type=self.__events_mapping[odd_t.tr.th.span.text.strip()]["name"]
            except:
                self.odd_type=odd_t.tr.th.span.text.strip()
                print ("Nie ma: %s", odd_t.tr.th.span.text.strip() )
            odd_t2=games.find('tbody')
            #print "TU JEST KURS:"
            cols=games.find('tbody').find('tr').find_all('td')
            i=0
            self.odds[self.odd_type] = {}
            for col in cols:
                #print col.text.strip().split(' ')[-1]
                x = col.text.strip().replace(' ','').split('\n')
                #print x
                try:
                    self.odds[self.odd_type][x[0]]=float(x[1])
                except:
                    print ("nieznany zaklad:")
                    print (col.text.strip().replace(' ','').split('\n'))
                    continue
                i=i+1
        games_col2 = soup.find_all('table', {'class': 'col2'})
        for games in games_col2:
            odd_t=games.find('thead')
            #print odd_t
            try:
                #print ("TEXT:")
                #print (odd_t.tr.th.span.text.strip())
                #print (codecs.encode(odd_t.tr.th.span.text.strip(),encoding='utf-8'))
                self.odd_type=self.__events_mapping[odd_t.tr.th.span.text.strip()]["name"]
            except:
                self.odd_type=odd_t.tr.th.span.text.strip()
                print ("Nie ma: %s", odd_t.tr.th.span.text.strip() )
            odd_t2=games.find('tbody')
            #print "TU JEST KURS:"
            cols=games.find('tbody').find('tr').find_all('td')
            i=0
            self.odds[self.odd_type] = {}
            for col in cols:
                #print col.text.strip().split(' ')[-1]
                x = col.text.strip().replace(' ','').split('\n')
                #print x
                try:
                    self.odds[self.odd_type][x[0]]=float(x[1])
                except:
                    print ("nieznany zaklad:")
                    print (col.text.strip().replace(' ','').split('\n'))
                    continue
                i=i+1



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
        print ("ODD TYPE:")
        print (self.odd_type)
        print (self.odds)


data=codecs.open('www.sts.pl.htm',mode='r',encoding='utf-8').read()
meczyk=one_event()

#if platform.system() == 'Windows':
#    PHANTOMJS_PATH = './phantomjs.exe'
#else:
#    PHANTOMJS_PATH = './phantomjs'

#browser = webdriver.PhantomJS(PHANTOMJS_PATH)
#browser = webdriver.Firefox()

#browser.get('https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6502&league=4163')

#soup = BeautifulSoup(browser.page_source, "html.parser")

soup=BeautifulSoup(data,"html.parser")
# get all the games
games = soup.find_all('table', {'class': 'col3'})
game_teams=soup.find('div',{'class':'shadow_box support_bets_offer'}).h2.text.strip()
#print "GAME:"
#print game_teams
# and print out the html for first game
#print(games[0].prettify())
head2=[]
odds={}
for game in games:
    heads=game.find_all('thead')
    for head in heads:
        head2.append(head.text.strip())
    body=game.find('tbody')
    rows=body.find_all('tr')
    for row in rows:
        #print soup.prettify(row)
#        print heads[0].text.strip()
#        print row.text.strip().replace("\n"," ").replace("  "," ")
        x=row.text.strip()
        odds[game_teams]=row.text.strip().replace("\n"," ").replace("  "," ")

#print "HEAD2:"
#print head2

#print "ODDS:"
#print odds
exit()

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
    print ("Additional info:")
    print (additional_info)
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
                #print "Nie poszlo:"
                #print td
                #print td.text.strip()
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
#print("/////////////////")
head2=head2[0].replace('  ',' ').replace('  ',' ').split(' ')
head2.append("Sport")
head2.append("League")
#print head2
#print game
#print len(head2)


#for i in game:
#    print i
#print head2
#print game
x=pd.DataFrame(game, columns=head2)
#print x
engine = create_engine('sqlite:///db.sqlite')
x.to_sql('db_fortuna', engine)
#x.to_sql('sqlite:///db_table2', sqlite3)
exit()


table=soup.find_all(class_='bet_tables_holder')

#for link in soup.find_all('bet_item_main_text'):
#    print(link.get('href'))
