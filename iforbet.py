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
import json
import re
#import requests
#data = requests.get("https://www.iforbet.pl/zdarzenie/460411")
#html_contents = page.text

#url = "http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers"

#data=urllib2.Request('https://www.iforbet.pl/zdarzenie/460411',None,headers)
#response = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers))
#site='https://www.iforbet.pl/zdarzenie/545659'
#request = urllib2.Request(site, None, headers)
#response = urllib2.urlopen(request)
#data = response.read() # The data u need
#print ("DATA:", data)
#exit()
#data=codecs.open('fortuna.html',mode='r',encoding='utf-8').read()
logging.basicConfig(filename='logfile_iforbet.log', level=logging.DEBUG)
class football_event:
    #soup = BeautifulSoup(data,"html.parser")
    logging.basicConfig(filename='logfile_iforbet.log', level=logging.DEBUG)

    def get_events_mapping(self):
        return self.__events_mapping
    def get_current_time(self):
        self.current_time = datetime.datetime.now()
        return self.current_time
    def get_name(self):
        #soup = BeautifulSoup(data, "html.parser")
        #print (soup)
        json_var=json.loads(data)
        self.json_var=json_var
#        print (json_var["data"])
        self.raw_home=json_var['data']['eventName'].split(' - ')[0]
        self.raw_home_part=self.raw_home.split(' ')[0]
        self.raw_away = json_var['data']['eventName'].split(' - ')[1]
        self.raw_away_part = self.raw_away.split(' ')[0]
        self.home=unify_name(json_var['data']['eventName'].split(' - ')[0],teams,logging)
#        print ("HHHHOME",self.home)
        self.away=unify_name(json_var['data']['eventName'].split(' - ')[1],teams,logging)
#        raw_league_name=self.game.find('div',{'id':'event-lvl3-name'}).text+' '+self.game.find('div',{'id':'event-lvl2-name'}).text
#        raw_league=soup.find('span',{'class':'header-navigation-site'}).text

        #print ("SOUP:", soup)
        #print ("X: ",raw_league)
        self.league=unify_name(json_var['data']['category3Name']+' '+json_var['data']['category2Name'],leagues,logging)
        print ("LEAGUE:",self.league)
        print (self.home,self.away)

        raw_date=json_var['data']['eventStart']

        date=datetime.datetime.fromtimestamp(raw_date/1000)
        self.raw_date=date
        current_time=datetime.datetime.now()

        day=date.day
        month = date.month
        hour=date.hour
        minute=date.minute
        print ("DAY:",day,month,hour,minute)
        full_date=datetime.datetime(current_time.year,int(month),int(day),int(hour),int(minute))
        self.update_time=str('{:04d}'.format(current_time.year))+'-'+str('{:02d}'.format(current_time.month))+'-'+str('{:02d}'.format(current_time.day))+\
        '-' + str('{:02d}'.format(current_time.hour))+'-'+str('{:02d}'.format(current_time.minute))+'-'+str('{:02d}'.format(current_time.second))
        self.date=str(full_date.year)+'-'+str('{:02d}'.format(full_date.month))+'-'+str('{:02d}'.format(full_date.day))
        #print("DATTTTEE",self.date)
        self.hour=str('{:02d}'.format(full_date.hour))+':'+str('{:02d}'.format(full_date.minute))


    def correct_name(self, name):
        try:
            return name.split('(')[1].split(')')[0]
        except:
            return name

    def correct_stupid_names(self,x):
        correct_names={'RB Lipsk':'RB Leipzig'}
        if x in correct_names.keys():
            return correct_names[x]
        else:
            return x
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
                name=self.extract_team_name(odd_tittle.span.text,self.raw_home,self.raw_away)
                if name not in events_mapping_iforbet.keys():
                    logging.warning("Nieznany zaklad: "+odd_tittle.span.text)
                self.odds[events_mapping_iforbet[name]["name"]]=defaultdict(str)
                #print ("Span:",odd_tittle.span.text)
            except:
                pass
            odd_values=table.find_all('div',{'class':'event-rate'})
