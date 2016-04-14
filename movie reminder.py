from time import sleep
import MySQLdb
import json
import urllib2
import time
import os
import re
import requests
import shutil
bad = ['DVDRip', 'XviD-SCREAM', '720p', '1080p', 'mp4', 'mkv', 'avi', 'x264', 'AAC', 'ETRG', 'REPACK', 'BluRay', 'YIFY',
       'Hindi', 'X264REMO', 'english', 'BRRip', 'DVDScr', 'XVID', 'AC3', 'HQ', 'Hive', 'CM8', 'avi', 'AAC', 'MkvCage',
       'Copy', 'XViD', 'ETRG', 'DVDSCR', 'Ozlem', 'HDRip', 'XviD', 'PROPER', 'DIRECTORS CUT', 'HC', 'Eng', 'Subs',
       'HDTV', 'MVGroup', 'org', 'Thriller', 'Sci-Fi', 'DvDrip', 'EVO', 'aXXo', 'X264', 'REMO', 'Download',
       'DVDRiP', 'Zaeem', 'DTS', '480p', 'CHD', 'www', 'com', 'DVDrip', 'H264', 'anoXmous', 'WEBRip', 'AsCo',
       'REMASTERED', 'RARBG', 'EXTENDED', 'BrRip', 'WEB-DL', 'm2g', 'Comedy', 'Dual', 'Audio']

def get_name(files):
    if files.find('srt') != -1 or files.find('jpg') != -1 or files.find('pdf') != -1 or files.find('txt') != -1 or files.find('png') != -1:
        return False

    files = re.sub(r'\[([^]]+)\]', ' ', files)
    files = re.sub(r'[_]', ' ', files)
    files = re.sub(r'\(([^)]+)\)', ' ', files)
    files = re.sub(r'[0-9]+(MB|mb|GB|Mb|mB|gB|Gb)', ' ', files)
    files = re.sub(r'[12][09][0-9][0-9]', ' ', files)
    for i in bad:
        files = files.replace(i, '')
    files = re.sub('[\-]*[. ]*$', ' ', str(files).strip())
    files = re.sub('  .*$', '', files)
    return files.replace('.', ' ').strip()

def Time(time):
    try:
        return str(int(time.split()[0])) + ":00"
    except:
        return '-1'

def movies(conn, cur, params):
    if not params:
        name = raw_input("Enter a movie name\n->")
        time = raw_input("Enter the time stopped at\n->")
    else:
        name = params[0]
        time = params[1]
    if time != '-1':
        time += ":00"
    sql_search = """SELECT * FROM remaining.movies WHERE Name LIKE "%%%s%%" """ % str(name)
    print(sql_search)
    try:
        cur.execute(sql_search)
        res = cur.fetchall()
        results = []
        for i in res:
            if i[2] != i[3]:
                results.insert(0, i)
            else:
                results.append(i)
        print("-1)search online")
        for key, res in enumerate(results):
            if res[2] != res[3]:
                print(" " + str(key) + ")" + res[1] + "(" + res[7] + "):" + res[6])
            else:
                print("*" + str(key) + ")" + res[1] + "(" + res[7] + "):" + res[6])
        opt = raw_input("->")
        if opt == '-1':
            data_json = search(name, 'movie')
            if data_json == False:
                opt = raw_input("Could not find the movie, add anyways(y/n)\n->")
                if opt == 'y':
                    sql_insert = """INSERT INTO remaining.movies(Name, watched) VALUES ("%s", "%s")""" % (name, time)
                    cur.execute(sql_insert)
                    conn.commit()
                return
            print(data_json)
            # Make sure data is present
            if data_json['Response'] != "False":
                # movie not finished
                if time == '-1':
                    sql_insert = """INSERT INTO remaining.movies(Name, watched, Runtime, Gener, Rating, Plot, Year, imdbID) VALUES ("%s", "%s", "%s", "%s", %f, "%s", "%s" ,"%s" )""" % (
                        data_json['Title'].replace('"', ''), Time(data_json['Runtime']), Time(data_json['Runtime']),
                        data_json['Genre'].replace('"', ''),
                        float(data_json['imdbRating']), data_json['Plot'].replace('"', ''), data_json['Year'],
                        data_json['imdbID'])
                else:
                    sql_insert = """INSERT INTO remaining.movies(Name, watched, Runtime, Gener, Rating, Plot, Year, imdbID) VALUES ("%s", "%s", "%s", "%s", %f, "%s", "%s", "%s" )""" % (
                        data_json['Title'].replace('"', ''), str(time), Time(data_json['Runtime']),
                        data_json['Genre'].replace('"', ''),
                        float(data_json['imdbRating']), data_json['Plot'].replace('"', ''), data_json['Year'],
                        data_json['imdbID'])

                print(sql_insert)
                cur.execute(sql_insert)
                conn.commit()
            print("Successful added\n")
        else:
            if time == '-1':
                sql_update_temp = "UPDATE remaining.movies SET watched = Runtime WHERE idMovies = %s" % (
                    results[int(opt)][0])
                cur.execute(sql_update_temp)
                conn.commit()
            else:
                sql_update(conn, cur, results[int(opt)][0], time)
            print("Successful Updates\n")
    except Exception as e:
        print(e)
        print("Error: unable to fetch the data\n")

