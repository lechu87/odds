from bs4 import BeautifulSoup
import urllib2

#url = ('www.efortuna.pl/pl/strona_glowna/serwis_sportowy/polskie_ligi/index.html')

#r = requests.get("https://" +url)
data=urllib2.urlopen('http://www.efortuna.pl/pl/strona_glowna/serwis_sportowy/polskie_ligi/index.html').read()
#data = r.text

soup = BeautifulSoup(data,'lxml')
#x=soup.find_all(name='bet_item_main_text')
#print x

#print soup.prettify()
# <span class="bet_item_main_text">
# 						<a id="title-602" class="bet_item_detail_href" href="/pl/strona_glowna/pilka-nozna/2017-07-22-lechia-g----cracovia-14014126">Lechia G. - Cracovia </a>
# <span id="id-602" class="bet_item_info_id">602</span>
# <span class="bet_item_subcontent">
# 							<span class="matchComment">live Canal+Sport</span>
# <div class="bet_item_content_icons">
# <a href="http://stats.betradar.com/s4/?clientid=147&amp;language=pl&amp;clientmatchid=14014126&amp;treemenu=false" target="_blank" class="right betradar bet_table_icon bet_table_icon_holder bti_stats_betradar" title="Statystyki"></a>
# <div class="clear"></div>
# 							</div>
# <span class="bet_item_content_icons_placer"><span style="width: 15px;">&nbsp;</span></span>
# </span>
# 					</span>

#x=soup.find_all(id='betTable-25-1')
tables=soup.find_all('table')[2]
#print tables
table_body = tables.find('tbody')
rows=table_body.find_all('tr')
game=[]
for tr in rows:
    cols=tr.find_all('td')
    for td in cols:
        try:
            a=td.find_all('a')
            #print a
            #print td.div.span.a.text
            for i in a:
                if len(i.text)>0:
                    game.append(i.text.strip())
                print i.text
            #print td.div.a.text
        except:
            continue
print("/////////////////")
print game

exit()


table=soup.find_all(class_='bet_tables_holder')
#table = soup.find_all("table", { "class" : "bet_table last_table" })
for mytable in table:
    print mytable
    table_body = mytable.find('thead')
    try:
        rows = table_body.find_all('tr')
        for tr in rows:
            cols = tr.find_all('td')
            for td in cols:
                print td.text
    except:
        print "no tbody"



#print(x.__contains__(x)[0])
#for element in x:
#    print (element.div.table.tbody.tr.text)

    #print(element)
    #print(element.td.div.span.a.text)
#for element in x:
#    print element

for link in soup.find_all('bet_item_main_text'):
    print(link.get('href'))