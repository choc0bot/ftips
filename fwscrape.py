#import urllib2
import re
from bs4 import BeautifulSoup
import requests
#import sqlite3 as sql
#from dateutil import parser
import sys
import time
#import json
from firebase import Firebase




start_time = time.mktime(time.gmtime())

team_dict = {
    'adelaide crows': 'adelaide',
    'brisbane lions': 'brisbane',
    'western bulldogs':'bulldogs',
    'carlton blues': 'carlton',
    'collingwood magpies': 'collingwood',
    'essendon bombers': 'essendon',
    'fremantle dockers': 'fremantle',
    'gold coast suns': 'gc',
    'geelong cats': 'geelong',
    'greater western sydney giants': 'gws',
    'hawthorn hawks': 'hawthorn',
    'melbourne demons': 'melbourne',
    'kangaroos': 'north',
    'port adelaide power': 'port',
    'richmond tigers': 'richmond',
    'st kilda saints': 'stkilda',
    'sydney swans': 'sydney',
    'west coast eagles': 'wce',
}

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

def clean_team(mylink):
    """removes - from string"""
    mylink = mylink[3:]
    mylink = mylink.replace('-', ' ')
    return mylink

def doit(text):
    """cleans up score_string string"""
    matches = re.findall(r'\"(.+?)\"', text)
    return ",".join(matches)

def list_to_file(thelist, filename):
    """outputs inputed list to a text file """
    thefile = filename + ".txt"
    print thefile
    text_file = open(thefile, "w")
    for item in thelist:
        text_file.write("%s\n" % item)

def multipleReplace(text):
    for key in team_dict:
        text = text.replace(key, team_dict[key])
    return text

def parse_result(team_one, score_one, team_two, score_two):
    score_o = int(score_one)
    score_t = int(score_two)
    team_one = multipleReplace(team_one)
    team_two = multipleReplace(team_two)
    if score_o > score_t:
        result = team_one +" "+ score_one +" def " + team_two +" "+ score_two
    elif score_t > score_o:
        result = team_two +" "+ score_two + " def " + team_one +" "+ score_one
    else:
        result = team_one +" "+ score_one +" drew "+ team_two +" "+ score_two
    return result




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

        for link in soup.find_all('a'):
            mylink = link.get('href')
            if mylink.find('/') == -1:
                if mylink.find('ft') == -1:
                    mylink = mylink[3:]
                    mylink = mylink.replace('-', ' ')
                    ladder.append((mylink))

        if ladder:
            f = Firebase('https://flickering-fire-9394.firebaseio.com/ladder')
            response = f.remove()
            print response
            for team in ladder:
                team = multipleReplace(team)
                print team
                r = f.push({'team_id': team })

    def get_results_ext(self):
        """Parses footywire HTML to get ladder"""

        result_url = "ft_match_list?year=2015"
        session = requests.session()
        response = session.get(self.baseURL + result_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')


        scores = soup.find_all(href=re.compile('ft_match_statistics'))

        final_match_list = []

        for score in scores:
            match_score = score.string
            final_match_list.append(match_score)

        #list_to_file(final_match_list, 'scores')

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

        firebasedb = Firebase('https://flickering-fire-9394.firebaseio.com/results/')
        response = firebasedb.remove()
        length = len(rowlist) - 3
        newlist = rowlist[-length:]
        count = 1
        idx = 0
        for row in newlist:
            if count < 25:
                if row == []:
                    current_round = "round" + str(count)
                    count += 1
                    print current_round
                else:
                    thteam = doit(str(row[0]))
                    thteam_two = doit(str(row[1]))
                    #thteam = clean_team(thteam)
                    #thteam_two = clean_team(thteam_two)
                    match_score_one, match_score_two = scraper.format_match_score(final_match_list[idx])
                    idx += 1
                    result = parse_result(clean_team(thteam), match_score_one, clean_team(thteam_two), match_score_two)
                    fireb = Firebase('https://flickering-fire-9394.firebaseio.com/results/'+ current_round)
                    resp = fireb.push({'match': result })
                    #print result
                    """
                    resp = fireb.push({'team_one': thteam })
                    print thteam
                    resp = fireb.push({'score_one': match_score_one })
                    print match_score_one
                    resp = fireb.push({'team_two': thteam_two })
                    print thteam_two
                    resp = fireb.push({'score_two': match_score_two })
                    print match_score_two
                    """


    def score_string(self, s_string, split_one, split_two):
        "removes html chrs"
        score_one = s_string.split('>')
        score_two = score_one[1].split('<')
        return score_two[0]

    def format_match_score(self, match_score):
        "Takes match score of aa-bb and returns aa, bb"
        match_score_split = match_score.split("-")
        return match_score_split[0], match_score_split[1]


scraper = Footywire_Scraper()
ladder = scraper.get_ladder()
results = scraper.get_results_ext()