def tv(conn, cur, params):
    print(params)
    if not params:
        name = raw_input("Enter a Tv name")
        season = raw_input("Enter season and episode")
        time = raw_input("Enter the time stopped at")
        episode = season.split()[1]
        season = season.split()[0]
    else:
        name = params[0]
        season = params[1]
        episode = params[2]
        time = params[3]
    time += ":00"
    sql_search = "SELECT * FROM remaining.tv WHERE Name LIKE '%" + str(name) + "%' "
    try:
        cur.execute(sql_search)
        res = cur.fetchall()
        results = []
        for i in res:
            if i[2] != i[3]:
                results.insert(0, i)
            else:
                results.append(i)
        print("-1)search online")
        for key, res in enumerate(results):
            if res[2] != res[3]:
                print(" " + str(key) + ")" + res[1] + "(" + res[6] + "):" + res[5])
            else:
                print("*" + str(key) + ")" + res[1] + "(" + res[6] + "):" + res[5])
        opt = raw_input("->")

        if opt == '-1':
            data_json = json.load(urllib2.urlopen('http://www.omdbapi.com/?s=%s&type=series' % name))
            if data_json['Response'] == "False":
                opt = raw_input("Could not find the Tv show, add anyways(y/n)\n->")
                if opt == 'n':
                    return
                else:
                    sql_insert = """INSERT INTO remaining.tv(Name, Watched, Season, Episode) VALUES ("%s", "%s", "%s", "%s")""" % (
                    name, time, season, episode)
                    cur.execute(sql_insert)
                    conn.commit()

            for key, temp in enumerate(data_json['Search']):
                print(str(key) + ")" + temp['Title'] + "(" + temp['Year'] + ")")
            selection = raw_input("Select a Tv show\n->")
            data_json = json.load(urllib2.urlopen(
                'http://www.omdbapi.com/?i=%s&type=series' % data_json['Search'][int(selection)]['imdbID']))
            print(data_json['Year'])

            if data_json['Response'] != "False":
                sql_insert = """INSERT INTO remaining.tv(Name, Watched, Season, Episode, Plot, Year, imdbID, Rating) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", %f )""" % (
                    data_json['Title'], time, season, episode, data_json['Plot'].replace('"', ''),
                    data_json['Year'].encode('ascii', 'ignore')[:4] + "-" + data_json['Year'].encode('ascii', 'ignore')[
                                                                            4:], data_json['imdbID'],
                    float(data_json['imdbRating']))
                print(sql_insert)
                cur.execute(sql_insert)
                conn.commit()
            print("Successful added\n")
        else:
            sql_update = "UPDATE remaining.tv SET Watched = '%s',Season = '%s',Episode = '%s' WHERE idtv = %s" % (
                time, season, episode, results[int(opt)][0])
            cur.execute(sql_update)
            conn.commit()
            print("Successful Updates\n")
    except Exception as e:
        print("Error: unable to fetch the data\n")

def update(conn, cur):
    print("Updating...")
    data_json = json.load(urllib2.urlopen('http://api.tvmaze.com/schedule?date=%s' % time.strftime('%Y-%m-%d')))
    for res in data_json:
        if res['show']['externals']['imdb'] != None:
            try:
                sql_search = "SELECT * FROM remaining.tv WHERE imdbID = '%s' " % res['show']['externals']['imdb']
                cur.execute(sql_search)
                result = cur.fetchall()
                if result:
                    print("""A new episode of "%s" is coming tonight""" % result[0][1])
            except Exception as e:
                print("An error occurred during the update")

def check(name, type):
    data_json = {'Response': False}
    try:
        data_json = json.load(
            urllib2.urlopen('http://www.omdbapi.com/?t=%s&type=%s' % (str(name).replace(' ', '%20'), type)))
    except Exception as e:
        print(e)
    if data_json['Response'] == "False":
        return False
    else:
        return True

