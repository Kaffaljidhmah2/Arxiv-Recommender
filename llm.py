from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage  
import json
import time 
import os
import pickle
from datetime import date
from research_topic import RESEARCH_TOPIC_DICT

class OpenAIChat:
    model = {
        "gpt-3.5": ChatOpenAI(openai_api_key=open('.openai_api_key').read().strip(), model_name='gpt-3.5-turbo'),
        "gpt-4": ChatOpenAI(openai_api_key=open('.openai_api_key').read().strip(), model_name='gpt-4'),
    }
 
    @classmethod
    def chat(cls, request, model_name):
        response = cls.model[model_name]([HumanMessage(content=request)]).content
        json_response = json.loads(response)
        return json_response

def get_summary_score(arxiv_obj, topic, cascade=False):
    meta_prompt = """
    You are a professional research assistant. Please read the title and the abstract of the paper I provide you below and summarize it into one sentence as concise as possible. Next, please judge if the paper is relevant to my current research topic.

    ** Score Scale
    Please use the following score scale:
    - 0 (most irrelevant, completely different directions)
    - 1 (somewhat relevant, there is only one keyword match)
    - 2 (medium, there are merely keyword matches, but the topic deviates a bit from the my research topic)
    - 3 (a must read, the paper is exactly working on the similar direction as my research topic). 

    ** My current research topic: 
    {topic}

    ** Arxiv paper title: 
    {title}

    ** Arxiv paper abstract: 
    {abstract}

    ** Response
    Please respond in the following format, and make sure it is parsable by JSON.
    {{
        "thoughts": "", # put your thinking step-by-step here.
        "summarization": "", # summarization of the contribution of the paper in one sentence.
        "score": "" # 0, 1, 2, 3.
    }}
    """

    models = ["gpt-3.5", "gpt-4"] if cascade else ["gpt-3.5"]
    for model_name in models:
        result = OpenAIChat.chat(meta_prompt.format(topic=topic, title=arxiv_obj.title, abstract=arxiv_obj.abstract), model_name=model_name) 
        score = result.get('score', None)
        if score is not None and score in ['0', '1', 0, 1]:
            return result
        
    return result

# Note: as the candidate papers are all about artificial intelligence, the papers may look relevant to my research topic at a first glance. However, you should try to discriminate if indeed there will be a significant overlapping with my research topic, and use high scores sparingly. 

def get_chatGPT_response(papers_dict, is_save=False, verbose=True):
    if is_save:
        today=date.today()
        if os.path.exists(f'response_{today}.pkl'): 
            response_dict = pickle.load(open(f'response_{today}.pkl', 'rb'))
            return response_dict


    response_dict={}
    for key, research_topic in RESEARCH_TOPIC_DICT.items():
        response_list = {}
        for index, arxiv_obj in papers_dict.items():
            try:
                chatGPT_response = get_summary_score(arxiv_obj, research_topic)
                if verbose:
                    print(chatGPT_response)
                response_list[index] = chatGPT_response
                time.sleep(1)
            except Exception as ex:
                print("Error occured", ex)
                response_list[index] = None
        assert len(papers_dict) == len(response_list)
        response_dict[key] = response_list

    if is_save:
        today=date.today()
        with open(f'response_{today}.pkl', 'wb') as f:
            pickle.dump(response_dict, f)
    return response_dict
