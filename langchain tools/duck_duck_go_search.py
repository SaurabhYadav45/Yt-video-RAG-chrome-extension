from ddgs import DDGS


query = "Top news in india"
with DDGS() as ddgs:
    results = ddgs.news(query)
    for r in results:
        print(r["title"])
        print(r["url"])
        print(r["body"])
        print("-" * 50)