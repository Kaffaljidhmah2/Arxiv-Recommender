import re
import requests
from dataclasses import dataclass
from typing import List, Optional
import time
import os
import pickle
from datetime import date

@dataclass
class ArxivPaper:
    arxiv_id: str
    title: str
    author: List[str]
    subject: List[str]
    comment: List[str]
    abstract: Optional[str]



def arxiv_parser(txt):
    """
        parse arxiv format, e.g., https://export.arxiv.org/abs/2110.14416?fmt=txt
    """
    title, authors, abstract = re.findall('Title: (.*?)\nAuthors: (.*?)\nCategories.*\\\\\n(.*?)\n\\\\', txt, re.DOTALL)[0]
    title = title.replace('\n', ' ')
    authors = authors.replace('\n', ' ')
    abstract = abstract.replace('\n', ' ')
    return title, authors, abstract

def decode_date(arxiv_raw):
    delim = r'(?:.*?)'
    pat1 = r'#item(\d*?)">'
    pat2 = r'([A-Za-z]*, \d* [A-Za-z]* \d*)<'
    pat = delim.join([pat1,pat2])
    return re.findall(pat, arxiv_raw, re.DOTALL)

def decode_arxiv_webpage(arxiv_raw):
    """
        convert webpage (html) or recent publications into a list of arxiv entries.
    """
    pat_coarse = r'<dt><a name="item(\d*?)">\[(?:\d*?)\]</a>(.*?)</dd>'
    delim = r'(?:.*?)'
    #pat_arxiv_id = r'<a href="https://arxiv.org/abs/(\d\d\d\d\.\d\d\d\d\d)"'  ## if we manually download
    pat_arxiv_id = r'<a href="/abs/(\d\d\d\d\.\d\d\d\d\d)"' ## if we crawl from web
    pat_title = r'Title:</span>(.*?)</div>'
    pat_author_raw = r'<span class="descriptor">Authors:</span>(.*?)</div>'
    pat_subject_raw = r'<span class="descriptor">Subjects:</span>(.*?)</div>'
    pat_comment = r'<span class="descriptor">Comments:</span>(.*?)</div>'
    pat_comment_ = re.compile(pat_comment, re.DOTALL)
    pat_author = r'<a href="(?:.*?)">(.*?)</a>'
    pat_author_ = re.compile(pat_author, re.DOTALL)
    pat_subject = r'([\sA-Za-z]*?\([A-Za-z]*?\.[A-Za-z]*?\))'
    pat_subject_ = re.compile(pat_subject, re.DOTALL)
    pat = delim.join([pat_arxiv_id,pat_title,pat_author_raw,pat_subject_raw])
    pat_ = re.compile(pat, re.DOTALL)
    res = re.findall(pat_coarse, arxiv_raw, re.DOTALL)
    for indx, raw in res:
        ret = pat_.findall(raw)
        assert len(ret)==1, raw
        arxiv_id, title, author_raw, subject_raw = ret[0]
        author = pat_author_.findall(author_raw)
        comment = pat_comment_.findall(raw)
        subject = pat_subject_.findall(subject_raw)
        paper_obj = ArxivPaper(arxiv_id, title, author, subject, comment, None)
        yield (indx, paper_obj)

def get_abstract(arxiv_obj : ArxivPaper):
    ptext = requests.get(f'https://export.arxiv.org/abs/{arxiv_obj.arxiv_id}?fmt=txt').text
    title, authors, abstract = arxiv_parser(ptext)
    arxiv_obj.abstract= abstract
    return arxiv_obj

def get_today_paper(cate_list=['cs.LG', 'cs.CL', 'cs.AI'], is_save=False, verbose=True):
    if is_save:
        today=date.today()
        if os.path.exists(f'papers_{today}.pkl'):
            papers_dict = pickle.load(open(f'papers_{today}.pkl', 'rb'))
            return papers_dict

    paper_dict = {}
    for cate in cate_list:
        url = f"https://arxiv.org/list/{cate}/pastweek?skip=0&show=2000"
        print(f"fetching {url}")

        retry_count = 0
        while retry_count <= 5:
            try:
                arxiv_raw = requests.get(url).text
                time.sleep(20) # TODO
                break
            except:
                retry_count += 1

        papers = list(decode_arxiv_webpage(arxiv_raw))
        today_max = int(decode_date(arxiv_raw)[0][0]) - 1 ## decode_date returns a list of (start index, date) for previous dates.
        papers_today = papers[:today_max]
        for _, obj in papers_today:
            paper_dict[obj.arxiv_id] = obj

    for index, arxiv_obj in paper_dict.items():
        retry_count = 0
        while retry_count <= 5:
            try:
                ret = get_abstract(arxiv_obj)
                time.sleep(1)
                break
            except:
                retry_count += 1
        if verbose:
            print(index, ret)
    if is_save:
        today=date.today()
        with open(f'papers_{today}.pkl', 'wb') as f:
            pickle.dump(paper_dict, f)
    return paper_dict

def get_url(arxivObj):
    return 'https://www.arxiv.org/abs/'+arxivObj.arxiv_id
