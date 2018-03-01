from bs4 import BeautifulSoup
import urllib.request as urllib2
import sqlite3
import json
from dictionaries import *
import logging
import datetime

def get_value(json,tittle,fcparam='0'):
    for i in range(0, len(json)):
        if json[i]['Description'] == tittle:
            return i

class football_event:
    logging.basicConfig(filename='logfile_lvbet.log', level=logging.DEBUG)

    def open_site(self,site):
        #league_list = 'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=114&gameId=0&gameParam=0'
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib2.Request(site, None, headers)
        response = urllib2.urlopen(request)
        data = response.read()
        soup = BeautifulSoup(data,"html.parser")
        json_var=json.loads(data)
        return json_var

    def get_name(self, json_var):
        #soup = BeautifulSoup(data, "html.parser")
        print (json_var['sportsGroups'][2]['name'])
        #self.league = unify_name(json_var['sportsGroups'][2]['name'], leagues, logging)
        self.league = unify_name(json_var['sportsGroups'][2]['label'], leagues, logging)
        self.raw_home=json_var['participants']['home']
        self.raw_away=json_var['participants']['away']
        self.home=unify_name(json_var['participants']['home'],teams,logging)
        self.away=unify_name(json_var['participants']['away'],teams,logging)
        self.date=json_var['date'].split('T')[0]
        #self.hour=json_var['EventTime']
        current_time = datetime.datetime.now()
        self.update_time = str('{:04d}'.format(current_time.year)) + '-' + str(
            '{:02d}'.format(current_time.month)) + '-' + str('{:02d}'.format(current_time.day)) + \
                           '-' + str('{:02d}'.format(current_time.hour)) + '-' + str(
            '{:02d}'.format(current_time.minute)) + '-' + str('{:02d}'.format(current_time.second))
        #print (json_var)
        #print (self.league)
        #print (self.home)
        #print (self.away)
        #print (self.date)
        #print (self.update_time)

    def get_rate(self,json, name, raw_home):
        for i in range(0, len(json)):
            #print (json[i]['selections'][0]['name'])
            x=''
            if json[i]['name'].lower() == name.lower():
                for j in range(0, len(json[i]['selections'])):
                    if (json[i]['selections'][j]['name']).lower() == (raw_home.lower()):
                        #print ("ZNALAZLEM")
                        #print (json[i]['selections'][j]['rate']['decimal'])
                        x=json[i]['selections'][j]['rate']['decimal']
                        return x
            else:
                #
                #return 1.0
                continue
                # print ("NR: ",i)
                # print (json[i]['selections'])
#######Sypie dużo warningów: !!!!!!!!!!!!!!
#        if x=='':
#            logging.warning(
#                "ERROR. Nie znalazlem " + name + " " + raw_home + " dla " + self.raw_home + " " + self.raw_away)
    def prepare_dict_to_sql(self, json_var):
        self.dict_sql = defaultdict(str)
        self.dict_sql['home']=self.home
        self.dict_sql['away']=self.away
        goal_dict = defaultdict(int)
        for goals in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5):
            goal_dict[goals] = defaultdict(int)
            for el in json_var['markets']:
                if el['name'] == 'Liczba goli' and el['selections'][0]['name'] == 'Powyżej ('+str(goals)+')':
                    goal_dict[goals]['over'] = el['selections'][0]['rate']['decimal']
                    goal_dict[goals]['under'] = el['selections'][1]['rate']['decimal']

        handi_dict = defaultdict(int)
        for handi in (-1.0, -2.0, -3.0, 1.0, 2.0, 3.0,):
            handi_dict[handi] = defaultdict(int)
            for el in json_var['markets']:
                if el['name'] == '3-drogowy handicap' and el['selections'][0]['name'] == str(self.raw_home) + ' ('+str(handi)+')':
                    handi_dict[handi]['1'] = el['selections'][0]['rate']['decimal']
                    handi_dict[handi]['x'] = el['selections'][1]['rate']['decimal']
                    handi_dict[handi]['2'] = el['selections'][2]['rate']['decimal']
