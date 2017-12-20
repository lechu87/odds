from bs4 import BeautifulSoup
import urllib.request as urllib2
import sqlite3
import codecs
import logging
import re
import datetime
from collections import defaultdict
from dictionaries import *
from selenium import webdriver
import time

#driver = webdriver.Chrome()
#driver.get('https://lvbet.pl/pl/zaklady-bukmacherskie/5/448/669/1797570')
#time.sleep(5)
#data = driver.page_source
#print (htmlSource)
#exit()
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
#url = "http://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers"
headers={'User-Agent':user_agent,}
data=urllib2.urlopen(urllib2.Request('https://old.lvbet.pl/sports/zaklady/zaklady-przedmeczowe/5/119/917/',None,headers))
#response = urllib2.urlopen(urllib2.Request('https://www.iforbet.pl/zdarzenie/450168',None,headers))
#data = urllib2.urlopen(urllib2.Request('https://lvbet.pl/pl/zaklady-bukmacherskie/5/448/669/1797564',None,headers)).read() # The data u need
#data=codecs.open('fortuna.html',mode='r',encoding='utf-8').read()
#data=urllib2.urlopen('https://old.lvbet.pl/sports/zaklady/zaklady-przedmeczowe/5/119/917/').read()
#data=codecs.open('lvbet_examplr.html',mode='r',encoding='utf-8').read()
soup = BeautifulSoup(data, "html.parser")
game=soup.find('h1',{'class':'bet_table_title'})
print (soup)
exit()
class football_event:
    soup = BeautifulSoup(data,"html.parser")
    logging.basicConfig(filename='logfile_lvbet.log', level=logging.DEBUG)
    def get_events_mapping(self):
        return self.__events_mapping
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
    def get_name(self):
        soup = BeautifulSoup(data, "html.parser")
        #self.game=soup.find('h1',{'class':'bet_table_title'})
        self.game = soup.find('div',{'class':'scoreboard-mini'}).text
        self.home_raw=self.game.split('VS')[0].strip()
        self.away_raw=self.game.split('VS')[1].strip()
        self.home = unify_name(self.game.split('VS')[0].strip(),teams,logging)
        self.away = unify_name(self.game.split('VS')[1].strip(),teams,logging)
        self.league_raw = unify_name(soup.find_all('span',{'class':'additional'})[-3].text+' '+soup.find_all('span',{'class':'additional'})[-1].text,leagues,logging)
        #for el in self.league_raw:
        #    print (el.text)
        current_time=datetime.datetime.now()
        self.update_time=str('{:04d}'.format(current_time.year))+'-'+str('{:02d}'.format(current_time.month))+'-'+str('{:02d}'.format(current_time.day))+\
        '-' + str('{:02d}'.format(current_time.hour))+'-'+str('{:02d}'.format(current_time.minute))+'-'+str('{:02d}'.format(current_time.second))
        print (self.league_raw)
        print (self.home)
        print(self.away)
        #print (self.date)
    def get_odds(self):
        soup = BeautifulSoup(data, "html.parser")
        self.odds = defaultdict(str)
        rows=soup.find_all('div',{'class':'row lv-table-entry live-view'})
        #print ("ROW1",rows[0])
        #z=rows[0].find('div',{'class':'row'})
        #print(z)
        for row in rows:
            #print (row)
            name=row.find('div',{'class':'col-d-4 col-t-12 teams live-event'}).text.strip()
            #odd_tittle=odd_t.text
            if name not in self.__events_mapping.keys():
                logging.warning(self.home + ' ' + self.away)
                logging.warning("Nieznany zaklad: " + name)
                continue
            if self.__events_mapping[name]["name"] not in self.odds.keys():
                self.odds[self.__events_mapping[name]["name"]] = defaultdict(str)
            odds_name=row.find_all('span',{'class':'player-name'})
            odds_stake=row.find_all('span',{'class':'player-odds'})
            i=0
            for odd_name in odds_name:
                print ("ODD_NAME",odd_name)
                corr_name=self.extract_team_name(odd_name.text.strip(),self.home_raw,self.away_raw)
                corr_stake=self.extract_team_name(odds_stake[i].text.strip(),self.home_raw,self.away_raw)
                self.odds[self.__events_mapping[name]["name"]][corr_name]=corr_stake
                i=i+1
        print ('ODDS:',self.odds)
        #tables = soup.find_all('table', {'class': 'bet_table last_table'})

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
        self.dict_sql['_0']=self.odds['game']['Remis']
        self.dict_sql['_2']=self.odds['game']['2']
        self.dict_sql['_10']=self.odds['dc']['Drużyna 1 lub remis']
        self.dict_sql['_02']=self.odds['dc']['Drużyna 2 lub remis']
        self.dict_sql['_12']=self.odds['dc']['Drużyna 1 lub Drużyna 2']
        #self.dict_sql['data']=self.date.split(' ')[1].split('.')[2]+'-'+self.date.split(' ')[1].split('.')[1]+'-'+self.date.split(' ')[1].split('.')[0]
        #self.dict_sql['Sport']=self.sport
        #self.dict_sql['League']=self.league
        #self.dict_sql['data']=self.date
        #self.dict_sql['hour']=self.hour
        self.dict_sql['update_time']=self.update_time
        self.dict_sql['o_35'] = self.odds['goals']['Powyżej (3.5)']
        #self.dict_sql['country']=self.
        self.dict_sql['dnb_1']=self.odds['dnb']['Drużyna 1']
        self.dict_sql['dnb_2']=self.odds['dnb']['Drużyna 2']
        self.dict_sql['o_05'] = self.odds['goals']['Powyżej (0.5)']
        self.dict_sql['u_05'] = self.odds['goals']['Poniżej (0.5)']
        self.dict_sql['o_15'] = self.odds['goals']['Powyżej (1.5)']
        self.dict_sql['u_15'] = self.odds['goals']['Poniżej (1.5)']
        self.dict_sql['o_25'] = self.odds['goals']['Powyżej (2.5)']
        self.dict_sql['u_25'] = self.odds['goals']['Poniżej (2.5)']
        self.dict_sql['u_35'] = self.odds['goals']['Poniżej (3.5)']
        self.dict_sql['o_45'] = self.odds['goals']['Powyżej (4.5)']
        self.dict_sql['u_45'] = self.odds['goals']['Poniżej (4.5)']
        self.dict_sql['o_55'] = self.odds['goals']['Powyżej (5.5)']
        self.dict_sql['u_55'] = self.odds['goals']['Poniżej (5.5)']
        self.dict_sql['o_65'] = self.odds['goals']['Powyżej (6.5)']
        self.dict_sql['u_65'] = self.odds['goals']['Poniżej (6.5)']
        self.dict_sql['o_75'] = self.odds['goals']['Powyżej (7.5)']
        self.dict_sql['u_75'] = self.odds['goals']['Poniżej (7.5)']
        self.dict_sql['o_85'] = self.odds['goals']['Powyżej (8.5)']
        self.dict_sql['u_85'] = self.odds['goals']['Poniżej (8.5)']
        self.dict_sql['o_95'] = self.odds['goals']['Powyżej (9.5)']
        self.dict_sql['u_95'] = self.odds['goals']['Poniżej (9.5)']
        self.dict_sql['ht_ft_11'] = self.odds['half/game'][ '1/1']
        self.dict_sql['ht_ft_1x'] = self.odds['half/game'][ '1/Remis']
        self.dict_sql['ht_ft_2x'] = self.odds['half/game'][ '2/Remis']
        self.dict_sql['ht_ft_21'] = self.odds['half/game'][ '2/1']
        self.dict_sql['ht_ft_22'] = self.odds['half/game'][ '2/2']
        self.dict_sql['ht_ft_x1'] = self.odds['half/game'][ 'Remis/1']
        self.dict_sql['ht_ft_x2'] = self.odds['half/game'][ 'Remis/2']
        self.dict_sql['ht_ft_12'] = self.odds['half/game'][ '1/2']
        self.dict_sql['ht_ft_xx'] = self.odds['half/game'][ 'Remis/Remis']
        ###Dotąd
        self.dict_sql['_1st_half_1']= self.odds['1st_half'][ '1']
        self.dict_sql['_1st_half_x'] = self.odds['1st_half'][ 'Remis']
        self.dict_sql['_1st_half_2'] = self.odds['1st_half'][ '2']
        self.dict_sql['_1st_half_10'] = self.odds['1st_half']['Drużyna 1 lub remis']
        self.dict_sql['_1st_half_02'] = self.odds['1st_half']['Drużyna 2 lub remis']
        self.dict_sql['_1st_half_12'] = self.odds['1st_half']['Drużyna 1 lub Drużyna 2']
        self.dict_sql['eh-1_1'] = self.odds['eh']['1 (-1.0)']
        #self.dict_sql['eh-1_x2'] = self.odds['eh-1']['02']
        self.dict_sql['u_25_1'] = self.odds['game_and_goals25']['1 i Poniżej 2.5']
        self.dict_sql['o_25_1'] = self.odds['game_and_goals25']['1 i Powyżej 2.5']
        self.dict_sql['u_25_x'] = self.odds['game_and_goals25']['Remis i Poniżej 2.5']
        self.dict_sql['o_25_x'] = self.odds['game_and_goals25']['Remis i Powyżej 2.5']
        self.dict_sql['u_25_2'] = self.odds['game_and_goals25']['2 i Poniżej 2.5']
        self.dict_sql['o_25_2'] = self.odds['game_and_goals25']['2 i Powyżej 2.5']
        self.dict_sql['u_35_1'] = self.odds['game_and_goals35']['1 i Poniżej 3.5']
        self.dict_sql['o_35_1'] = self.odds['game_and_goals35']['1 i Powyżej 3.5']
        self.dict_sql['u_35_x'] = self.odds['game_and_goals35']['Remis i Poniżej 3.5']
        self.dict_sql['o_35_x'] = self.odds['game_and_goals35']['Remis i Powyżej 3.5']
        self.dict_sql['u_35_2'] = self.odds['game_and_goals35']['2 i Poniżej 3.5']
        self.dict_sql['o_35_2'] = self.odds['game_and_goals35']['2 i Powyżej 3.5']
        #self.dict_sql['1_st_goal_1'] = self.odds['1st_goal'][sehome]
        #self.dict_sql['1_st_goal_2'] = self.odds['1st_goal'][away]
        #self.dict_sql['1_st_goal_0'] = self.odds['1st_goal']['nikt']
        print (self.dict_sql)
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
        table='"db_lvbet"'
        columns_string = '("' + '","'.join(meczyk.dict_sql.keys()) + '")'
        values_string = '("' + '","'.join(map(str, meczyk.dict_sql.values())) + '")'
        try:
            sql_command="DELETE FROM %s WHERE home=%s and away=%s and data=%s" % (table,"'"+home+"'","'"+away+"'")
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
    def __init__(self, events_mapping_lvbet):
        self.__events_mapping=events_mapping_lvbet
        self.get_name()
        self.get_odds()
        #self.get_odds()
        self.prepare_dict_to_sql()


meczyk = football_event(events_mapping_lvbet)
meczyk.save_to_db()
