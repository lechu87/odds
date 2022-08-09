#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import ALL_COMPLETED
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
import common
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
        self.raw_home=self.json_data['eventName'].split(' - ')[0]
        self.raw_home_part=self.raw_home.split(' ')[0]
        self.raw_away = self.json_data['eventName'].split(' - ')[1]
        self.raw_away_part = self.raw_away.split(' ')[0]
        self.home=unify_name(self.json_data['eventName'].split(' - ')[0],teams,logging)
        self.away=unify_name(self.json_data['eventName'].split(' - ')[1],teams,logging)

        self.league=unify_name(self.json_data['category3Name']+' '+self.json_data['category2Name'],leagues,logging)
        print ("LEAGUE:",self.json_data['category3Name']+' '+self.json_data['category2Name'],self.league)
        print (self.home,self.away)
        for name in [self.home,self.away]:
            if name==None:
                logging.warning("Nazwa nie znaleziona"+str(self.home)+'-'+str(self.away))
                exit

        raw_date=self.json_data['eventStart']

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

    def get_rate(self,json,name,raw_home,log=0):
        found=False
        for i in range(0,len(json['eventGames'])):
            if json['eventGames'][i]['gameName'].lower() == name.lower():
                for j in range(0, len(json['eventGames'][i]['outcomes'])):
                    x=json['eventGames'][i]['outcomes'][j]['outcomeName'].lower()
                    if x==raw_home.lower():
                        odd=json['eventGames'][i]['outcomes'][j]['outcomeOdds']
                        found=True
                        return odd
        if found==False and (self.get_current_time()-datetime.timedelta(days=-5))>self.raw_date:
            print ("Nie znalazłem:",name,raw_home)

    def get_rate_old(self,json, name, raw_home,log=0):
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
        self.odds=defaultdict(str)
        self.dict_sql=defaultdict(str)
        self.dict_sql['bet']="iforbet"
        for i in events_mapping_iforbet.values():
            if i['name'] not in self.odds.keys():
                self.odds[i['name']]=defaultdict(str)
        self.dict_sql['home']=self.home
        self.dict_sql['away']=self.away
        #print (self.json_var['data'], "1X2", self.home)

        self.dict_sql['game_1']=self.get_rate(self.json_var, "1X2", self.raw_home,1)
        self.dict_sql['game_0']=self.get_rate(self.json_var, "1X2", "X",1)
        self.dict_sql['game_2']=self.get_rate(self.json_var, "1X2", self.raw_away,1)
        self.dict_sql['game_10']=self.get_rate(self.json_var, "Podwójna szansa", "1/X",1)
        self.dict_sql['game_02']=self.get_rate(self.json_var, "Podwójna szansa", "X/2",1)
        self.dict_sql['game_12']=self.get_rate(self.json_var, "Podwójna szansa", "1/2",1)
        #self.dict_sql['data']=self.date.split(' ')[1].split('.')[2]+'-'+self.date.split(' ')[1].split('.')[1]+'-'+self.date.split(' ')[1].split('.')[0]
        #self.dict_sql['Sport']=self.sport
        self.dict_sql['League']=self.league
        self.dict_sql['data']=self.date
        self.dict_sql['hour']=self.hour
        self.dict_sql['update_time']=self.update_time
        self.dict_sql['o_35'] = self.get_rate(self.json_var, "poniżej/powyżej 3.5 bramek", "Powyżej 3.5 bramek")
        #self.dict_sql['country']=self.
        self.dict_sql['dnb_1']=self.get_rate(self.json_var, "Remis - nie ma zakładu (remis=zwrot)", self.raw_home)
        self.dict_sql['dnb_2']=self.get_rate(self.json_var, "Remis - nie ma zakładu (remis=zwrot)", self.raw_away)
        self.dict_sql['o_05'] = self.get_rate(self.json_var, "poniżej/powyżej 0.5 bramek", "Powyżej 0.5 bramek")
        self.dict_sql['u_05'] = self.get_rate(self.json_var, "poniżej/powyżej 0.5 bramek", "Poniżej 0.5 bramek")
        self.dict_sql['o_15'] = self.get_rate(self.json_var, "poniżej/powyżej 1.5 bramek", "Powyżej 1.5 bramek")
        self.dict_sql['u_15'] = self.get_rate(self.json_var, "poniżej/powyżej 1.5 bramek", "Poniżej 1.5 bramek")
        self.dict_sql['o_25'] = self.get_rate(self.json_var, "poniżej/powyżej 2.5 bramek", "Powyżej 2.5 bramek",1)
        self.dict_sql['u_25'] = self.get_rate(self.json_var, "poniżej/powyżej 2.5 bramek", "Poniżej 2.5 bramek",1)
        self.dict_sql['u_35'] = self.get_rate(self.json_var, "poniżej/powyżej 3.5 bramek", "Poniżej 3.5 bramek")
        self.dict_sql['o_35'] = self.get_rate(self.json_var, "poniżej/powyżej 3.5 bramek", "Powyżej 3.5 bramek")
        self.dict_sql['o_45'] = self.get_rate(self.json_var, "poniżej/powyżej 4.5 bramek", "Powyżej 4.5 bramek")
        self.dict_sql['u_45'] = self.get_rate(self.json_var, "poniżej/powyżej 4.5 bramek", "Poniżej 4.5 bramek")
        self.dict_sql['o_55'] = self.get_rate(self.json_var, "poniżej/powyżej 5.5 bramek", "Powyżej 5.5 bramek")
        self.dict_sql['u_55'] = self.get_rate(self.json_var, "poniżej/powyżej 5.5 bramek", "Poniżej 5.5 bramek")
        self.dict_sql['o_65'] = self.get_rate(self.json_var, "poniżej/powyżej 6.5 bramek", "Powyżej 6.5 bramek")
        self.dict_sql['u_65'] = self.get_rate(self.json_var, "poniżej/powyżej 6.5 bramek", "Poniżej 6.5 bramek")
        self.dict_sql['o_75'] = self.get_rate(self.json_var, "poniżej/powyżej 7.5 bramek", "Powyżej 7.5 bramek")
        self.dict_sql['u_75'] = self.get_rate(self.json_var, "poniżej/powyżej 7.5 bramek", "Poniżej 7.5 bramek")
        self.dict_sql['o_85'] = self.get_rate(self.json_var, "poniżej/powyżej 8.5 bramek", "Powyżej 8.5 bramek")
        self.dict_sql['u_85'] = self.get_rate(self.json_var, "poniżej/powyżej 8.5 bramek", "Poniżej 8.5 bramek")
        self.dict_sql['o_95'] = self.get_rate(self.json_var, "poniżej/powyżej 9.5 bramek", "Powyżej 9.5 bramek")
        self.dict_sql['u_95'] = self.get_rate(self.json_var, "poniżej/powyżej 9.5 bramek", "Poniżej 9.5 bramek")
        self.dict_sql['ht_ft_11'] = self.get_rate(self.json_var, "1. połowa/mecz", self.raw_home + ' / '+self.raw_home)
        self.dict_sql['ht_ft_1x'] = self.get_rate(self.json_var, "1. połowa/mecz", self.raw_home + ' / '+'X')
        print("TO JEST TO:", self.dict_sql['ht_ft_1x'], self.raw_home + ' / '+'X')
        self.dict_sql['ht_ft_2x'] = self.get_rate(self.json_var, "1. połowa/mecz", self.raw_away + ' / '+'X')
        self.dict_sql['ht_ft_21'] = self.get_rate(self.json_var, "1. połowa/mecz", self.raw_away + ' / '+self.raw_home)
        self.dict_sql['ht_ft_22'] = self.get_rate(self.json_var, "1. połowa/mecz", self.raw_away + ' / '+self.raw_away)
        self.dict_sql['ht_ft_x1'] = self.get_rate(self.json_var, "1. połowa/mecz", 'X' + ' / '+self.raw_home)
        self.dict_sql['ht_ft_x2'] = self.get_rate(self.json_var, "1. połowa/mecz", 'X' + ' / '+self.raw_away)
        self.dict_sql['ht_ft_12'] = self.get_rate(self.json_var, "1. połowa/mecz", self.raw_home + ' / '+self.raw_away)
        self.dict_sql['ht_ft_xx'] = self.get_rate(self.json_var, "1. połowa/mecz", 'X' + ' / '+'X')
        self.dict_sql['first_half_1']= self.get_rate(self.json_var, "1. połowa - 1X2", self.raw_home)
        self.dict_sql['first_half_x'] = self.get_rate(self.json_var, "1. połowa - 1X2", 'X')
        self.dict_sql['first_half_2'] = self.get_rate(self.json_var, "1. połowa - 1X2", self.raw_away)

        self.dict_sql['first_half_10'] = self.get_rate(self.json_var, "1. połowa - podwójna szansa", self.raw_home+'/X')
        self.dict_sql['first_half_02'] = self.get_rate(self.json_var, "1. połowa - podwójna szansa", 'X/'+self.raw_away)
        self.dict_sql['first_half_12'] = self.get_rate(self.json_var, "1. połowa - podwójna szansa", self.raw_home+'/'+self.raw_away)
        #self.dict_sql['eh-1_1'] = self.odds['eh-1']['1']
        #self.dict_sql['eh-1_x2'] = self.odds['eh-1']['02']
        self.dict_sql['u_15_1'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 1.5 goli", self.raw_home+' i Poniżej 1.5 bramki')
        self.dict_sql['o_15_1'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 1.5 goli", self.raw_home+' i Powyżej 1.5 bramki')
        self.dict_sql['u_15_x'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 1.5 goli", 'X i Poniżej 1.5 bramki')
        self.dict_sql['o_15_x'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 1.5 goli", 'X i Powyżej 1.5 bramki')
        self.dict_sql['u_15_2'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 1.5 goli", self.raw_away+' i Poniżej 1.5 bramki')
        self.dict_sql['o_15_2'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 1.5 goli", self.raw_away+' i Powyżej 1.5 bramki')
        self.dict_sql['u_25_1'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 2.5 goli", self.raw_home+' i Poniżej 2.5 bramki')
        self.dict_sql['o_25_1'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 2.5 goli", self.raw_home+' i Powyżej 2.5 bramki')
        self.dict_sql['u_25_x'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 2.5 goli", 'X i Poniżej 2.5 bramki')
        self.dict_sql['o_25_x'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 2.5 goli", 'X i Powyżej 2.5 bramki')
        self.dict_sql['u_25_2'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 2.5 goli", self.raw_away+' i Poniżej 2.5 bramki')
        self.dict_sql['o_25_2'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 2.5 goli", self.raw_away+' i Powyżej 2.5 bramki')
        self.dict_sql['u_35_1'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 3.5 goli", self.raw_home+' i Poniżej 3.5 bramki')
        self.dict_sql['o_35_1'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 3.5 goli", self.raw_home+' i Powyżej 3.5 bramki')
        self.dict_sql['u_35_x'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 3.5 goli", 'X i Poniżej 3.5 bramki')
        self.dict_sql['o_35_x'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 3.5 goli", 'X i Poniżej 3.5 bramki')
        self.dict_sql['u_35_2'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 3.5 goli", self.raw_away+' i Powyżej 3.5 bramki')
        self.dict_sql['o_35_2'] = self.get_rate(self.json_var, "1X2 i poniżej/powyżej 3.5 goli", self.raw_away+' i Powyżej 3.5 bramki')
        self.dict_sql['btts_1'] = self.get_rate(self.json_var, "1X2 i obie drużyny strzelą", self.raw_home+' i Tak')
        self.dict_sql['btts_2'] = self.get_rate(self.json_var, "1X2 i obie drużyny strzelą", self.raw_away+' i Tak')
        self.dict_sql['btts_x'] = self.get_rate(self.json_var, "1X2 i obie drużyny strzelą", 'X i Tak')
        self.dict_sql['btts_no_1'] = self.get_rate(self.json_var, "1X2 i obie drużyny strzelą", self.raw_home+' i Nie')
        self.dict_sql['btts_no_2'] = self.get_rate(self.json_var, "1X2 i obie drużyny strzelą", self.raw_away+' i Nie')
        self.dict_sql['btts_no_x'] = self.get_rate(self.json_var, "1X2 i obie drużyny strzelą", 'X i Nie')
        self.dict_sql['eh_min_1_1'] = self.get_rate(self.json_var, "Handicap 0:1", self.remove_pl(self.raw_home)+ " (0:1)")
        self.dict_sql['eh_min_1_x'] = self.get_rate(self.json_var, "Handicap 0:1", 'X'+ " (0:1)")
        self.dict_sql['eh_min_1_2'] = self.get_rate(self.json_var, "Handicap 0:1", self.remove_pl(self.raw_away)+ " (0:1)")
        self.dict_sql['eh_plus_1_1'] = self.get_rate(self.json_var, "Handicap 1:0", self.remove_pl(self.raw_home)+ " (1:0)")
        self.dict_sql['eh_plus_1_x'] = self.get_rate(self.json_var, "Handicap 1:0", 'X'+ " (1:0)")
        self.dict_sql['eh_plus_1_2'] = self.get_rate(self.json_var, "Handicap 1:0", self.remove_pl(self.raw_away)+ " (1:0)")
        self.dict_sql['btts_yes'] = self.get_rate(self.json_var, "Obie drużyny strzelą bramkę", 'Tak')
        self.dict_sql['btts_no'] = self.get_rate(self.json_var, "Obie drużyny strzelą bramkę", 'Nie')
        self.dict_sql['corners_o_65']=self.get_rate(self.json_var, "poniżej/powyżej 6.5 rzutów rożnych", 'Powyżej 6.5 rzutów rożnych')
        self.dict_sql['corners_u_65'] = self.get_rate(self.json_var, "poniżej/powyżej 6.5 rzutów rożnych", 'Poniżej 6.5 rzutów rożnych')
        self.dict_sql['corners_o_75'] = self.get_rate(self.json_var, "poniżej/powyżej 7.5 rzutów rożnych", 'Powyżej 7.5 rzutów rożnych')
        self.dict_sql['corners_u_75'] = self.get_rate(self.json_var, "poniżej/powyżej 7.5 rzutów rożnych", 'Poniżej 7.5 rzutów rożnych')
        self.dict_sql['corners_o_85'] = self.get_rate(self.json_var, "poniżej/powyżej 8.5 rzutów rożnych", 'Powyżej 8.5 rzutów rożnych')
        self.dict_sql['corners_u_85'] = self.get_rate(self.json_var, "poniżej/powyżej 8.5 rzutów rożnych", 'Poniżej 8.5 rzutów rożnych')
        self.dict_sql['corners_o_95'] = self.get_rate(self.json_var, "poniżej/powyżej 9.5 rzutów rożnych", 'Powyżej 9.5 rzutów rożnych')
        self.dict_sql['corners_u_95'] = self.get_rate(self.json_var, "poniżej/powyżej 9.5 rzutów rożnych", 'Poniżej 9.5 rzutów rożnych')
        self.dict_sql['corners_o_105'] = self.get_rate(self.json_var, "poniżej/powyżej 10.5 rzutów rożnych", 'Powyżej 10.5 rzutów rożnych')
        self.dict_sql['corners_u_105'] = self.get_rate(self.json_var, "poniżej/powyżej 10.5 rzutów rożnych", 'Poniżej 10.5 rzutów rożnych')
        self.dict_sql['corners_o_115'] = self.get_rate(self.json_var, "poniżej/powyżej 11.5 rzutów rożnych", 'Powyżej 11.5 rzutów rożnych')
        self.dict_sql['corners_u_115'] = self.get_rate(self.json_var, "poniżej/powyżej 11.5 rzutów rożnych", 'Poniżej 11.5 rzutów rożnych')
        self.dict_sql['corners_o_125'] = self.get_rate(self.json_var, "poniżej/powyżej 12.5 rzutów rożnych", 'Powyżej 12.5 rzutów rożnych')
        self.dict_sql['corners_u_125'] = self.get_rate(self.json_var, "poniżej/powyżej 12.5 rzutów rożnych", 'Poniżej 12.5 rzutów rożnych')
        self.dict_sql['corners_o_135'] = self.get_rate(self.json_var, "poniżej/powyżej 13.5 rzutów rożnych", 'Powyżej 13.5 rzutów rożnych')
        self.dict_sql['corners_u_135'] = self.get_rate(self.json_var, "poniżej/powyżej 13.5 rzutów rożnych", 'Poniżej 13.5 rzutów rożnych')
        self.dict_sql['corners_o_145'] = self.get_rate(self.json_var, "poniżej/powyżej 14.5 rzutów rożnych", 'Powyżej 14.5 rzutów rożnych')
        self.dict_sql['corners_u_145'] = self.get_rate(self.json_var, "poniżej/powyżej 14.5 rzutów rożnych", 'Poniżej 14.5 rzutów rożnych')
        self.dict_sql['corners_o_155'] = self.get_rate(self.json_var, "poniżej/powyżej 15.5 rzutów rożnych", 'Powyżej 15.5 rzutów rożnych')
        self.dict_sql['corners_u_155'] = self.get_rate(self.json_var, "poniżej/powyżej 15.5 rzutów rożnych", 'Poniżej 15.5 rzutów rożnych')
        self.dict_sql['corners_o_165'] = self.get_rate(self.json_var, "poniżej/powyżej 16.5 rzutów rożnych", 'Powyżej 16.5 rzutów rożnych')
        self.dict_sql['corners_u_165'] = self.get_rate(self.json_var, "poniżej/powyżej 16.5 rzutów rożnych", 'Poniżej 16.5 rzutów rożnych')
        self.dict_sql['corners_o_175'] = self.get_rate(self.json_var, "poniżej/powyżej 17.5 rzutów rożnych", 'Powyżej 17.5 rzutów rożnych')
        self.dict_sql['corners_u_175'] = self.get_rate(self.json_var, "poniżej/powyżej 17.5 rzutów rożnych", 'Poniżej 17.5 rzutów rożnych')
        #self.dict_sql['1_st_goal_1'] = self.odds['1st_goal'][sehome]
        #self.dict_sql['1_st_goal_2'] = self.odds['1st_goal'][away]
        #self.dict_sql['1_st_goal_0'] = self.odds['1st_goal']['nikt']

        return self.dict_sql
    def save_to_db(meczyk):
        database_name = 'odds_new.sqlite'
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
        #print ("SQL UPDATE")
        for k,v in meczyk.dict_sql.items():
            sql_update_command = sql_update_command + '"'+str(k) + '"="' + str(v)+'",'
        #print (sql_update_command)
        sql_update_cmd=sql_update_command[:-1] + " WHERE bet=\"iforbet\" and home=" + "\""+str(home) +"\""+ " and away = "+ "\""+str(away) +"\""+ " and data = "+"\""+str(date)+"\""
        sql = """INSERT INTO %s %s
             VALUES %s""" % (table, columns_string, values_string)
        sql_insert = """INSERT INTO %s %s
                     VALUES %s""" % (table, columns_string, values_string)
        #print (sql_update_cmd)

        polecenie="SELECT * FROM "+str(table2)+ " WHERE bet=\"iforbet\" and home="+"\""+str(home) +"\""+" and away=" +"\""+ str(away) +"\""+" and data=\""+str(date)+"\""
        #print(polecenie)
        cur = db.cursor()
        try:
            x=cur.execute(polecenie).fetchone()
            #print (x)
        except Exception as e: 
            print(e)
            x=None


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

    def __init__(self, events_mapping_fortuna,json_data):
        self.json_data=json_data
        self.json_var=self.json_data
        self.get_name()
        self.prepare_dict_to_sql()
        #for k,v in self.dict_sql.items():
        #    if v!=None:
        #        print (k,v)
        self.save_to_db()
        #print ("ODDS:",self.odds)

#json=get_json('https://www.iforbet.pl/rest/market/categories')

def get_links(url):
    json_var = common.get_json(url)['data']
    linki=[]
    for i in range(0,len(json_var)):
        linki.append(json_var[i]['eventId'])
    logging.debug("LINKI:,{}".format(' '.join(map(str, linki))))
    return linki




league_url="https://www.iforbet.pl/rest/market/categories/multi/"
leagues_iforbet=[29861]
leagues_iforbet=[159,122,199,29861,555,29994,29973,29970,29914,29928,29968,29975,29858,29958,29922,29996,3055,29953,29972,29927]
#leagues_iforbet=[29972]
all_links=[]
for league in leagues_iforbet:
    logging.debug("LINKKKKKKK:"+league_url+str(league)+'/events')
    links=get_links(league_url+str(league)+'/events')
    print (links)
    all_links.extend(links)

#get_links("https://www.iforbet.pl/rest/market/categories/multi/29861/events?gamesClass=major")

#TO bedzie w petli:
i=0
for game in all_links:
    game_json=common.get_json("https://www.iforbet.pl/rest/market/events/"+str(game))
    print ("https://www.iforbet.pl/rest/market/events/"+str(game))
    #print (game_json)
    meczyk = football_event(events_mapping_fortuna,game_json['data'])
    i=i+1
print ("Tyle meczy do wrzucenia:",len(all_links))
print ("Tyle meczy wrzucone:",i)

