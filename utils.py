import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

KEYWORD_CONTEXT = ['꿀강', '열정', '도움', '유익']
load_dotenv()
key = os.environ["OPENAI_API_KEY"]

# 
def get_embedding(text, model):
    load_dotenv()
    client = OpenAI(api_key=key)
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

# 주어진 text를 임베딩해주는 def
# 매개변수 : text(키워드), model(임베딩 해줄 모델)
# 출력 : 임베딩한 결과물 출력
def get_embeddings(text, model):
    client = OpenAI(api_key=key)
    response = client.embeddings.create(
        input=text,
        model=model
    )
    output = []
    for i in range(len(response.data)):
        output.append(response.data[i].embedding)
    return output

# 코사인 유사도를 구해주는 함수
# 매개변수 a, b
# 출력 : a와 b에 대한 유사도를 출력 -1 ~ 1
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# query(키워드)와 context(리뷰)임베딩 한것의 유사도를 구하고 높은것부터 정리
# 매개변수 : query임베딩한거, context임베딩한거
# 출력 : 정렬한 index, 유사도
def get_most_relevant_indices(query_embedding, context_embeddings):
    query = np.array(query_embedding)
    context = np.array(context_embeddings)
    
    similarities = np.array([cosine_similarity(query, ctx) for ctx in context])
    
    sorted_indices = np.argsort(similarities)[::-1].tolist()
    
    return sorted_indices, similarities

def extract_keywords(review_text):
    keywords = []
    
    for word in review_text.split():
        if any(keyword in word for keyword in KEYWORD_CONTEXT):
            keywords.append(word)
    return keywords

# LLM을 불러오는 모듈
# 매개변수 : 프롬프트, temperature, 모델
# llm 결과문장
def call_openai(prompt, temperature, model):
    client = OpenAI(api_key=key)
    completion = client.chat.completions.create(
        model = model,
        messages = [{'role': 'user', 'content': prompt}],
        temperature = temperature
    )
    
    return completion.choices[0].message.content


            