def search(name, type):
    data_json = json.load(urllib2.urlopen('http://www.omdbapi.com/?s=%s&type=%s' % (name.replace(' ', '%20'), type)))
    if data_json['Response'] == "False":
        return False
    page = 1
    while True:
        data_json = json.load(
            urllib2.urlopen('http://www.omdbapi.com/?s=%s&type=%s&page=%d' % (name.replace(' ', '%20'), type, page)))
        if page != 1:
            print("-1 ) Prv")
        for key, temp in enumerate(data_json['Search']):
            print(' ' + str(key) + ")" + temp['Title'] + "(" + temp['Year'] + ")")
        if page != 100:
            print('10) Next')
            print('11) Cancel')
        selection = raw_input("Select\n->")
        if selection == '-1':
            page -= 1
        elif selection == '10':
            page += 1
        elif selection == '11':
            return False
        else:
            return json.load(urllib2.urlopen(
                'http://www.omdbapi.com/?i=%s&type=%s' % (data_json['Search'][int(selection)]['imdbID'], type)))

def new_movies(conn, cur, params):
    if not params:
        path = raw_input("Enter the path\n->")
    else:
        path = params[0]
    file_save = open(str(path) + '\\new_movies.txt', 'w')
    file_save.close()
    for files in os.listdir(path):
        full_name = files
        files = get_name(files)
        movie_name = ""
        if check(files, 'movie'):
            movie_name = files
        else:
            print("Not found, online?:\t" + files)
            x = raw_input("->")
            # search online
            if x.split()[0] == '-':
                if len(x.split()) == 3:
                    temp_res = " ".join(
                        files.split()[int(x.split()[1]) - 1:int(x.split()[2])])
                elif x == '- 0':
                    temp_res = " ".join(files.split()[0:])
                else:
                    temp_res = " ".join(files.split()[0:int(x.split()[1])])
                print(temp_res)
                temp_res = search(temp_res, 'movie')
                if temp_res == False:
                    print("Couldn't find movie")
                else:
                    #rename
                    movie_name = temp_res['Title']
                    temp_opt = raw_input("rename " + str(full_name) + " to " + movie_name + " (y/n)?")
                    if temp_opt == 'y':
                        if os.path.isdir(path + "\\" + full_name):
                            os.rename(path + "\\" + full_name, path + "\\" + movie_name.replace(':', '').replace(',', '').replace("'", ''))
                            full_name = movie_name
                        else:
                            os.rename(path + "\\" + full_name, path + "\\" + str(movie_name.replace(':','').replace(',','').replace("'",'')) + '.' + full_name.encode('ascii', 'ignore').split('.')[-1])
                            full_name = movie_name + '.' + full_name.encode('ascii', 'ignore').split('.')[-1]
            # skip
            elif x == '-1':
                continue
            # sub directories
            elif x == 's':
                file_save = open(str(path) + '\\new_movies.txt', 'a')
                new_movies(conn, cur, [path + '\\' + full_name])
                temp_file = open(path + '\\' + full_name + '\\new_movies.txt')
                for items in temp_file:
                    file_save.write('\\' + full_name + '\\' + items + '\n')
                temp_file.close()
                os.remove(path + '\\' + full_name + '\\new_movies.txt')
                file_save.close()
                continue
            else:
                try:
                    if len(x.split()) == 2:
                        movie_name = " ".join(
                            files.split()[int(x.split()[0]) - 1:int(x.split()[1])])
                    elif x == '0':
                        movie_name = " ".join(files.split()[0:])
                    else:
                        movie_name = " ".join(files.split()[0:int(x)])
                        # movie check dB
                except Exception as e:
                    continue

                #rename correctly for the file
                temp_opt = raw_input("rename " + full_name + " to " + movie_name + " (y/n)?")
                if temp_opt == 'y':
                    if os.path.isdir(path + "\\" + full_name):
                        os.rename(path + "\\" + full_name, path + "\\" + movie_name)
                        full_name = movie_name
                    else:
                        os.rename(path + "\\" + full_name, path + "\\" + movie_name + '.' + full_name.split('.')[-1])
                        full_name = movie_name + '.' + str(full_name).split('.')[-1]

        if check(movie_name, 'movie'):
            try:
                sql_check = """SELECT * FROM remaining.movies WHERE Name = "%s" """ % str(movie_name.replace('"', ''))
                cur.execute(sql_check)
                results = cur.fetchall()
                if not results:
                    file_save = open(str(path) + '\\new_movies.txt', 'a')
                    file_save.write(full_name + '\n')
                    file_save.close()
            except:
                print("Error check up")
                continue
        else:
            print("Couldn't find movie")
        print(movie_name)

def move(params):
    if not params:
        path = raw_input("Enter source\n->")
        dest = raw_input("Enter destination\n->")
    else:
        path = params[0]
        dest = params[1]
    file = open(path + '\\new_movies.txt')
    for comp, movie in enumerate(file):
        if movie.replace('\n', '') != '':
            print(comp + " out or " + len(file) + " left")
            copy(path + '\\' + movie.replace('\n',''), dest + '\\' + movie.replace('\n',''))

