#!/usr/bin/python3
# -*- coding:utf-8 -*-

import urllib
import requests,re,time
import datetime
import json
import threading
import telebot
from pysqlite3 import dbapi2 as sqlite

class GitMonitor:
    def __init__(self, telebot):
        self.total_count = 0
        self.db_path = "./monitor.db"
        self._running = True
        self.telebot = telebot
        
    def firstrun(self):
        # Each time the program restart
        self.getAllRepository()

    def run(self):
        self._running = True
        while self._running:
            print("Monitoring cve...")
            self.getRepository()
            time.sleep(300)

    def stop(self):
        print("Stop monitor cve...")
        self._running = False

    def getAllRepository(self):
        year = datetime.datetime.now().year
        api = "https://api.github.com/search/repositories?q=CVE-{}&sort=updated&per_page=50&page=1".format(year)
        req = requests.get(api).text
        data = json.loads(req)
        total_count = data['total_count']
        self.total_count = total_count
        incomplete_results = data['incomplete_results']
        items = data['items']

        fetched_result = 0
        pageid = 1
        pagesize = 50
        content_size = pagesize
        while fetched_result < total_count:
            print(fetched_result,pagesize,pageid)
            api = "https://api.github.com/search/repositories?q=CVE-{}&sort=updated&per_page={}&page={}".format(year,pagesize,pageid)
            fetched_result = fetched_result + pagesize
            pageid = pageid + 1

            req = requests.get(api).text
            data = json.loads(req)
            items = data['items']

            conn = sqlite.connect(self.db_path)
            cursor = conn.cursor()

            if fetched_result > total_count:
                content_size = total_count + pagesize - fetched_result

            for index in range(content_size):
                id = items[index]['id']
                name = items[index]['name']
                full_name = items[index]['full_name']
                size = items[index]['size']
                stargazers_count = items[index]['stargazers_count']
                watchers_count = items[index]['watchers_count']
                timestamp = items[index]['created_at']
                if size > 0 or watchers_count > 0 or stargazers_count > 0:
                    print(items[index]['full_name'],items[index]['size'])
                    try:
                        result = cursor.execute("INSERT INTO gitrepo VALUES (?,?,?,?,?,?,?)",(id, name, full_name, size, stargazers_count, watchers_count, timestamp))
                    except sqlite.IntegrityError as msg:
                        pass
                    except Exception as msg:
                        pass

            conn.commit()
            cursor.close()
            conn.close()
            time.sleep(5)
        self.telebot.push("[*] Git CVE Monitor Initialized")

    def getRepository(self):
        year = datetime.datetime.now().year
        pageid = 1
        pagesize = 10
        api = "https://api.github.com/search/repositories?q=CVE-{}&sort=updated&per_page={}&page={}".format(year,pagesize,pageid)
        req = requests.get(api).text
        data = json.loads(req)
        total_count = data['total_count']
        incomplete_results = data['incomplete_results']
        items = data['items']
        self.telebot.push("[*] Git CVE Monitor: " + str(total_count))
        content_size = pagesize
        if pagesize > total_count:
            content_size = total_count
        if total_count > self.total_count :
            content_size = total_count - self.total_count
            if content_size > pagesize:
                # should be real strange, this is not a fix
                content_size = pagesize
            self.total_count = total_count
            conn = sqlite.connect(self.db_path)
            cursor = conn.cursor()
            for index in range(content_size):
                id = items[index]['id']
                name = items[index]['name']
                full_name = items[index]['full_name']
                size = items[index]['size']
                stargazers_count = items[index]['stargazers_count']
                watchers_count = items[index]['watchers_count']
                timestamp = items[index]['created_at']
                if size > 0 or watchers_count > 0 or stargazers_count > 0:
                    print(items[index]['full_name'],items[index]['size'])
                    self.telebot.push("New CVE Repo comming: https://github.com/{}  Size: {}".format(items[index]['full_name'],items[index]['size']))
                    try:
                        result = cursor.execute("INSERT INTO gitrepo VALUES (?,?,?,?,?,?,?)",(id, name, full_name, size, stargazers_count, watchers_count, timestamp))
                    except sqlite.IntegrityError as msg:
                        pass
                    except Exception as msg:
                        pass
                conn.commit()
            cursor.close()
            conn.close()

class Telebot:

    def __init__(self):
        self.userid = "Telegram ID"
        self.bot = telebot.TeleBot("TOKEN")
        self.initGit = True
        self.gitmonitor = GitMonitor(self)
        
        
        # GitMonitor
        @self.bot.message_handler(commands=['startGit'])
        def handle_start_help(message):
            t = threading.Thread(target=self.gitmonitor.run,args=())
            t.start()
            self.bot.reply_to(message, "GitMonitor Started")
            
        @self.bot.message_handler(commands=['stopGit'])
        def handle_start_help(message):
            self.gitmonitor.stop()
            self.bot.reply_to(message, "GitMonitor Stopped")
        
        def handle_messages(messages):
            for message in messages:
                pass
                # self.bot.reply_to(message, "Hi")

        self.bot.set_update_listener(handle_messages)

    def push(self,text):
        self.bot.send_message(self.userid,text)

    def run(self):
        if self.initGit:
            print("Initing git")
            self.gitmonitor.firstrun()
        
        self.bot.polling()        
        

if __name__ == '__main__':
    Telebot().run()
