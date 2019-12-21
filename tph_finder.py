import requests
import threading
from bs4 import BeautifulSoup
from queue import Queue
import queue
import os
import time
import timeit
import sys

# tph_finder.py [tag] [threads] [threads_for_save]

q_check = Queue()
q_result = Queue()
deep_check = True
mutex = threading.Lock()
global_counter = 0
tag = 'default'
thread_number = 64
thread_number_save = 64
argv_len = len(sys.argv)
print(argv_len)
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

def generate_url(url,index):
    result = ''
    if(index == 2):
        result = url + '-' + str(index)
    else:
        url = url[:-len(str(index-1))]
        result = url+str(index)
    return result

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
            #print(response.status_code)
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
                    next_url = generate_url(url,index)
                    q_check.put((next_url,month,day,index))
        except queue.Empty:
            mutex.acquire()
            if(status):
                global_counter += 1
            if global_counter == thread_number:
                leave = True
            mutex.release()
            if leave: break
            status = False
            time.sleep(1)
  
def thread_saver():
    while True:
        try:
            url,year,month,day,index = q_to_save.get(False)
            try:
                response = requests.get(url)
                if response.ok:
                    last = url.split('/')
                    with open(download_path+'/'+str(tag)+'-'+str(year)+'-'+str(month)+'-'+str(day)+'-'+str(index)+'.'+last[-1], "wb") as file:
                        file.write(response.content)
            except:
                pass
        except queue.Empty:
            break

#######################################################

for month in range(1,13):
    for day in range(1,32):
        generated_url = 'https://telegra.ph/'+tag+'-'+('0'+str(month) if month<10 else str(month))+'-'+('0'+str(day) if day<10 else str(day))
        q_check.put((generated_url,month,day,1))

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
print('Searching time: '+str(toc - tic))

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
    print('Start saving')
    threads_list = list()
    for x in range(thread_number_save):
        thread = threading.Thread(target=thread_saver)
        thread.start()
        threads_list.append(thread)
    for thread in threads_list:
        thread.join()
    print('End saving')
    toc = time.time()
    print('Download time: '+str(toc - tic))
else:
    print('Nothing to download')