from urllib.request import urlopen, HTTPError
from bs4 import BeautifulSoup
from multiprocessing import Process
from multiprocessing.dummy import Pool as ThreadPool
from threading import Thread
import queue
import time
import sqlite3
import sys

global url_pool
# url_pool = ["https://stackoverflow.com/questions/tagged/python?page=" + str(i) + "&sort=votes&pagesize=15" for i in
#             range(1, 62266)]
url_pool = ["https://stackoverflow.com/questions/tagged/python?page=" + str(i) + "&sort=votes&pagesize=15" for i in
            range(1, 101)]
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
    votes_temp = bs_obj.findAll('span', {'class': 'vote-count-post high-scored-post'})
    votes = []
    for i in votes_temp[0:2]:
        try:
            vote = i.get_text()
        except Exception as e:
            print(e)
        votes.append(vote)
    # for i in votes:
    #     print(i, end=' ')
    # print('')

    question_id = int(sub_url.split('/')[4])
    question_name = bs_obj.find("a", {"class": "question-hyperlink"}).get_text()
    favorite_count = int(bs_obj.find('div', {'class': 'favoritecount'}).get_text())
    question_vote = int(votes[0])
    answer_vote = int(votes[1]) if len(votes) > 1 else 0
    answer_text = str(bs_obj.findAll('div', {'class': 'post-text', 'itemprop': 'text'})[1].get_text)
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

    try:
        c.execute('insert into SOPython values (?,?,?,?,?,?)',
                  [question_dict.get('question_id'), question_dict.get('question_name'),
                   question_dict.get('favorite_count'),
                   question_dict.get('question_vote'), question_dict.get('answer_vote'),
                   question_dict.get('answer_text')])
        print('---------------------')
        conn.commit()
        print('Insert Successfully')
    except Exception as e:
        print(e)
        print('Insertion Failed')
    conn.close()


def url_fetch_entry():
    global url_pool
    with ThreadPool(processes=10) as pool:
        pool.map(url_fetch, url_pool)
    global sub_url_pool
    for item in sub_url_pool:
        print(item)
    print(len(sub_url_pool))


def sub_url_analysis_entry():
    global sub_url_pool

    with ThreadPool(processes=10) as pool:
        pool.map(sub_url_analysis, sub_url_pool)


def data_store_entry():
    global questions_list_dict
    with ThreadPool(processes=10) as pool:
        pool.map(data_store, questions_list_dict)


def main():
    fetch_thread = Thread(target=url_fetch_entry)
    analysis_thread = Thread(target=sub_url_analysis_entry)
    store_thread = Thread(target=data_store_entry)

    fetch_thread.start()
    fetch_thread.join()
    analysis_thread.start()
    analysis_thread.join()
    store_thread.start()
    store_thread.join()


if __name__ == '__main__':
    main()
