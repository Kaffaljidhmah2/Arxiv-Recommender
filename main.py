from arxiv_util import get_today_paper, get_url
from llm import get_chatGPT_response
import time
import pickle
from research_topic import RESEARCH_TOPIC_DICT
from filter_util import MY_AUTHOR_LIST
from datetime import date
from collections import defaultdict
from mail import SendEmail

buffer=[]
def my_print(s):
    buffer.append(s)

def my_format(arxiv_obj, summary): 
    return '\t'.join([get_url(arxiv_obj), arxiv_obj.title, '(' + ( ', '.join(arxiv_obj.author)) + ')', '\n' + summary])

CATEGORY_LIST = ['cs.LG']
IS_SAVE = True
today=date.today()

papers_dict = get_today_paper(cate_list=CATEGORY_LIST, is_save=IS_SAVE)
my_print(f"we have {len(papers_dict)} papers today")
response_dict = get_chatGPT_response(papers_dict, is_save=IS_SAVE)

MY_AUTHOR_LIST_lower = [_.lower() for _ in MY_AUTHOR_LIST]
default_key=list(response_dict.keys())[0]
for idx, arxiv_obj in papers_dict.items():
    contains_author = False
    for aut in arxiv_obj.author:
        if aut.lower() in MY_AUTHOR_LIST_lower:
            contains_author= True
            break
    if contains_author:
        summary = response_dict[default_key][idx]['summarization']
        my_print(my_format(arxiv_obj, summary))
        my_print('')

my_print("==========================")
            


recommended_papers = defaultdict(list)
for key in RESEARCH_TOPIC_DICT.keys():
    for idx in papers_dict.keys():
        arxiv_obj = papers_dict[idx]
        response = response_dict[key][idx]
        if response is not None and  response['score'] in ['3', 3]:
            recommended_papers[key].append([arxiv_obj, response['summarization']])

for key in recommended_papers.keys():
    my_print(key)
    for p in recommended_papers[key]:
        my_print(my_format(*p))
        my_print('')
    my_print("----------------")
    

#SendEmail('\n'.join(buffer))
print('\n'.join(buffer))