import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import urllib.parse

# 성별, 나이별 추천 키워드 예시(각 30개씩)
male_keywords = [
    "스테이크", "삼겹살", "치킨", "갈비", "돈까스", "피자", "햄버거", "라면", "카레", "치즈",
    "감자탕", "떡볶이", "파스타", "짬뽕", "마라탕", "부대찌개", "감자", "계란찜", "된장찌개", "순두부찌개",
    "돈불고기", "족발", "닭볶음탕", "회", "참치", "해물파전", "불닭", "김치찌개", "김밥", "토마토파스타"
]
female_keywords = [
    "샐러드", "오트밀", "닭가슴살", "과일", "두부", "콩나물국", "잡곡밥", "도라지무침", "과일주스", "현미밥",
    "오믈렛", "연어샐러드", "닭가슴살샐러드", "아보카도", "청포묵무침", "연두부", "구운야채", "토마토", "버섯볶음", "가지구이",
    "미역국", "단호박죽", "오트밀죽", "방울토마토", "시금치나물", "고구마구이", "코코넛워터", "아몬드", "야채수프", "로제파스타"
]
age_keywords = {
    "20": ["샐러드", "떡볶이", "치즈볼", "치킨", "김밥", "마라탕", "파스타", "아보카도", "로제파스타", "라면",
           "샤브샤브", "버블티", "닭갈비", "오므라이스", "스시", "유부초밥", "쌀국수", "팬케이크", "베이글", "초밥",
           "회덮밥", "함박스테이크", "치즈돈까스", "케밥", "계란토스트", "콩나물불고기", "망고빙수", "불닭볶음면", "버거", "타코"],
    "30": ["잡채", "된장찌개", "갈비찜", "콩나물국", "파프리카볶음", "유산슬", "닭볶음탕", "돼지불고기", "새우볶음밥", "순두부찌개",
           "연어스테이크", "양송이수프", "스테이크", "쭈꾸미볶음", "굴전", "낙지볶음", "현미밥", "스파게티", "연두부샐러드", "깻잎김치",
           "두부구이", "오징어볶음", "닭죽", "우엉조림", "치즈스틱", "크림파스타", "쌀국수", "피클", "불고기", "양배추롤"],
    "40": ["도라지무침", "고등어조림", "시금치나물", "북엇국", "청국장", "미역국", "배추전", "소고기무국", "우거지탕", "버섯볶음",
           "멸치볶음", "김치전", "계란찜", "연근조림", "꽁치구이", "청포묵무침", "깻잎장아찌", "가자미조림", "양배추쌈", "삼치구이",
           "가지무침", "쑥갓나물", "돼지수육", "카레라이스", "삼계탕", "닭도리탕", "현미밥", "잡곡밥", "고사리나물", "애호박전"],
    "50": ["연근조림", "나물비빔밥", "매생이국", "순두부찌개", "장어구이", "도미구이", "갓김치", "닭한마리", "묵은지찜", "닭백숙",
           "굴국밥", "홍합미역국", "곤드레밥", "생선전", "애호박볶음", "우엉조림", "우거지국", "코다리찜", "동태찌개", "청국장",
           "보리밥", "시래기국", "갈치조림", "보쌈", "매운탕", "돌나물무침", "우럭조림", "브로콜리무침", "고사리나물", "쑥국"],
    "60": ["미역줄기볶음", "우엉조림", "고들빼기", "청포묵무침", "연근조림", "더덕구이", "곤드레밥", "닭죽", "명란젓", "보리굴비",
           "전복죽", "조개탕", "김치찌개", "매운탕", "콩비지찌개", "청국장", "연근나물", "모듬전", "갓김치", "호박죽",
           "모시조개국", "무나물", "코다리조림", "쑥국", "가지나물", "콩나물국", "누룽지", "고구마줄기볶음", "무국", "청경채나물"]
}

