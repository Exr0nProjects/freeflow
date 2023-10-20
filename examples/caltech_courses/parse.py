from rich import print
from bs4 import BeautifulSoup
from pickle import load, dump
from tqdm import tqdm
import requests
from os.path import join as path_join
from glob import glob

from free_flow import ff, rff, T, dea, mc, ig, ag
# from operator import methodcaller as mc, itemgetter as ig, attrgetter as ag

with open('./options.xml', 'r') as rf:
    s = rf.read()
    soup = BeautifulSoup(s, 'html.parser')

    links = [x['href'] for x in soup.select('a')]
    shortnames = [x[28:-1] for x in links]

#def get_page(url, shortname):
#    path = 'https://catalog.caltech.edu' + url
#    print(path)
#    r = requests.get(path)
#    with open(f'./pages/{shortname}.html', 'w+') as wf:
#        wf.write(r.content.decode('utf-8'))
#
#for url, shortname in zip(tqdm(links), shortnames):
#    get_page(url, shortname)

def inspect(x):
    print(x)
    return x



publish_date = [ mc('select', '.page-published-at'), lambda x: x[0].text[29:-4] ]
courses = [ mc('select', '.course-description2'),
           #rff(T(
           #      mc('select', '.course-description2__title'),
           #      mc('select', '.course-description2__title'),
           #      )
           #),
           rff(T(
                    # [ mc('select', '.course-description2__title'), dea('[0].text.strip()') ],
                    dea(".select('.course-description2__title')[0].text.strip()"),
                    ag('text')
            ))

           #rff(T(   [ mc('select', '.course-description2__title'), ig(0), ag('text'), mc('strip') ],  ag('text')   ) )
       ]

def read_to_soup(path):
    with open(path, 'r') as rf:
        content = rf.read()
    soup = BeautifulSoup(content, 'html.parser')
    return soup


data = lambda fs: ff(
        glob('./pages/*.html'),
    )(read_to_soup, *fs)

x = data(courses)

# x = ff(glob('./pages/*.html'))(read_to_soup, *courses)
# print(x)
flat = [a for y in x for a in y]


print(flat[:10])
#from json import dump
#with open('all_courses.json', 'w') as wf:
#    dump(flat, wf)