#            print ("NAME:",name)
            for odd in odd_values:
                rows=odd.find_all('div',{'class':'outcome-row'})
                if len(rows)==0:
                    odd_name = odd.find('div', {'class': 'outcome-name'})
                    #print ("ODD_name: ", odd_name.text)
                    odd_rate = odd.find('span', {'class': 'rate-value'})
                    #print ("ODD_rate: ", odd_rate.text)
                    odd_name_corr=self.extract_team_name(odd_name.text,self.raw_home,self.raw_away)
                    #print ("ODD_NAME", odd_name_corr)
                    try:
                        #print ("NAME:", name)
                        self.odds[events_mapping_iforbet[name]["name"]][odd_name_corr] = odd_rate.text
                    except:
                        logging.warning("Nieznany zaklad 2: "+name)
                        pass
                else:
                    for row in rows:
                        odd_name=row.find('div',{'class':'outcome-name'})
                        print ("ODD_name: ",odd_name.text)
                        odd_rate=row.find('span',{'class':'rate-value'})
                        print ("ODD_rate: ", odd_rate.text)
                    #self.odds[name][odd_name.text]={}
                        odd_name_corr = self.extract_team_name(odd_name.text, self.raw_home, self.raw_away)
                        try:
                            self.odds[self.events_mapping_iforbet[name]["name"]][odd_name_corr]=odd_rate.text
                        except:
                            logging.warning("Nieznany zaklad 3: "+name)
                            pass
        import json
        #print (json.dumps(self.odds, indent=4, sort_keys=False))
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
                if name not in events_mapping_iforbet.keys():
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
    def get_rate(self,json, name, raw_home,log=0):
        for i in range(0, len(json['eventGames'])):
            x=''
            error=1
            if json['eventGames'][i]['gameName'].lower() == name.lower():
                for j in range(0, len(json['eventGames'][i]['outcomes'])):
                    x=json['eventGames'][i]['outcomes'][j]['outcomeName'].lower()
                    if ' ' in x and 'bramki' not in x:
                        tmp=x.split(' ')[1]
                        tmp2=x.split(' ')[0]
                    else:
                        tmp="napis_bez_sensu"
                        tmp2=tmp
                    if (x in raw_home.lower()):
                        x=json['eventGames'][i]['outcomes'][j]['outcomeOdds']
                        error=0
                        return x
                    elif ' ' in x and 'bramki' not in x:
                        tmp=x.split(' ')[1]
                        tmp2=x.split(' ')[0]
                    elif (x.split(' / ')[0] in raw_home.lower() and x.split(' / ')[1] in raw_home.lower()):# or tmp in raw_home.lower() or tmp2 in raw_home.lower():
                        x = json['eventGames'][i]['outcomes'][j]['outcomeOdds']
                        error = 0
                        return x

                if error==1 and (self.get_current_time()-datetime.timedelta(days=-3))>self.raw_date:
                    ###ODKOMENTOWAC######
                    logging.info("Nie znalazłem zakładu "+str(name)+" "+str(raw_home))
                    pass
            else:
                #
                #return 1.0
                continue


    def remove_pl(self,input_text):
        strange = 'ĄąĆćŚśŻżŹźŁłÓóĘę'

        ascii_replacements = 'AaCcSsZzZzLlOoEe'

        translator = str.maketrans(strange, ascii_replacements)
        return input_text.translate(translator)

    def prepare_dict_to_sql(self):
        self.dict_sql=defaultdict(str)
        for i in events_mapping_iforbet.values():
            if i['name'] not in self.odds.keys():
                self.odds[i['name']]=defaultdict(str)
        self.dict_sql['home']=self.home
        self.dict_sql['away']=self.away
        #print (self.json_var['data'], "1X2", self.home)

        self.dict_sql['iforbet_game_1']=self.get_rate(self.json_var['data'], "1X2", self.raw_home,1)
        self.dict_sql['iforbet_game_0']=self.get_rate(self.json_var['data'], "1X2", "X",1)
        self.dict_sql['iforbet_game_2']=self.get_rate(self.json_var['data'], "1X2", self.raw_away,1)
        self.dict_sql['iforbet_game_10']=self.get_rate(self.json_var['data'], "Podwójna szansa", "1/X",1)
        self.dict_sql['iforbet_game_02']=self.get_rate(self.json_var['data'], "Podwójna szansa", "X/2",1)
        self.dict_sql['iforbet_game_12']=self.get_rate(self.json_var['data'], "Podwójna szansa", "1/2",1)
        #self.dict_sql['data']=self.date.split(' ')[1].split('.')[2]+'-'+self.date.split(' ')[1].split('.')[1]+'-'+self.date.split(' ')[1].split('.')[0]
        #self.dict_sql['Sport']=self.sport
        self.dict_sql['League']=self.league
        self.dict_sql['data']=self.date
        self.dict_sql['hour']=self.hour
        self.dict_sql['iforbet_update_time']=self.update_time
        self.dict_sql['iforbet_o_35'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 3.5 bramek", "Powyżej 3.5 bramki")
        #self.dict_sql['country']=self.
        self.dict_sql['iforbet_dnb_1']=self.get_rate(self.json_var['data'], "Remis - nie ma zakładu (remis=zwrot)", self.raw_home)
        self.dict_sql['iforbet_dnb_2']=self.get_rate(self.json_var['data'], "Remis - nie ma zakładu (remis=zwrot)", self.raw_away)
        self.dict_sql['iforbet_o_05'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 0.5 bramek", "Powyżej 0.5 bramki")
        self.dict_sql['iforbet_u_05'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 0.5 bramek", "Poniżej 0.5 bramki")
        self.dict_sql['iforbet_o_15'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 1.5 bramek", "Powyżej 1.5 bramki")
        self.dict_sql['iforbet_u_15'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 1.5 bramek", "Poniżej 1.5 bramki")
        self.dict_sql['iforbet_o_25'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 2.5 bramek", "Powyżej 2.5 bramki",1)
        self.dict_sql['iforbet_u_25'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 2.5 bramek", "Poniżej 2.5 bramki",1)
        self.dict_sql['iforbet_u_35'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 3.5 bramek", "Poniżej 3.5 bramki")
        self.dict_sql['iforbet_o_35'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 3.5 bramek", "Powyżej 3.5 bramki")
        self.dict_sql['iforbet_o_45'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 4.5 bramek", "Powyżej 4.5 bramki")
        self.dict_sql['iforbet_u_45'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 4.5 bramek", "Poniżej 4.5 bramki")
        self.dict_sql['iforbet_o_55'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 5.5 bramek", "Powyżej 5.5 bramki")
        self.dict_sql['iforbet_u_55'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 5.5 bramek", "Poniżej 5.5 bramki")
        self.dict_sql['iforbet_o_65'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 6.5 bramek", "Powyżej 6.5 bramki")
        self.dict_sql['iforbet_u_65'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 6.5 bramek", "Poniżej 6.5 bramki")
        self.dict_sql['iforbet_o_75'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 7.5 bramek", "Powyżej 7.5 bramki")
        self.dict_sql['iforbet_u_75'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 7.5 bramek", "Poniżej 7.5 bramki")
        self.dict_sql['iforbet_o_85'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 8.5 bramek", "Powyżej 8.5 bramki")
        self.dict_sql['iforbet_u_85'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 8.5 bramek", "Poniżej 8.5 bramki")
        self.dict_sql['iforbet_o_95'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 9.5 bramek", "Powyżej 9.5 bramki")
        self.dict_sql['iforbet_u_95'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 9.5 bramek", "Poniżej 9.5 bramki")
        self.dict_sql['iforbet_ht_ft_11'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", self.raw_home + ' / '+self.raw_home)
        self.dict_sql['iforbet_ht_ft_1x'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", self.raw_home + ' / '+'X')
        print("TO JEST TO:", self.dict_sql['iforbet_ht_ft_1x'], self.raw_home + ' / '+'X')
        self.dict_sql['iforbet_ht_ft_2x'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", self.raw_away + ' / '+'X')
        self.dict_sql['iforbet_ht_ft_21'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", self.raw_away + ' / '+self.raw_home)
        self.dict_sql['iforbet_ht_ft_22'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", self.raw_away + ' / '+self.raw_away)
        self.dict_sql['iforbet_ht_ft_x1'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", 'X' + ' / '+self.raw_home)
        self.dict_sql['iforbet_ht_ft_x2'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", 'X' + ' / '+self.raw_away)
        self.dict_sql['iforbet_ht_ft_12'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", self.raw_home + ' / '+self.raw_away)
        self.dict_sql['iforbet_ht_ft_xx'] = self.get_rate(self.json_var['data'], "Wynik do przerwy/Wynik końcowy", 'X' + ' / '+'X')
        self.dict_sql['iforbet_first_half_1']= self.get_rate(self.json_var['data'], "Wynik 1 połowy", self.raw_home)
        self.dict_sql['iforbet_first_half_x'] = self.get_rate(self.json_var['data'], "Wynik 1 połowy", 'X')
        self.dict_sql['iforbet_first_half_2'] = self.get_rate(self.json_var['data'], "Wynik 1 połowy", self.raw_away)

        self.dict_sql['iforbet_first_half_10'] = self.get_rate(self.json_var['data'], "Podwójna szansa - 1 połowa", self.raw_home+'/X')
        self.dict_sql['iforbet_first_half_02'] = self.get_rate(self.json_var['data'], "Podwójna szansa - 1 połowa", 'X/'+self.raw_away)
        self.dict_sql['iforbet_first_half_12'] = self.get_rate(self.json_var['data'], "Podwójna szansa - 1 połowa", self.raw_home+'/'+self.raw_away)
        #self.dict_sql['iforbet_eh-1_1'] = self.odds['eh-1']['1']
        #self.dict_sql['iforbet_eh-1_x2'] = self.odds['eh-1']['02']
        self.dict_sql['iforbet_u_15_1'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 1.5 bramki", self.raw_home+' i Poniżej 1.5 bramki')
        self.dict_sql['iforbet_o_15_1'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 1.5 bramki", self.raw_home+' i Powyżej 1.5 bramki')
        self.dict_sql['iforbet_u_15_x'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 1.5 bramki", 'X i Poniżej 1.5 bramki')
        self.dict_sql['iforbet_o_15_x'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 1.5 bramki", 'X i Powyżej 1.5 bramki')
        self.dict_sql['iforbet_u_15_2'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 1.5 bramki", self.raw_away+' i Poniżej 1.5 bramki')
        self.dict_sql['iforbet_o_15_2'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 1.5 bramki", self.raw_away+' i Powyżej 1.5 bramki')
        self.dict_sql['iforbet_u_25_1'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 2.5 bramki", self.raw_home+' i Poniżej 2.5 bramki')
        self.dict_sql['iforbet_o_25_1'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 2.5 bramki", self.raw_home+' i Powyżej 2.5 bramki')
        self.dict_sql['iforbet_u_25_x'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 2.5 bramki", 'X i Poniżej 2.5 bramki')
        self.dict_sql['iforbet_o_25_x'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 2.5 bramki", 'X i Powyżej 2.5 bramki')
        self.dict_sql['iforbet_u_25_2'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 2.5 bramki", self.raw_away+' i Poniżej 2.5 bramki')
        self.dict_sql['iforbet_o_25_2'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 2.5 bramki", self.raw_away+' i Powyżej 2.5 bramki')
        self.dict_sql['iforbet_u_35_1'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 3.5 bramki", self.raw_home+' i Poniżej 3.5 bramki')
        self.dict_sql['iforbet_o_35_1'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 3.5 bramki", self.raw_home+' i Powyżej 3.5 bramki')
        self.dict_sql['iforbet_u_35_x'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 3.5 bramki", 'X i Poniżej 3.5 bramki')
        self.dict_sql['iforbet_o_35_x'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 3.5 bramki", 'X i Poniżej 3.5 bramki')
        self.dict_sql['iforbet_u_35_2'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 3.5 bramki", self.raw_away+' i Powyżej 3.5 bramki')
        self.dict_sql['iforbet_o_35_2'] = self.get_rate(self.json_var['data'], "Wynik końcowy i Poniżej/Powyżej 3.5 bramki", self.raw_away+' i Powyżej 3.5 bramki')
        self.dict_sql['iforbet_btts_1'] = self.get_rate(self.json_var['data'], "Wynik końcowy i obie drużyny strzelą", self.raw_home+' i Tak')
        self.dict_sql['iforbet_btts_2'] = self.get_rate(self.json_var['data'], "Wynik końcowy i obie drużyny strzelą", self.raw_away+' i Tak')
        self.dict_sql['iforbet_btts_x'] = self.get_rate(self.json_var['data'], "Wynik końcowy i obie drużyny strzelą", 'X i Tak')
        self.dict_sql['iforbet_btts_no_1'] = self.get_rate(self.json_var['data'], "Wynik końcowy i obie drużyny strzelą", self.raw_home+' i Nie')
        self.dict_sql['iforbet_btts_no_2'] = self.get_rate(self.json_var['data'], "Wynik końcowy i obie drużyny strzelą", self.raw_away+' i Nie')
        self.dict_sql['iforbet_btts_no_x'] = self.get_rate(self.json_var['data'], "Wynik końcowy i obie drużyny strzelą", 'X i Nie')
        self.dict_sql['iforbet_eh_min_1_1'] = self.get_rate(self.json_var['data'], "Handicap 0:1", self.remove_pl(self.raw_home))
        self.dict_sql['iforbet_eh_min_1_x'] = self.get_rate(self.json_var['data'], "Handicap 0:1", 'X')
        self.dict_sql['iforbet_eh_min_1_2'] = self.get_rate(self.json_var['data'], "Handicap 0:1", self.remove_pl(self.raw_away))
        self.dict_sql['iforbet_eh_plus_1_1'] = self.get_rate(self.json_var['data'], "Handicap 1:0", self.remove_pl(self.raw_home))
        self.dict_sql['iforbet_eh_plus_1_x'] = self.get_rate(self.json_var['data'], "Handicap 1:0", 'X')
        self.dict_sql['iforbet_eh_plus_1_2'] = self.get_rate(self.json_var['data'], "Handicap 1:0", self.remove_pl(self.raw_away))
        self.dict_sql['iforbet_btts_yes'] = self.get_rate(self.json_var['data'], "Obie drużyny strzelą bramkę", 'Tak')
        self.dict_sql['iforbet_btts_no'] = self.get_rate(self.json_var['data'], "Obie drużyny strzelą bramkę", 'Nie')
        self.dict_sql['iforbet_corners_o_65']=self.get_rate(self.json_var['data'], "Poniżej/Powyżej 6.5 rzutów rożnych", 'Powyżej 6.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_65'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 6.5 rzutów rożnych", 'Poniżej 6.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_75'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 7.5 rzutów rożnych", 'Powyżej 7.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_75'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 7.5 rzutów rożnych", 'Poniżej 7.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_85'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 8.5 rzutów rożnych", 'Powyżej 8.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_85'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 8.5 rzutów rożnych", 'Poniżej 8.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_95'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 9.5 rzutów rożnych", 'Powyżej 9.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_95'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 9.5 rzutów rożnych", 'Poniżej 9.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_105'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 10.5 rzutów rożnych", 'Powyżej 10.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_105'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 10.5 rzutów rożnych", 'Poniżej 10.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_115'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 11.5 rzutów rożnych", 'Powyżej 11.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_115'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 11.5 rzutów rożnych", 'Poniżej 11.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_125'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 12.5 rzutów rożnych", 'Powyżej 12.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_125'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 12.5 rzutów rożnych", 'Poniżej 12.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_135'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 13.5 rzutów rożnych", 'Powyżej 13.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_135'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 13.5 rzutów rożnych", 'Poniżej 13.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_145'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 14.5 rzutów rożnych", 'Powyżej 14.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_145'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 14.5 rzutów rożnych", 'Poniżej 14.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_155'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 15.5 rzutów rożnych", 'Powyżej 15.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_155'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 15.5 rzutów rożnych", 'Poniżej 15.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_165'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 16.5 rzutów rożnych", 'Powyżej 16.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_165'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 16.5 rzutów rożnych", 'Poniżej 16.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_o_175'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 17.5 rzutów rożnych", 'Powyżej 17.5 rzutów rożnych')
        self.dict_sql['iforbet_corners_u_175'] = self.get_rate(self.json_var['data'], "Poniżej/Powyżej 17.5 rzutów rożnych", 'Poniżej 17.5 rzutów rożnych')
        #self.dict_sql['iforbet_1_st_goal_1'] = self.odds['1st_goal'][sehome]
        #self.dict_sql['iforbet_1_st_goal_2'] = self.odds['1st_goal'][away]
        #self.dict_sql['iforbet_1_st_goal_0'] = self.odds['1st_goal']['nikt']

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
        table="'db_bets'"
        table2='db_bets'
        columns_string = '("' + '","'.join(meczyk.dict_sql.keys()) + '")'
        values_string = '("' + '","'.join(map(str, meczyk.dict_sql.values())) + '")'
        sql_update_command= 'UPDATE ' + str(table) + " SET "
        print ("SQL UPDATE")
        for k,v in meczyk.dict_sql.items():
            sql_update_command = sql_update_command + '"'+str(k) + '"="' + str(v)+'",'
        #print (sql_update_command)
        sql_update_cmd=sql_update_command[:-1] + " WHERE home=" + str(home) + "and away = "+ str(away) + " and data = "+str(date)
        sql = """INSERT INTO %s %s
             VALUES %s""" % (table, columns_string, values_string)
        sql_insert = """INSERT INTO %s %s
                     VALUES %s""" % (table, columns_string, values_string)
        print (sql_update_cmd)

        polecenie="SELECT * FROM "+str(table2)+ " WHERE home="+str(home) +" and away=" + str(away) +" and data="+str(date)
        print(polecenie)
        cur = db.cursor()
        try:
            x=cur.execute(polecenie).fetchone()
        except Exception as e: print(e)


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

    def __init__(self, events_mapping_fortuna,url):
        #self.__events_mapping=events_mapping_fortuna
        self.data=url
        self.get_name()
        self.get_odds2()

        self.prepare_dict_to_sql()

        save_to_db_common(self,"'"+str(self.date)+"'")
        #print (self.dict_sql)
        #print ("ODDS:",self.odds)
#data = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/470334',None,headers)).read() # The data u need
#meczyk=football_event(events_mapping_fortuna)
#exit()


#url='https://www.iforbet.pl/oferta/8/4437,4569,199,511,168,2432,321,159,269,223,147,122,273,660,2902,558,641,289'
url='https://www.iforbet.pl/oferta/8/321,159,269,223,147,122,273,660,2902,558,641,289,2432'
url='https://m.iforbet.pl/rest/market/categories/multi/321,159,269,223,147,122,123,273,660,2902,558,641,289,2432,4437,357,555,282,434,511,199/events'
#url='https://m.iforbet.pl/rest/market/categories/multi/4437/events'
#url='https://www.iforbet.pl/oferta/8/293,380,398,3372,357,7018,555,3096,120,666,123'
#url='https://www.iforbet.pl/oferta/8/908,2911'
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent,}
def get_links(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(request)
    data = response.read().decode('utf-8')
    soup = BeautifulSoup(data, "html.parser")
    json_var = json.loads(data)
    linki=[]
    for i in range(0,len(json_var['data'])):
        linki.append(json_var['data'][i]['eventId'])

    print(linki)

    return linki



#get_links(url)
    #data = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers)).read() # The data u need
#site = 'https://www.iforbet.pl/zdarzenie/545630'
#request = urllib2.Request(site, None, headers)
#response = urllib2.urlopen(request)
#data = response.read()  # The data u need


#meczyk.prepare_dict_to_sql()
##meczyk.save_to_db()
#print (get_links(url))

#exit()
x='https://m.iforbet.pl/rest/market/events/4738877'
sites2=[4738877]
for sites in get_links(url):
#for sites in sites2:
    try:
        site = 'https://m.iforbet.pl/rest/market/events/'+str(sites)
        print ("SITE",site)
        request = urllib2.Request(site, None, headers)
        response = urllib2.urlopen(request)
        #print (request)
        data = response.read()
        data = urllib2.urlopen(urllib2.Request(site, None, headers)).read().decode('utf-8')
        #print ("DATA:",data)
        try:
            meczyk = football_event(events_mapping_fortuna,data)
        except:
            logging.warning("ERROR dla: " + 'https://m.iforbet.pl/rest/market/events/' + str(sites))
            continue
    except:
        logging.warning("ERROR dla: " + 'https://m.iforbet.pl/rest/market/events/'+str(sites))
        continue


