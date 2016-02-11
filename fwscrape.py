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

    def clean_team(self, mylink):
        mylink = mylink[3:]
        mylink = mylink.replace('-', ' ')
        return mylink

    def doit(self, text):      
        matches=re.findall(r'\"(.+?)\"',text)
        # matches is now ['String 1', 'String 2', 'String3']
        return ",".join(matches)

    def list_to_file(self, thelist, filename):
        thefile = filename + ".txt"
        text_file = open(thefile, "w")
        for item in thelist:
           text_file.write("%s\n" % item)

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
        soup = BeautifulSoup(response.text,'html.parser')


        result = []
        #result_header = soup.find_all(text=re.compile('Round'))
        #print result_header
        team_header = soup.find_all(href=re.compile('th-'))
        #print team_header

        team_list = []
        count = 0
        #for link in team_header:
        for count in range(0, 414):
            link = team_header[count]
            print link
            mylink = link.get('href')
            team_list.append(scraper.clean_team(mylink))


        scraper.list_to_file(team_list, 'teams')

        scores = soup.find_all(href=re.compile('ft_match_statistics'))

        final_match_list = []
        count = 0
        for score in scores:
            match_score = score.string
            count +=1
            match_list = match_score.split('-')
            final_match_list.append(match_list[0])
            final_match_list.append(match_list[1])

        scraper.list_to_file(final_match_list, 'scores')

    def get_results_ext(self):
        """Parses footywire HTML to get ladder"""



        result_url = "ft_match_list?year=2015"
        session = requests.session()
        response = session.get(self.baseURL + result_url, headers=self.headers)
        soup = BeautifulSoup(response.text,'html.parser')


        result = []
        #result_header = soup.find_all(text=re.compile('Round'))
        #print result_header

        #team_header = soup.find_all(tr=re.compile('#f2f4f7'))
        allrows = soup.findAll('tr')
        userrows = [t for t in allrows if t.findAll(text=re.compile('v '))]


        rowlist = []
        count = 0
        for row in userrows:
            rowtxt = row.findAll(href=re.compile('th-'))
            rowlist.append(rowtxt)

        for row in userrows:
            rowtxt = row.findAll(href=re.compile('ft_match_statistics'))
            #print rowtxt
            if rowtxt == []:
                pass
                #count += 1
                #print "Round" + str(count)
            else:
                scraper.score_string(str(rowtxt), '>', '<')
            #rowlist.append(rowtxt)

        idx = 0
        count = 0
        for row in rowlist:
            if count > 23:
                return
            if row == []:
                count += 1
                #print "Round" + str(count)
            else:
                thteam = scraper.doit(str(row[0]))
                thteam_two = scraper.doit(str(row[1]))
                #print scraper.clean_team(thteam) + " vs " + scraper.clean_team(thteam_two)
            idx += 1

        #scraper.list_to_file(team_list, 'teams')

        scores = soup.find_all(href=re.compile('ft_match_statistics'))

        final_match_list = []
        count = 0
        for score in scores:
            match_score = score.string
            count += 1
            match_list = match_score.split('-')
            final_match_list.append(match_list[0])
            final_match_list.append(match_list[1])

        #scraper.list_to_file(final_match_list, 'scores')

    def score_string(self, s_string, split_one, split_two):
        score_one = s_string.split('>')
        print score_one[1]



scraper = Footywire_Scraper()
#ladder = scraper.get_ladder()
results = scraper.get_results_ext()
