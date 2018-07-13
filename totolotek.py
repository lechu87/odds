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
    logging.basicConfig(filename='logfile_totolotek.log', level=logging.DEBUG)

    def open_site(self,site):
        #league_list = 'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=114&gameId=0&gameParam=0'
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib2.Request(site, None, headers)
        response = urllib2.urlopen(request)
        data = response.read()
        soup = BeautifulSoup(data,"html.parser")
        json_var=json.loads(data)
        return json_var['Response']

    def get_name(self, json_var):
        #soup = BeautifulSoup(data, "html.parser")
        self.league = unify_name(json_var['TournamentDescription'], leagues, logging)
        self.home=unify_name(json_var['Team1Description'],teams,logging)
        self.away=unify_name(json_var['Team2Description'],teams,logging)
        self.date=json_var['EventDate']
        self.hour=json_var['EventTime']
        current_time = datetime.datetime.now()
        self.update_time = str('{:04d}'.format(current_time.year)) + '-' + str(
            '{:02d}'.format(current_time.month)) + '-' + str('{:02d}'.format(current_time.day)) + \
                           '-' + str('{:02d}'.format(current_time.hour)) + '-' + str(
            '{:02d}'.format(current_time.minute)) + '-' + str('{:02d}'.format(current_time.second))
        #print (json_var)
        print (self.league)
        print (self.home)
        print (self.away)

    def prepare_dict_to_sql(self, json_var):
        self.dict_sql = defaultdict(str)
        self.dict_sql['home']=self.home
        self.dict_sql['away']=self.away
        goal_dict = defaultdict(int)
        for goals in (0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5):
            goal_dict[goals] = defaultdict(int)
            for el in json_var['MarketGroups'][0]['Bets']:
                if el['Description'] == 'Liczba bramek' and el['Odds'][0]['FcParam'] == goals:
                    goal_dict[goals]['under'] = el['Odds'][0]['Odd']
                    goal_dict[goals]['over'] = el['Odds'][1]['Odd']
        #print (goal_dict)
        handi_dict = defaultdict(int)
        for handi in (-1.5, 1.5, -2.5, 2.5, -4.5, 3.5, -4.5, 4.5):
            handi_dict[handi] = defaultdict(int)
            for el in json_var['MarketGroups'][0]['Bets']:
                if el['Description'] == 'Handicap' and el['Odds'][0]['FcParam'] == handi:
                    handi_dict[handi]['+'] = el['Odds'][0]['Odd']
                    handi_dict[handi]['-'] = el['Odds'][1]['Odd']
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
        self.dict_sql['totolotek_game_1']=json_var['MarketGroups'][0]['Bets'][0]['Odds'][0]['Odd']
        self.dict_sql['totolotek_game_0']=json_var['MarketGroups'][0]['Bets'][0]['Odds'][1]['Odd']
        #print (self.dict_sql['totolotek__1'])
        self.dict_sql['totolotek_game_2'] =json_var['MarketGroups'][0]['Bets'][0]['Odds'][2]['Odd']
        self.dict_sql['totolotek_game_10']=json_var['MarketGroups'][0]['Bets'][0]['Odds'][3]['Odd']
        self.dict_sql['totolotek_game_02']=json_var['MarketGroups'][0]['Bets'][0]['Odds'][5]['Odd']
        self.dict_sql['totolotek_game_12']=json_var['MarketGroups'][0]['Bets'][0]['Odds'][4]['Odd']
        self.dict_sql['League']=self.league
        self.dict_sql['data']=self.date
        self.dict_sql['hour']=self.hour
        self.dict_sql['totolotek_update_time']=self.update_time
        #self.dict_sql['totolotek_country']=self.
        try:
            self.dict_sql['totolotek_dnb_1']=get_o(json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Remis zwrot','0')]['Odds'][0]['Odd'])
        except:
            logging.info("FEW BETS FOR: "+ self.home + ' ' + self.away + ' ' + self.date)
            self.dict_sql['totolotek_dnb_1'] = 1.0
        try:
            self.dict_sql['totolotek_dnb_2']=json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Remis zwrot','0')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_dnb_2'] = 1.0
        self.dict_sql['totolotek_o_05'] = goal_dict[0.5]['over']
        self.dict_sql['totolotek_u_05'] = goal_dict[0.5]['under']
        self.dict_sql['totolotek_o_15'] = goal_dict[1.5]['over']
        self.dict_sql['totolotek_u_15'] = goal_dict[1.5]['under']
        self.dict_sql['totolotek_o_25'] = goal_dict[2.5]['over']
        self.dict_sql['totolotek_u_25'] = goal_dict[2.5]['under']
        self.dict_sql['totolotek_u_35'] = goal_dict[3.5]['under']
        self.dict_sql['totolotek_o_35'] = goal_dict[3.5]['over']
        self.dict_sql['totolotek_o_45'] = goal_dict[4.5]['over']
        self.dict_sql['totolotek_u_45'] = goal_dict[4.5]['under']
        self.dict_sql['totolotek_o_55'] = goal_dict[5.5]['over']
        self.dict_sql['totolotek_u_55'] = goal_dict[5.5]['under']
        self.dict_sql['totolotek_o_65'] = goal_dict[6.5]['over']
        self.dict_sql['totolotek_u_65'] = goal_dict[6.5]['under']
        self.dict_sql['totolotek_o_75'] = goal_dict[7.5]['over']
        self.dict_sql['totolotek_u_75'] = goal_dict[7.5]['under']
        self.dict_sql['totolotek_o_85'] = goal_dict[8.5]['over']
        self.dict_sql['totolotek_u_85'] = goal_dict[8.5]['under']
        self.dict_sql['totolotek_o_95'] = goal_dict[9.5]['over']
        self.dict_sql['totolotek_u_95'] = goal_dict[9.5]['under']
        try:
            self.dict_sql['totolotek_ht_ft_11'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][0]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_11'] = 1.0
        try:
            self.dict_sql['totolotek_ht_ft_1x'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][3]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_1x'] = 1.0
        try:
            self.dict_sql['totolotek_ht_ft_2x'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][5]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_2x'] = 1.0
        try:
            self.dict_sql['totolotek_ht_ft_21'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][2]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_21'] = 1.0
        try:
            self.dict_sql['totolotek_ht_ft_22'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][8]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_22'] = 1.0
        try:
            self.dict_sql['totolotek_ht_ft_x1'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_x1'] = 1.0
        try:
            self.dict_sql['totolotek_ht_ft_x2'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][7]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_x2'] = 1.0
        try:
            self.dict_sql['totolotek_ht_ft_12'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][6]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_12'] = 1.0
        try:
            self.dict_sql['totolotek_ht_ft_xx'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa/koniec meczu','0')]['Odds'][4]['Odd']
        except:
            self.dict_sql['totolotek_ht_ft_xx'] = 1.0
        try:
            self.dict_sql['totolotek_first_half_1']=json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa','0')]['Odds'][0]['Odd']
        except:
            self.dict_sql['totolotek_first_half_1'] = 1.0
        try:
            self.dict_sql['totolotek_first_half_x'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa','0')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_first_half_x'] = 1.0
        try:
            self.dict_sql['totolotek_first_half_2'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa','0')]['Odds'][2]['Odd']
        except:
            self.dict_sql['totolotek_first_half_2'] = 1.0
        try:
            self.dict_sql['totolotek_first_half_10'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa','0')]['Odds'][3]['Odd']
        except:
            self.dict_sql['totolotek_first_half_10'] = 1.0
        try:
            self.dict_sql['totolotek_first_half_02'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa','0')]['Odds'][5]['Odd']
        except:
            self.dict_sql['totolotek_first_half_02'] = 1.0
        try:
            self.dict_sql['totolotek_first_half_12'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwsza połowa','0')]['Odds'][4]['Odd']
        except:
            self.dict_sql['totolotek_first_half_12'] = 1.0
            # #self.dict_sql['totolotek_eh-1_1'] = self.odds['eh-1']['1']
        # #self.dict_sql['totolotek_eh-1_x2'] = self.odds['eh-1']['02']
        try:
            self.dict_sql['totolotek_u_15_1'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/ilość goli','0')]['Odds'][0]['Odd']
        except:
            self.dict_sql['totolotek_u_15_1'] = 1.0
        try:
            self.dict_sql['totolotek_o_15_1'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/ilość goli','0')]['Odds'][3]['Odd']
        except:
            self.dict_sql['totolotek_o_15_1'] = 1.0
        try:
            self.dict_sql['totolotek_u_15_x'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/ilość goli','0')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_u_15_x'] = 1.0
        try:
            self.dict_sql['totolotek_o_15_x'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/ilość goli','0')]['Odds'][4]['Odd']
        except:
            self.dict_sql['totolotek_o_15_x'] = 1.0
        try:
            self.dict_sql['totolotek_u_15_2'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/ilość goli','0')]['Odds'][2]['Odd']
        except:
            self.dict_sql['totolotek_u_15_2'] = 1.0
        try:
            self.dict_sql['totolotek_o_15_2'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/ilość goli','0')]['Odds'][5]['Odd']
        except:
            self.dict_sql['totolotek_o_15_2'] = 1.0
        try:
            self.dict_sql['totolotek_u_25_1'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (2.5)', '0')]['Odds'][0]['Odd']
        except:
            self.dict_sql['totolotek_u_25_1'] = 1.0
        try:
            self.dict_sql['totolotek_o_25_1'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (2.5)', '0')]['Odds'][3]['Odd']
        except:
            self.dict_sql['totolotek_o_25_1'] = 1.0
        try:
            self.dict_sql['totolotek_u_25_x'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (2.5)', '0')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_u_25_x'] = 1.0
        try:
            self.dict_sql['totolotek_o_25_x'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (2.5)', '0')]['Odds'][4]['Odd']
        except:
            self.dict_sql['totolotek_o_25_x'] = 1.0
        try:
            self.dict_sql['totolotek_u_25_2'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (2.5)', '0')]['Odds'][2]['Odd']
        except:
            self.dict_sql['totolotek_u_25_2'] = 1.0
        try:
            self.dict_sql['totolotek_o_25_2'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (2.5)', '0')]['Odds'][5]['Odd']
        except:
            self.dict_sql['totolotek_o_25_2'] = 1.0
        try:
            self.dict_sql['totolotek_u_35_1'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (3.5)', '0')]['Odds'][0]['Odd']
        except:
            self.dict_sql['totolotek_u_35_1'] = 1.0
        try:
            self.dict_sql['totolotek_o_35_1'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (3.5)', '0')]['Odds'][3]['Odd']
        except:
            self.dict_sql['totolotek_o_35_1'] = 1.0
        try:
            self.dict_sql['totolotek_u_35_x'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (3.5)', '0')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_u_35_x'] = 1.0
        try:
            self.dict_sql['totolotek_o_35_x'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (3.5)', '0')]['Odds'][4]['Odd']
        except:
            self.dict_sql['totolotek_o_35_x'] = 1.0
        try:
            self.dict_sql['totolotek_u_35_2'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (3.5)', '0')]['Odds'][2]['Odd']
        except:
            self.dict_sql['totolotek_u_35_2'] = 1.0
        try:
            self.dict_sql['totolotek_o_35_2'] = json_var['MarketGroups'][0]['Bets'][
            get_value(json_var['MarketGroups'][0]['Bets'], 'Wynik meczu/ilość goli (3.5)', '0')]['Odds'][5]['Odd']
        except:
            self.dict_sql['totolotek_o_35_2'] = 1.0

        try:
            self.dict_sql['totolotek_btts_1'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/obie strzelą','0')]['Odds'][0]['Odd']
        except:
            self.dict_sql['totolotek_btts_1'] = 1.0
        try:
            self.dict_sql['totolotek_btts_2'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/obie strzelą','0')]['Odds'][4]['Odd']
        except:
            self.dict_sql['totolotek_btts_2'] = 1.0
        try:
            self.dict_sql['totolotek_btts_x'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/obie strzelą','0')]['Odds'][2]['Odd']
        except:
            self.dict_sql['totolotek_btts_x'] = 1.0
        try:
            self.dict_sql['totolotek_btts_no_1'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/obie strzelą','0')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_btts_no_1'] = 1.0
        try:
            self.dict_sql['totolotek_btts_no_2'] =  json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/obie strzelą','0')]['Odds'][5]['Odd']
        except:
            self.dict_sql['totolotek_btts_no_2'] = 1.0
        try:
            self.dict_sql['totolotek_btts_no_x'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Wynik meczu/obie strzelą','0')]['Odds'][3]['Odd']
        except:
            self.dict_sql['totolotek_btts_no_x'] = 1.0
        try:
            self.dict_sql['totolotek_btts_yes'] = json_var['MarketGroups'][0]['Bets'][
                get_value(json_var['MarketGroups'][0]['Bets'], 'Obie drużyny strzelą bramkę', '0')]['Odds'][0]['Odd']
        except:
            self.dict_sql['totolotek_btts_yes'] = 1.0
        try:
            self.dict_sql['totolotek_btts_no'] = json_var['MarketGroups'][0]['Bets'][
                get_value(json_var['MarketGroups'][0]['Bets'], 'Obie drużyny strzelą bramkę', '1')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_btts_no'] = 1.0
            # self.dict_sql['totolotek_eh-1_1'] = self.odds['ah-']['1 (Handicap 0:1)']
        # self.dict_sql['totolotek_eh-1_x'] = self.odds['ah-']['X (Handicap 0:1)']
        # self.dict_sql['totolotek_eh-1_2'] = self.odds['ah-']['2 (Handicap 0:1)']
        # self.dict_sql['totolotek_eh+1_1'] = self.odds['ah+']['1 (Handicap 1:0)']
        # self.dict_sql['totolotek_eh+1_x'] = self.odds['ah+']['X (Handicap 1:0)']
        # self.dict_sql['totolotek_eh+1_2'] = self.odds['ah+']['2 (Handicap 1:0)']
        try:
            self.dict_sql['totolotek_first_goal_1'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwszy gol','0')]['Odds'][0]['Odd']
        except:
            self.dict_sql['totolotek_first_goal_1'] = 1.0
        try:
            self.dict_sql['totolotek_first_goal_2'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwszy gol','0')]['Odds'][2]['Odd']
        except:
            self.dict_sql['totolotek_first_goal_2']=1.0
        try:
            self.dict_sql['totolotek_first_goal_0'] = json_var['MarketGroups'][0]['Bets'][get_value(json_var['MarketGroups'][0]['Bets'],'Pierwszy gol','0')]['Odds'][1]['Odd']
        except:
            self.dict_sql['totolotek_first_goal_0']=1.0
        #
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
        table='"db_totolotek"'
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
        #self.open_site(url)
        self.get_name(self.data)
        #self.get_odds2()

        self.prepare_dict_to_sql(self.data)
        #self.save_to_db()
        save_to_db_common(self,"'"+self.date+"'")
sites=['https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=114&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=116&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=112&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=156&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=141&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=118&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=127&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=2713&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=145&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=1329&gameId=0&gameParam=0',
       'https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=165&gameId=0&gameParam=0']
#sites=['https://m.totolotek.pl/PalinsestoRest/GetEventsByMarket?filter=Any&sportId=2&tournamentId=2713&gameId=0&gameParam=0',]
logging.basicConfig(filename='logfile_totolotek.log', level=logging.DEBUG)
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