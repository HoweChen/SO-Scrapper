from urllib.request import urlopen
from bs4 import BeautifulSoup

test = 'https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do'
print(test.split('/'))
html = urlopen(test)
bs_obj = BeautifulSoup(html.read(), 'lxml')
print(bs_obj.find('span', {'class': 'vote-count-post high-scored-post'}).get_text())
print(bs_obj.find('div', {'class': 'favoritecount'}).get_text())
answer_html = bs_obj.findAll('div', {'class': 'post-text', 'itemprop': 'text'})[1].get_text()
print(answer_html)
