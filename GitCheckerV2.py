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
        self.GitPaths       =   ['/.git/','/.svn/']
        self.gitFiles       =   ['HEAD', 'index', 'config', 'description', 'FETCH_HEAD', 'info/exclude', 'packed-refs', 'logs/refs/heads/master', 'logs/refs/remotes/origin/HEAD', 'logs/refs/remotes/origin/master', 'refs/heads/master']
        self.Urls           =   []
        self.Found          =   []
        self.Forbidden      =   []
        self.NotFound       =   []
        self.OkResponse     =   []
        self.Errors         =   []
        self.UrlCounter     =   0
        self.ScanCounter    =   1
        self.NumberOfTreads =   Threads
        self.Printing       =   Lock()
        #   Load URLS From File
        print ("[!] Loading File {}.\r".format(self.UrlFile),end='')
        FileHandler = open(self.UrlFile, 'r')
        for URL in FileHandler:
            URL = URL.strip()
            if URL[-1]=='/':
                self.UrlList.put(URL+'.git/')
                self.UrlCounter += 1
            else:
                self.UrlList.put(URL+'/.git/')
                self.UrlCounter += 1
        print ('[!] Loaded {} URLs From {}'.format(self.UrlCounter,self.UrlFile))

    def Checker(self):
        #for Url in self.UrlList:
        while True:
            Url = self.UrlList.get()
            try:
                self.Printing.acquire()
                print ('\r[!] [{}/{}] Scanning {}                                       '.format(self.ScanCounter, self.UrlCounter, Url),end='')
                self.Printing.release()
                Handler = Req.head(Url)
                self.ScanCounter += 1
                if Handler.status_code == 200:
                    #self.Printing.acquire()
                    #print ("\r[-] {} Respoded 200 OK.".format(Url),end='\n')
                    self.OkResponse.append(Url)
                    #self.Printing.release()
                elif Handler.status_code == 404:
                    self.NotFound.append(Url)
                elif Handler.status_code == 403 or Handler.status_code == 401:
                    self.Forbidden.append(Url)
                else:
                    self.Errors.append(Url)
                if (Handler.status_code <= 404):
                    try:
                        AllOk = False
                        for FileName in self.gitFiles:
                            Handler = Req.head(Url+FileName)
                            if (Handler.status_code == 200 and ('Content-Type' not in Handler or ('text/html' not in Handler.headers['Content-Type'].lower()))):
                                self.OkResponse.append(Url+FileName)
                                AllOk = True
                                #self.Printing.acquire()
                                #print ("\r    [*] {} Respoded 200 OK.".format(Url+FileName))
                                #self.Printing.release()
                        if AllOk:
                            self.Printing.acquire()
                            print ("\r[*] Check {}                                                                    ".format(Url), end='\n')
                            self.Printing.release()
                    except:
                        self.UrlList.task_done()
                self.UrlList.task_done()
            except:
                self.UrlList.task_done()
                self.Errors.append(Url)
    def Check(self):
        for thread in range(self.NumberOfTreads):
            Worker  =   Thread(target=self.Checker, args=())
            Worker.setDaemon(True)
            Worker.start()
        self.UrlList.join()
        
    def Results(self,):
        if self.NotFound:
            print ("\n\n\n[-] Not Found Targets :")
            for Target in self.NotFound:
                print ('\t[*] {} .'.format(Target))
        if self.Forbidden:
            print ("\n\n\n[-] Forbidden Targets :")
            for Target in self.Forbidden:
                print ('\t[*] {} .'.format(Target))
        if self.OkResponse:
            print ("\n\n\n[-] Found Targets :                                                    ")
            for Target in self.OkResponse:
                print ('\t[*] {} .'.format(Target))

        print ("\n\n[-] Scan Done.")
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file", help='Imput File Name containing the URL List')
    parser.add_argument("-t","--thread", help='Number of threads to run Default : 3', default=3, type=int)
    arg = parser.parse_args()
    try:
        checker = GitRepoChecker(arg.file)
        checker.Check()
        checker.Results()
    except KeyboardInterrupt:
        print ("\r[~] Detected CTRL-C                                                                                                       ")
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
