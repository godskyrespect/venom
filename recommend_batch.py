import os
import urllib
import certifi
import numpy as np
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

from utils import get_embeddings, cosine_similarity, call_openai

# 1. 표시할 키워드 선정
COMBINATIONS = ['열정적인 교수님', '유익한 수업', '도움되는 수업', '꿀강', '얻어가는 수업']
KEYWORDS_CONTEXT = ['열정', '유익', '도움', '꿀강', '얻어']

# 2. 키워드가 포함된 리뷰 추출
def extract_keywords(review_text):
    keywords = []

    for word in review_text.split():
        if any(keyword in word for keyword in KEYWORDS_CONTEXT):
            keywords.append(word)
    return keywords

# 3. MongoDB에서 학과 리뷰 데이터 불러오기
def fetch_subject_info():
    load_dotenv()
    username = urllib.parse.quote_plus(os.environ['MONGODB_USERNAME'])
    password = urllib.parse.quote_plus(os.environ['MONGODB_PASSWORD'])
    uri = f"mongodb+srv://{username}:{password}@cluster0.7pdc1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    db = client.highschool_db
    collections = db.classes_reviews

    classes_info = list(collections.find({}))
    print("^^ : MongoDB에서 수업 정보를 불러오는데 성공했습니다.")
    return classes_info

# 4. 리뷰에서 추출한 키워드를 바탕으로 수업에 포함된 키워드로 묶기
def create_candidates(class_infos):
    candidates = []
    for idx, info in enumerate(class_infos):
        for reviews in info['reviews']:
            review_text = reviews.get('review_text')
            cls = reviews.get('class_name')
            
            keywords = extract_keywords(review_text)
            if keywords == []:
                continue
            
            candidates.append(
                {
                    "subject": info['subject_name'],
                    "class": cls,
                    "keywords": " ".join([cls] + keywords)
                }
            )
    print("^^ : 키워드를 바탕으로 수업과 관련된 키워드를 합치는데 성공했습니다. .")
    return candidates


# 5. 키워드와 수업과 연관지은 키워드 임베딩, 유사도 측정
def create_recommendations(query, candidates):
    contexts = [cand["keywords"] for cand in candidates]
    query_embedding = get_embeddings([query], model='text-embedding-3-large')[0]
    context_embeddings = get_embeddings(contexts, model='text-embedding-3-large')
    similarities = [cosine_similarity(query_embedding, context_embedding) for context_embedding in context_embeddings]
    
    sorted_indices = np.argsort(similarities)[::-1]
    recommendations = [candidates[i] for i in sorted_indices]
    print("^^ : 기존 데이터와 키워드를 벡터로 임베딩에 성공했습니다.")
    
    recommendations_filtered = []
    unique_menus = set()
    for rec in recommendations:
        class_name = rec['class']
        if class_name not in unique_menus:
                rec['class'] = class_name
                recommendations_filtered.append(rec)
                unique_menus.add(class_name)
                
    final_recommendations = {}
    for rec in recommendations_filtered:
        class_name = rec['class']
        if rec['subject'] not in final_recommendations:
            final_recommendations[rec['subject']] = [class_name]
        else:
            final_recommendations[rec['subject']].append(class_name)
    print("^^ : 키워드와 유사도가 높은 순으로 정렬하는데 성공했습니다.")
    return final_recommendations

# 6. 프롬프트 작성, LLM을 이용한 추천사유 생성
def create_recommmendation_text(query, recommendations):
    prompt = f"""당신은 학교 강의평 사이트에서 강의평가 텍스트를 바탕으로 메뉴를 추천해주는 내타입수업AI입니다.
아래 목록은 {query}와 관련된 수업을 연관성 높은 순서로 나열한 목록입니다.
당신의 목표는 키워드인 {query}와 연관된 수업을 추천하는 것입니다. 키워드 총 6개로 내용은 '열정적인 교수님', '유익한 수업', '도움되는 수업', '꿀강', '얻어가는 수업' 이 있습니다. 

문구 생성 예시는 다음과 같습니다.
학교에 다니는 이유는 유익한 수업을 듣기 위해서죠. 강의평을 통해 유익한 수업을 골라보았어요.

주의사항은 다음과 같습니다.
1. 첫번째 문장은 {query}와 관련해서 해당 키워드를 선택하는 이유를 적어주세요.
2. 두번째 문장은 강의평에서 참고해서 골라보았다는 이유로 작성해 주세요. 
3. 생성하는 문장은 키워드와 관련있게 상대방에게 수업을 추천해주기 위함임을 기억하세요.
4. 문구를 생성할때는 2문장만 출력하세요.


메뉴 목록
{str(recommendations)}
"""
    recommendation_message = call_openai(prompt, 1.0, "gpt-4o-2024-11-20")
    print("^^ : GPT를 사용하여 추천사유를 생성하는데 성공하였습니다.")
    return recommendation_message

# 7. DB에 추천사유와 추천과목 업로드
def insert_to_mongo(query, text, recommendations):
    load_dotenv()
    username = urllib.parse.quote_plus(os.environ['MONGODB_USERNAME'])
    password = urllib.parse.quote_plus(os.environ['MONGODB_PASSWORD'])
    uri = f"mongodb+srv://{username}:{password}@cluster0.7pdc1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    db = client.recommendations_db
    collections = db.recommendations

    insertion = {
        "recommend_text": query,
        "recommend_reason": text,
        "recommendations": [
            {"subject": key, "class": value} for key, value in recommendations.items()]

    }
    result = collections.update_one({"_id": query}, {"$set": insertion}, upsert=True)
    
    return result

## ============== 리뷰 추천 코드 ============== ##
def recommend_batch():
    infos = fetch_subject_info()
    candidates = create_candidates(infos)
    queries = COMBINATIONS
    for query in queries:
        recommendations = create_recommendations(query, candidates)
        text = create_recommmendation_text(query, recommendations)
        result = insert_to_mongo(query, text, recommendations)
        
    print("^^ : 성공적으로 수행하였습니다.")
    

if __name__ == '__main__':
    recommend_batch()
