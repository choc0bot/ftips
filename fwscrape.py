import urllib2
import re
from bs4 import BeautifulSoup
import requests
#import sqlite3 as sql
#from dateutil import parser
import sys
import time
import json
from firebase import Firebase




start_time = time.mktime(time.gmtime())

def update_progress(progress, max_time, starting_time=start_time):
    """ Pretty prints a progress bar """

    percent = float(progress)/float(max_time)
    int_percent = int(percent*100)
    elapsed_min = (time.mktime(time.gmtime())-starting_time)/60.0
    if percent > 0:
        eta_min = int(round(elapsed_min/percent))
    else:
        eta_min = '?'
    sys.stdout.write( '\r[{0}{2}] {1}% ({3}) Elapsed:{4}min ETA:{5}min'.format('#'*(int_percent), int_percent,' '*(100-(int_percent)), progress, int(elapsed_min), eta_min))
    sys.stdout.flush()


class Footywire_Scraper:
    def __init__(self):
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Referer":"http://www.google.com.au","Cache-Control":"max-age=0"}
        self.baseURL = "http://www.footywire.com/afl/footy/"

    def get_ladder(self):
        """Parses footywire HTML to get ladder"""


        ladder_url = "ft_ladder"
        session = requests.session()
        response = session.get(self.baseURL + ladder_url, headers=self.headers)
        soup = BeautifulSoup(response.text)

        ladder = []
        ladder_header = soup.find_all(text=re.compile('AFL Season  Ladder'))

        team_header = soup.find_all(href=re.compile('th-'))

        #team_link = soup.find_all('a')

        #linkre=re.compile('th-')

        for link in soup.find_all('a'):
            mylink = link.get('href')
            if mylink.find('/') == -1:
                if mylink.find('ft') == -1:
                    #mylink = mylink.translate(None, 'th-')
                    #mylink = mylink.translate(None, '-')
                    mylink = mylink[3:]
                    mylink = mylink.replace('-', ' ')
                    ladder.append((mylink))



        print json.dumps(ladder)

        print "================="

        if ladder:
            f = Firebase('https://flickering-fire-9394.firebaseio.com/ladder')
            response = f.remove()
            print response
            for team in ladder:
                print team
                r = f.push({'team_id': team })
                print r

            text_file = open("Output.txt", "w")
            text_file.write(json.dumps(ladder))
            text_file.close()
            #print ladder_header
            #print team_header

    def get_results(self):
        """Parses footywire HTML to get ladder"""



        result_url = "ft_match_list?year=2015"
        session = requests.session()
        response = session.get(self.baseURL + result_url, headers=self.headers)
        soup = BeautifulSoup(response.content)

        result = []
        #result_header = soup.find_all(text=re.compile('Round'))
        #print result_header
        team_header = soup.find_all(href=re.compile('th-'))
        print team_header

        for link in team_header:
            mylink = link.get('href')
            print mylink

        #team_link = team_header.find_all('a')
        #print team_link

        """
        for link in soup.find_all('a'):
            mylink = link.get('href')
            if mylink.find('/') == -1:
                if mylink.find('ft') == -1:
                    #mylink = mylink.translate(None, 'th-')
                    #mylink = mylink.translate(None, '-')
                    mylink = mylink[3:]
                    mylink = mylink.replace('-', ' ')
                    result.append((mylink))



        print json.dumps(result)

        print "================="
        
        if result:
            f = Firebase('https://flickering-fire-9394.firebaseio.com/result')
            response = f.remove()
            print response
            for team in result:
                print team
                r = f.push({'team_id': team })
                print r

            text_file = open("Output.txt", "w")
            text_file.write(json.dumps(result))
            text_file.close()
            #print result_header
            #print team_header
        """


scraper = Footywire_Scraper()
#ladder = scraper.get_ladder()
results = scraper.get_results()
