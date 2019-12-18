#!/usr/bin/env python3
import requests as Req
from queue import Queue
from threading import Thread,Lock
import argparse
import sys

class GitRepoChecker:
    def __init__(self, UrlFile = 'test.lst', Threads = 3):
        #   Local Variables
        self.UrlFile        =   UrlFile
        self.UrlList        =   Queue(maxsize=0)
        self.GitPaths       =   ['/.svn/', 'wc.db']
        self.gitFiles       =   ['entries']
        self.Urls           =   []
        self.Found          =   []
        self.Forbidden      =   []
        self.NotFound       =   []
        self.OkResponse     =   []
        self.Errors         =   []
        self.UrlCounter     =   0
        self.NumberOfTreads =   Threads
        self.Printing       =   Lock()
        #   Load URLS From File
        print ("[!] Loading File {}.\r".format(self.UrlFile),end='')
        FileHandler = open(self.UrlFile, 'r')
        for URL in FileHandler:
            URL = URL.strip()
            if URL[-1]=='/':
                self.UrlList.put(URL+'.svn/')
                self.UrlCounter += 1
            else:
                self.UrlList.put(URL+'/.svn/')
                self.UrlCounter += 1
        print ('[!] Loaded {} URLs From {}'.format(self.UrlCounter,self.UrlFile))

    def Checker(self):
        #for Url in self.UrlList:
        while True:
            Url = self.UrlList.get()
            try:
                self.Printing.acquire()
                print ('[!] Scanning {}'.format(Url),end='\r')
                Handler = Req.head(Url)
                if Handler.status_code == 200:
                    print ("\r[-] {} Respoded 200 OK.".format(Url))
                    self.OkResponse.append(Url)
                elif Handler.status_code == 404:
                    self.NotFound.append(Url)
                elif Handler.status_code == 403:
                    self.Forbidden.append(Url)
                else:
                    self.Errors.append(Url)
                if (Handler.status_code != 404):
                    try:
                        for FileName in self.gitFiles:
                            Handler = Req.head(Url+FileName)
                            if Handler.status_code == 200:
                                print ("\t[*] {} Respoded 200 OK.".format(Url+FileName))
                    except:
                        self.UrlList.task_done()
                self.Pringting.release()
                self.UrlList.task_done()
            except:
                self.UrlList.task_done()
                self.Errors.append(Url)
                self.Printing.release()
    def Check(self):
        for thread in range(self.NumberOfTreads):
            Worker  =   Thread(target=self.Checker, args=())
            Worker.setDaemon(True)
            Worker.start()
        self.UrlList.join()
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file", help='Imput File Name containing the URL List')
    parser.add_argument("-t","--thread", help='Number of threads to run Default : 3', default=3, type=int)
    arg = parser.parse_args()
    try:
        checker = GitRepoChecker(arg.file)
        checker.Check()
    except KeyboardInterrupt:
        sys.exit()

#a = open('Amass-httprobe', 'r')

#for line in a:
#uris.append(line.strip())
#
#for line in uris:
#if line[-1]=='/':
#urls.append(line+'.git/')
#else:
#urls.append(line+'/.git/')
#
#for url in urls:
#r = req.get(url)
#print("[!] Connecting {} Retuened {}".format(url, r.status_code))
