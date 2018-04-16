from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup
from multiprocessing import Process
from multiprocessing.dummy import Pool as ThreadPool
from threading import Thread
import queue
import time
import sqlite3

global url_pool
# url_pool = ["https://stackoverflow.com/questions/tagged/python?page=" + str(i) + "&sort=votes&pagesize=15" for i in
#             range(1, 62266)]
url_pool = ["https://stackoverflow.com/questions/tagged/python?page=" + str(i) + "&sort=votes&pagesize=15" for i in
            range(1, 2)]
global sub_url_pool
sub_url_pool = []
global questions_list_dict
questions_list_dict = []


def url_fetch(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
        html = None  # should set this as None, or when it comes to error, the local variable 'html' referenced
        # before assignment

    if html is None:
        print("URL is not found")
    else:
        try:
            bs_obj = BeautifulSoup(html.read(), "lxml")
        except AttributeError as e:
            print(e)
            return None
        # print(bs_obj)  # till now is okay to get the bs_obj
    question_list = bs_obj.findAll("a", {"class": "question-hyperlink"})

    global sub_url_pool
    for question in question_list:
        sub_url_pool.append('https://stackoverflow.com' + str(question.attrs.get('href')))


def sub_url_analysis(sub_url):
    global questions_list_dict
    try:
        html = urlopen(sub_url)
    except HTTPError as e:
        print(e)
        html = None

    if html is None:
        return
    else:
        try:
            bs_obj = BeautifulSoup(html.read(), "lxml")
        except AttributeError as e:
            print(e)
            return None
    votes = bs_obj.findAll('span', {'class': 'vote-count-post high-scored-post'})

    question_id = int(sub_url.split('/')[4])
    question_name = bs_obj.find("a", {"class": "question-hyperlink"}).get_text()
    favorite_count = int(bs_obj.find('div', {'class': 'favoritecount'}).get_text())
    question_vote = int(votes[0].get_text())
    if len(votes) >= 1:
        answer_vote = votes[1].get_text()
    else:
        answer_vote = None
    answer_text = bs_obj.findAll('div', {'class': 'post-text', 'itemprop': 'text'})[1].get_text
    return_dict = {
        'question_id': question_id,
        'question_name': question_name,
        'answer_vote': answer_vote,
        'favorite_count': favorite_count,
        'question_vote': question_vote,
        'answer_text': answer_text
    }
    questions_list_dict.append(return_dict)


def data_store(question_dict):
    conn = sqlite3.connect('SO-Python.db')
    c = conn.cursor()
    c.execute('insert into SOPython values (?,?,?)',
              [question_dict['question_id'], question_dict['question_name'], question_dict['favorite_count'],
               question_dict['question_vote'], question_dict['answer_vote'], question_dict['answer_text']])
    conn.commit()
    print('Insert Successfully')
    conn.close()


def url_fetch_entry():
    global url_pool
    with ThreadPool(processes=5) as pool:
        pool.map(url_fetch, url_pool)
    global sub_url_pool
    for item in sub_url_pool:
        print(item)


def sub_url_analysis_entry():
    global sub_url_pool
    if not sub_url_pool:
        return
    else:
        with ThreadPool(processes=10) as pool:
            pool.map(sub_url_analysis, sub_url_pool)


def data_store_entry():
    global questions_list_dict
    if questions_list_dict:
        with ThreadPool(processes=10) as pool:
            pool.map(data_store, questions_list_dict)


def main():
    # url_fetch_process = Process(target=url_fetch_entry)
    # sub_url_analysis_process = Process(target=sub_url_analysis_entry)
    # data_store_process = Process(target=data_store_entry)
    # url_fetch_process.start()
    # sub_url_analysis_process.start()
    # data_store_process.start()
    # url_fetch_process.join()
    # sub_url_analysis_process.join()
    # data_store_process.join()
    # url_fetch_entry()
    # sub_url_analysis_entry()
    url_fetch_entry()
    sub_url_analysis_entry()
    data_store_entry()


if __name__ == '__main__':
    main()
