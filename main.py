#!/bin/env python3
import requests
import threading
from bs4 import BeautifulSoup
from queue import Queue
import queue
import os
import time
import timeit
import sys
import random

# main.py [tag] [threads] [threads_for_save]

q_check = Queue()
q_result = Queue()
deep_check = True
mutex = threading.Lock()
global_counter = 0
tag = 'default'
thread_number = 64
thread_number_save = 64
argv_len = len(sys.argv)
if argv_len >= 2:
    tag = sys.argv[1]
if argv_len >= 3:
    thread_number = int(sys.argv[2])
    thread_number_save = thread_number
if argv_len >= 4:
    thread_number_save = int(sys.argv[3])

download_path = 'download'
try:
    #shutil.rmtree('path')
    os.mkdir(download_path)
except:
    pass

#######################################################

def queue_to_list(q):
    l = []
    while q.qsize() > 0:
        l.append(q.get())
    return l

def generate_url(tag, month, day, index):
    if index == 1:
        template = "https://telegra.ph/{0}-{1}-{2}"
        generated_url = template.format(tag, month, day)
    else:
        template = "https://telegra.ph/{0}-{1}-{2}-{3}"
        generated_url = template.format(tag, month, day, index)
    return generated_url

def thread_worker():
    global global_counter
    status = True
    leave = False
    while True:
        try:
            url, month, day, index = q_check.get(False)
            if not status:
                mutex.acquire()
                global_counter -= 1
                mutex.release()
                status = True
            response = requests.get(url)
            if response.ok:
                # check images
                soup = BeautifulSoup(response.text, 'html.parser')
                imgs = soup.findAll("img")
                image_list = []
                year = soup.find("time")
                year = year['datetime'].split('-')[0]
                for img in imgs:
                    if 'http' in img['src']:
                        q_result.put((img['src'],year,month,day,index))
                    else:
                        q_result.put(('https://telegra.ph'+img['src'],year,month,day,index))
                # check page
                if deep_check:
                    index += 1
                    next_url = generate_url(tag,month,day,index)
                    q_check.put((next_url,month,day,index))
        except: #queue.Empty:
            mutex.acquire()
            if(status):
                global_counter += 1
                status = False
            if global_counter == thread_number:
                leave = True
            mutex.release()
            if leave: 
                break
            time.sleep(random.uniform(0, 1))
  
def thread_saver():
    template = "{0}/{1}-{2}-{3}-{4}-{5}.{6}"
    while True:
        try:
            url,year,month,day,index = q_to_save.get(False)
            try:
                response = requests.get(url)
                if response.ok:
                    last = url.split('/')
                    with open(template.format(download_path,tag,year,month,day,index,last[-1]), "wb") as file:
                        file.write(response.content)
            except:
                pass
        except queue.Empty:
                break

#######################################################

for month in range(1,13):
    for day in range(1,32):
        str_month = f'0{month}' if month < 10 else str(month)
        str_day = f'0{day}' if day<10 else str(day)
        new_url = generate_url(tag, str_month, str_day, 1)
        q_check.put((new_url,month,day,1))

tic = time.time()
print('Start searching')
threads_list = list()
for x in range(thread_number):
    thread = threading.Thread(target=thread_worker)
    thread.start()
    threads_list.append(thread)
for thread in threads_list:
    thread.join()
print('End searching')
toc = time.time()
print('Searching time: '+str(round(toc - tic,1)) + ' seconds')

buffer_list = queue_to_list(q_result)
buffer_list = list(set(buffer_list))
q_to_save = Queue()
for item in buffer_list:
    q_to_save.put(item)
print('Number of images: '+str(len(buffer_list)))
if(len(buffer_list)>0):
    download_path = download_path + '/' + tag + '/'
    try:
        os.mkdir(download_path)
    except:
        pass
    tic = time.time()
    print('Start download')
    threads_list = list()
    for x in range(thread_number_save):
        thread = threading.Thread(target=thread_saver)
        thread.start()
        threads_list.append(thread)
    for thread in threads_list:
        thread.join()
    print('End download')
    toc = time.time()
    print('Download time: '+str(round(toc - tic,1)) + ' seconds')
else:
    print('Nothing to download')
