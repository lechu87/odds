import urllib.request as urlib2

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
headers={'User-Agent':user_agent,}
sites=['https://www.sts.pl/pl/oferta/zaklady-bukmacherskie/zaklady-sportowe/?action=offer&sport=184&region=6502&league=43461']

request=urlib2.Request(sites[0],None,headers)
response = urlib2.urlopen(request)
data = response.read()

#strona=urllib2.Request(sites[0],headers=hdr).read()