#        print (handi_dict)
        def get_o(x):
            default=1.0
            try:
                tmp=x
                return tmp
            except:
                return default
        #print ("HANDI DICT:",handi_dict)
        #print (get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu 1X2'))
        #print (get_value(json_var['MarketGroups'][0]['Bets'], 'Pierwsza połowa'))
        #print (get_value(json_var['MarketGroups'][0]['Bets'], 'Pierwsza połowa'))
        #self.dict_sql['_1']=json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu 1X2','0')]['Odds'][0]['Odd']
        self.dict_sql['game_1']=self.get_rate(json_var['markets'],"Zwycięzca meczu",self.raw_home)
        self.dict_sql['game_0']=self.get_rate(json_var['markets'],"Zwycięzca meczu",'Remis')
        #print (self.dict_sql['_1'])
        self.dict_sql['game_2'] =self.get_rate(json_var['markets'],"Zwycięzca meczu",self.raw_away)
#        print (self.dict_sql)
        #self.ge
        self.dict_sql['game_10']=self.get_rate(json_var['markets'],"Podwójna szansa",'Drużyna 1 lub remis')
        self.dict_sql['game_02']=self.get_rate(json_var['markets'],"Podwójna szansa",'Drużyna 2 lub remis')
        self.dict_sql['game_12']=self.get_rate(json_var['markets'],"Podwójna szansa",'Drużyna 1 lub Drużyna 2')
        self.dict_sql['League']=self.league
        self.dict_sql['data']=self.date
        #self.dict_sql['hour']=self.hour
        self.dict_sql['update_time']=self.update_time
        #self.dict_sql['country']=self
        self.dict_sql['dnb_1']=self.get_rate(json_var['markets'],"Zakład bez remisu",'Drużyna 1')
        self.dict_sql['dnb_2']=self.get_rate(json_var['markets'],"Zakład bez remisu",'Drużyna 2')
        self.dict_sql['o_05'] = goal_dict[0.5]['over']
        self.dict_sql['u_05'] = goal_dict[0.5]['under']
        self.dict_sql['o_15'] = goal_dict[1.5]['over']
        self.dict_sql['u_15'] = goal_dict[1.5]['under']
        self.dict_sql['o_25'] = goal_dict[2.5]['over']
        self.dict_sql['u_25'] = goal_dict[2.5]['under']
        self.dict_sql['u_35'] = goal_dict[3.5]['under']
        self.dict_sql['o_35'] = goal_dict[3.5]['over']
        self.dict_sql['o_45'] = goal_dict[4.5]['over']
        self.dict_sql['u_45'] = goal_dict[4.5]['under']
        self.dict_sql['o_55'] = goal_dict[5.5]['over']
        self.dict_sql['u_55'] = goal_dict[5.5]['under']
        self.dict_sql['o_65'] = goal_dict[6.5]['over']
        self.dict_sql['u_65'] = goal_dict[6.5]['under']
        self.dict_sql['o_75'] = goal_dict[7.5]['over']
        self.dict_sql['u_75'] = goal_dict[7.5]['under']
        self.dict_sql['o_85'] = goal_dict[8.5]['over']
        self.dict_sql['u_85'] = goal_dict[8.5]['under']
        self.dict_sql['o_95'] = goal_dict[9.5]['over']
        self.dict_sql['u_95'] = goal_dict[9.5]['under']
        self.dict_sql['ht_ft_11'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",self.raw_home+'/'+self.raw_home)
        self.dict_sql['ht_ft_1x'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",'1'+'/Draw')
        self.dict_sql['ht_ft_11'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",self.raw_home+'/'+self.raw_home)
        self.dict_sql['ht_ft_2x'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",self.raw_away+'/Remis')
        self.dict_sql['ht_ft_21'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",self.raw_away+'/'+self.raw_home)
        self.dict_sql['ht_ft_22'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",self.raw_away+'/'+self.raw_away)
        self.dict_sql['ht_ft_x1'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",'Remis/'+self.raw_home)
        self.dict_sql['ht_ft_x2'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",'Remis/'+self.raw_away)
        self.dict_sql['ht_ft_12'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",self.raw_home+'/'+self.raw_away)
        self.dict_sql['ht_ft_xx'] = self.get_rate(json_var['markets'],"Do przerwy/Koniec meczu",'Remis/Remis')
        self.dict_sql['first_half_1']=self.get_rate(json_var['markets'],"1. połowa - Zwycięzca",self.raw_home)
        self.dict_sql['first_half_x'] = self.get_rate(json_var['markets'],"1. połowa - Zwycięzca",'Remis')
        self.dict_sql['first_half_2'] = self.get_rate(json_var['markets'],"1. połowa - Zwycięzca",self.raw_away)
        self.dict_sql['first_half_10'] = self.get_rate(json_var['markets'],"1. połowa - Podwójna szansa",'Drużyna 1 lub Remis')
        self.dict_sql['first_half_02'] = self.get_rate(json_var['markets'],"1. połowa - Podwójna szansa",'Drużyna 2 lub Remis')
        self.dict_sql['first_half_12'] = self.get_rate(json_var['markets'],"1. połowa - Podwójna szansa",'Drużyna 1 lub Drużyna 2')

        self.dict_sql['u_15_1'] = self.get_rate(json_var['markets'],"Wyniki i liczba bramek 1.5",self.raw_home+' i Poniżej 1.5')
        self.dict_sql['o_15_1'] = self.get_rate(json_var['markets'],"Wyniki i liczba bramek 1.5",self.raw_home+' i Powyżej 1.5')
        self.dict_sql['u_15_x'] = self.get_rate(json_var['markets'],"Wyniki i liczba bramek 1.5",'Remis i Poniżej 1.5')
        self.dict_sql['o_15_x'] = self.get_rate(json_var['markets'],"Wyniki i liczba bramek 1.5",'Remis i Powyżej 1.5')
        self.dict_sql['u_15_2'] = self.get_rate(json_var['markets'],"Wyniki i liczba bramek 1.5",self.raw_away +' i Poniżej 1.5')
        self.dict_sql['o_15_2'] = self.get_rate(json_var['markets'],"Wyniki i liczba bramek 1.5",self.raw_away +' i Powyżej 1.5')

        self.dict_sql['u_25_1'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 2.5",self.raw_home+' i Poniżej 2.5')
        self.dict_sql['o_25_1'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 2.5",self.raw_home+' i Powyżej 2.5')
        self.dict_sql['u_25_x'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 2.5",'Remis i Poniżej 2.5')
        self.dict_sql['o_25_x'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 2.5",'Remis i Powyżej 2.5')
        self.dict_sql['u_25_2'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 2.5",self.raw_away +' i Poniżej 2.5')
        self.dict_sql['o_25_2'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 2.5",self.raw_away +' i Powyżej 2.5')


        self.dict_sql['u_35_1'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 3.5",self.raw_home+' i Poniżej 3.5')
        self.dict_sql['o_35_1'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 3.5",self.raw_home+' i Powyżej 3.5')
        self.dict_sql['u_35_x'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 3.5",'Remis i Poniżej 3.5')
        self.dict_sql['o_35_x'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 3.5",'Remis i Powyżej 3.5')
        self.dict_sql['u_35_2'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 3.5",self.raw_away +' i Poniżej 3.5')
        self.dict_sql['o_35_2'] = self.get_rate(json_var['markets'],"Wynik i liczba bramek 3.5",self.raw_away +' i Powyżej 3.5')
        self.dict_sql['btts_yes'] = self.get_rate(json_var['markets'], "Obie drużyny strzelą gola",'Tak')
        self.dict_sql['btts_no'] = self.get_rate(json_var['markets'], "Obie drużyny strzelą gola", 'Nie')
        self.dict_sql['btts_1'] = self.get_rate(json_var['markets'],"Wynik i obie drużyny strzelą",self.raw_home +' i (Obie drużyny strzelą - Tak)')
        self.dict_sql['btts_2'] = self.get_rate(json_var['markets'],"Wynik i obie drużyny strzelą",self.raw_away +' i (Obie drużyny strzelą - Tak)')
        self.dict_sql['btts_x'] = self.get_rate(json_var['markets'],"Wynik i obie drużyny strzelą",'Remis i (Obie drużyny strzelą - Tak)')
        self.dict_sql['btts_no_1'] = self.get_rate(json_var['markets'],"Wynik i obie drużyny strzelą",self.raw_home +' i (Obie drużyny strzelą - Nie)')
        self.dict_sql['btts_no_2'] =  self.get_rate(json_var['markets'],"Wynik i obie drużyny strzelą",self.raw_away +' i (Obie drużyny strzelą - Nie)')
        self.dict_sql['btts_no_x'] = self.get_rate(json_var['markets'],"Wynik i obie drużyny strzelą",'Remis i (Obie drużyny strzelą - Nie)')
        self.dict_sql['eh_min_1_1'] = handi_dict[-1.0]['1']
        self.dict_sql['eh_min_1_x'] = handi_dict[-1.0]['x']
        self.dict_sql['eh_min_1_2'] = handi_dict[-1.0]['2']
        self.dict_sql['eh_plus_1_1'] = handi_dict[+1.0]['1']
        self.dict_sql['eh_plus_1_x'] = handi_dict[+1.0]['x']
        self.dict_sql['eh_plus_1_2'] = handi_dict[+1.0]['2']
        #self.dict_sql['1_st_goal_1'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwszy gol','0')]['Odds'][0]['Odd']


        #self.dict_sql['1_st_goal_2'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwszy gol','0')]['Odds'][2]['Odd']

        #self.dict_sql['1_st_goal_0'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwszy gol','0')]['Odds'][1]['Odd']

        #
        #print (self.dict_sql)
        return self.dict_sql




        #print (self.dict_sql)
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
        table='"db_lvbet"'
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


    def __init__(self, events_mapping_totolotek, url):
        self.data=self.open_site(url)
        self.__events_mapping=events_mapping_totolotek

        self.get_name(self.data)
        #self.get_odds2()

        self.prepare_dict_to_sql(self.data)
        self.save_to_db()

link='https://app.lvbet.pl/_api/v1/offer/matches/full/2974405'

meczyk=football_event(events_mapping_lvbet,link)
x=meczyk.open_site(link)
#team=meczyk.raw_away
#print (x)
#print (x['markets'][1]['name'])
#print (x['markets'][1]['selections'][0]['rate']['decimal'])

#meczyk.get_rate(x['markets'],"Match Result",team)
#meczyk.prepare_dict_to_sql(x)
#exit()
sites=['https://app.lvbet.pl/_api/v1/offer/matches/?is_live=false&sports_groups_ids=754,669,916,775,564,392,671,665,651,791,658,753,666,2345,718']
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers = {'User-Agent': user_agent, }
request = urllib2.Request(sites[0], None, headers)
response = urllib2.urlopen(request)
data = response.read()
soup = BeautifulSoup(data, "html.parser")
json_var = json.loads(data)
#print (json_var)
game_ids=[]
for i in range(0,len(json_var)):
    game_ids.append(json_var[i]['id'])

for game_id in game_ids:
    try:
        link = 'https://app.lvbet.pl/_api/v1/offer/matches/full/'+str(game_id)
        meczyk = football_event(events_mapping_lvbet, link)
        x = meczyk.open_site(link)
    except:
        logging.WARNING("ERROR DLA MECZU: "+str(game_id))

exit()




#sites=['https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=2713&gameId=0&gameParam=0',]

for site in sites:
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib2.Request(site, None, headers)
    response = urllib2.urlopen(request)
    tournamentid=site.split('&')[2].split('=')[1]
    data = response.read()
    soup = BeautifulSoup(data, "html.parser")
    json_var = json.loads(data)
    ids=[]

    for element in json_var['Response']['Events']:
        # print (element)
        try:
            if element['Bets'][0]['Odds'][0]['EventId'] not in ids:
                ids.append(element['Bets'][0]['Odds'][0]['EventId'])
                # print (element['Bets'][0]['Odds'][0]['EventId'])
        except:
            pass
    for game in ids:
        site = 'https://m.totolotek.pl/PalinsestoRest/GetEvent?sportId=2&tournamentId='+str(tournamentid)+'&eventId='+str(game)
        print (site)
        try:
            meczyk=football_event(events_mapping_totolotek,site)
        except:
            logging.WARNING("ERROR dla "+site)
            continue