def copy(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        shutil.copy(src, dest)

def sql_insert(data_json, conn, cur, time):
    sql_insert = """INSERT INTO remaining.movies(Name, watched, Runtime, Gener, Rating, Plot, Year, imdbID) VALUES ("%s", "%s", "%s", "%s", %f, "%s", "%s", "%s" )""" % \
                                 (data_json['Title'].replace('"', ''), time, Time(data_json['Runtime']),
                                  data_json['Genre'].replace('"', ''),float(data_json['imdbRating']), data_json['Plot'].replace('"', ''),
                                  data_json['Year'],data_json['imdbID'])
    cur.execute(sql_insert)
    conn.commit()

def sql_search(conn, cur, id):
    sql_search_temp = "SELECT * FROM remaining.movies WHERE imdbID = '%s' " % id
    print(sql_search_temp)
    cur.execute(sql_search_temp)
    res = cur.fetchall()
    if not res:
        return False
    else:
        return True

def sql_update(conn, cur, id, time):
    try:
        int(id)
        sql_update_temp = "UPDATE remaining.movies SET watched = '%s' WHERE idMovies = '%s'" % (time, id)
    except:
        sql_update_temp = "UPDATE remaining.movies SET watched = '%s' WHERE imdbID = '%s'" % (time, id)
    print(sql_update_temp)
    cur.execute(sql_update_temp)
    conn.commit()


def vlc_plugin(conn, cur):
    s = requests.Session()
    s.auth = ('', 'qwerty')# Username is blank, just provide the password
    while True:
        time = 0
        name = ''
        length = 0
        start = False
        while not start:
            try:
                r = s.get('http://localhost:8080/status.json', verify=False).json()
                name = r['information']['category']['meta']['filename']
                length = r['length']
                start = True
            except Exception as e:
                print("not connected")
                print(e)
                sleep(30)
                continue
        while start:
            try:
                r = s.get('http://localhost:8080/status.json', verify=False).json()
                if name != r['information']['category']['meta']['filename']:
                    break
                time = int(r['length'] * r['position'])
                print("playing at " + str(time))
                sleep(30)
            except:
                start = False
        name = get_name(name)
        if check(name, 'movie'):
            data_json = json.load(urllib2.urlopen('http://www.omdbapi.com/?t=%s&type=%s' % (str(name).replace(' ', '%20'), 'movie')))
            print(data_json)
            if data_json['Response'] == "False":
                continue
            if length -time <= 1000:
                x = raw_input("finished(y/n)?\n->")
                if x == 'y':
                    if not sql_search(conn, cur, data_json['imdbID']):
                        sql_insert(data_json, conn, cur, Time(data_json['Runtime']))
                    else:
                        sql_update(conn, cur, data_json['imdbID'], Time(data_json['Runtime']))
                else:
                    if not sql_search(conn, cur, data_json['imdbID']):
                        sql_insert(data_json, conn, cur, str(int(time/60)) + ":" + str(time%60))
                    else:
                        sql_update(conn, cur, data_json['imdbID'], str(int(time/60)) + ":" + str(time%60))

            else:
                if not sql_search(conn, cur, data_json['imdbID']):
                    sql_insert(data_json, conn, cur, str(int(time/60)) + ":" + str(time%60))
                else:
                    sql_update(conn, cur, data_json['imdbID'], str(int(time/60)) + ":" + str(time%60) + ":00")
        else:
            try:
                x = raw_input(name + '\n->')
                if len(x.split()) == 2:
                    movie_name = " ".join(name.split()[int(x.split()[0]) - 1:int(x.split()[1])])
                elif x == '0':
                    movie_name = " ".join(name.split()[0:])
                else:
                    movie_name = " ".join(name.split()[0:int(x)])
                    # movie check dB
            except Exception as e:
                print(e)
                continue
            data_json = search(name, 'movie')
            print(data_json)


print("Connecting...\n")
conn = MySQLdb.connect(host='localhost', user='root', passwd='admin', db='remaining')
#conn = MySQLdb.connect(host='sql6.freemysqlhosting.net', user='sql6113387', passwd='MvMI6xL8Ve', db='sql6113387', port=3306)
cur = conn.cursor()
option = raw_input("Movie(m) or TV Show(t/T) or File(f) or Copy(c)?\n->")
option = option.split()
params = option[1:]
option = option[0]
if option == 'm':
    movies(conn, cur, params)
elif option == 't':
    tv(conn, cur, params)
elif option == 'T':
    update(conn, cur)
    tv(conn, cur, params)
elif option == 'f':
    new_movies(conn, cur, params)
elif option == 'c':
    move(params)
elif option == 'v':
    vlc_plugin(conn, cur)