def get_age_keywords(age):
    try:
        age = int(age)
        decade = str((age // 10) * 10)
        return age_keywords.get(decade, [])
    except:
        return []

st.title("맞춤형 레시피 추천 시스템")
st.markdown("거주 지역(나라 이름), 성별, 나이, 재료를 입력하세요.")

with st.form("recipe_form"):
    region = st.selectbox(
        "거주 지역(나라 이름) 선택",
        ("한국", "중국", "일본", "미국", "이탈리아", "프랑스", "동남아", "태국", "베트남", "인도", "그리스", "멕시코", "스페인", "터키", "러시아", "영국", "독일", "브라질", "세계요리")
    )
    gender = st.radio("성별", ("남성", "여성"))
    age = st.text_input("나이", "25")
    st.info(f"{region} 요리만 추천합니다. **재료는 한국어로 3개 이상 입력하세요**. (예: 감자, 당근, 닭고기)")
    ingredient_input = st.text_input("재료를 입력하세요 (쉼표 또는 공백으로 구분)", "")
    submitted = st.form_submit_button("레시피 추천 받기")

if submitted:
    if ',' in ingredient_input:
        ingredients = [ing.strip() for ing in ingredient_input.split(',') if ing.strip()]
    else:
        ingredients = [ing.strip() for ing in ingredient_input.split() if ing.strip()]

    # ✨ 입력 재료에 성별/나이대별 추천 키워드 자동 추가 (중복 방지)
    user_keywords = []
    if gender == "남성":
        user_keywords += [k for k in male_keywords if k not in ingredients]
    elif gender == "여성":
        user_keywords += [k for k in female_keywords if k not in ingredients]
    user_keywords += [k for k in get_age_keywords(age) if k not in ingredients and k not in user_keywords]
    final_ingredients = ingredients + user_keywords[:7]  # 앞에서 7개만 추가

    if len(ingredients) < 3:
        st.error("재료는 3개 이상 입력해야 합니다.")
    else:
        region_map = {
            "한국": "한식",
            "중국": "중식",
            "일본": "일식"
        }
        category = region_map.get(region, region)  # 맵에 없으면 그대로 사용

        query = "+".join(final_ingredients)
        url = f"https://www.10000recipe.com/recipe/list.html?q={category}&order=reco"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        recipes = soup.select("ul.common_sp_list_ul.ea4 li")[:20]  # 최대 20개까지 받아서 필터

        results = []
        for item in recipes:
            title_tag = item.select_one(".common_sp_caption_tit")
            link_tag = item.select_one("a")
            if not title_tag or not link_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = "https://www.10000recipe.com" + link_tag["href"]

            # 상세 페이지에서 재료 추출
            detail = requests.get(link)
            detail_soup = BeautifulSoup(detail.text, 'html.parser')
            script_tag = detail_soup.find("script", {"type": "application/ld+json"})
            if not script_tag:
                continue
            try:
                json_data = json.loads(script_tag.string)
                recipe_ingredients = json_data.get("recipeIngredient", [])
            except:
                continue

            matched = [i for i in ingredients if any(i in ing for ing in recipe_ingredients)]
            unmatched = [i for i in recipe_ingredients if not any(ing in i for ing in ingredients)]
            match_rate = round(len(matched) / len(recipe_ingredients) * 100, 1) if recipe_ingredients else 0

            results.append({
                "title": title,
                "link": link,
                "match_rate": match_rate,
                "matched": matched,
                "unmatched": unmatched
            })

        results = sorted(results, key=lambda x: -x['match_rate'])[:5]

        if not results:
            st.warning("😢 입력한 재료와 일치하는 레시피가 없습니다.")
        else:
            st.success(f"🍽️ [{region}] 맞춤형 레시피 추천 결과 (Top 5)")
            for i, r in enumerate(results, 1):
                st.markdown(f"**{i}. [{r['title']}]({r['link']})** ({r['match_rate']}%)")
                st.markdown(f"✅ **일치한 재료:** {', '.join(r['matched']) if r['matched'] else '없음'}")
                st.markdown(f"❌ **부족한 재료:** {', '.join(r['unmatched']) if r['unmatched'] else '없음'}")
                st.markdown(f"🛒 **장바구니:**")
                for item in r['unmatched']:
                    encoded = urllib.parse.quote_plus(item)
                    search_link = f"https://www.coupang.com/np/search?component=&q={encoded}"
                    st.markdown(f"- [{item}]({search_link})")
                st.markdown("---")
