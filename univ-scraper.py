import requests
from bs4 import BeautifulSoup
import re
import time


URL = "https://nces.ed.gov/collegenavigator/?s=all&l=91+92+93+94&ct=1+2+3&ic=1+2+3&pg="

URLS = ["https://nces.ed.gov/globallocator/index.asp?search=1&State=&city=&zipcode=&miles=&itemname=seminary&sortby=name&College=1&Status=Search+Finished&Records=87&CS=A7ED9C07",
"https://nces.ed.gov/globallocator/index.asp?search=1&State=&city=&zipcode=&miles=&itemname=academy&sortby=name&College=1&CS=49051AD6",
"https://nces.ed.gov/globallocator/index.asp?search=1&State=&city=&zipcode=&miles=&itemname=institute&sortby=name&College=1&Status=Search+Finished&Records=2714&CS=B6DCB61A",
"https://nces.ed.gov/globallocator/index.asp?search=1&State=&city=&zipcode=&miles=&itemname=college&sortby=name&College=1&Status=Search+Finished&Records=1696&CS=3582F109",
"https://nces.ed.gov/globallocator/index.asp?search=1&State=&city=&zipcode=&miles=&itemname=university&sortby=name&College=1&Status=Search+Finished&Records=846&CS=58988AD9",
"https://nces.ed.gov/globallocator/index.asp?search=1&State=&city=&zipcode=&miles=&itemname=School&sortby=name&College=1&Status=Search+Finished&Records=87&CS=7A40956F"]


headers = {
    'Connection':'keep-alive',
    'Content-Type':'application/json',
    'Cookie':'<cookie-information>',
    'Sec-Fetch-User':'?1',
    'Sec-Fetch-Site':'same-origin',
    'Sec-Fetch-Mode':'navigate',
    'Sec-Fetch-Dest':'document',
    'Upgrade-Insecure-Requests':'1'
    }

f = open("college-list-2.txt", "a")


for u in URLS:
    # Scrape url
    print("Scraping... ")

    start = time.time()
    response = requests.get(u,headers=headers,verify=False,stream=True)

    print("That took "+ str(time.time()-start) + " seconds.")

    print("Parsing...")
    soup = BeautifulSoup(response.content, 'html.parser')
    descArr = soup.findAll("td", {"class": "InstDesc"})

    for d in descArr:
        f.write(d.findAll('a')[0].string+"\n")
    # detArr = soup.findAll("td", {"class": "InstDetail"})



# omitted_words = set(["My Favorites","comparisons","IPEDS Data Center"])

# for num in range(34):

#     # with FuturesSession() as session:
#     #     futures = [session.get(URL+ str(num + 1)) for num in range(34)]
#     #     for future in as_completed(futures):
#     #         response = future.result()





#     # Scrape url
#     print("Scraping page no. ",  str(num + 1))

#     start = time.time()
#     req = requests.get(URL+ str(num + 1),headers=headers,verify=False)

#     print("That took "+ str(time.time()-start) + " seconds.")

#     print("Parsing page no. ", str(num + 1))

#     start = time.time()
#     soup = BeautifulSoup(req.content, 'html.parser')
#     ls = soup.findAll("td", {"class": "InstDesc"})

#     st = str("".join(str(x) for x in ls if x))
#     st = st.replace("><","\n")
#     st = st.replace("</strong","")
#     st = st.replace("strong>","")
#     st = st.replace("<","")
#     st = st.replace(">","")
#     for l in st.split("\n"):
#         sub = l.strip()
#         if sub.replace(" ","").isalpha() and sub not in omitted_words:
#             f.write(sub+"\n")
#     # ls = [x.replace("<strong>","").replace("</strong>","").strip() for x in ls if x]
#     # ls = [x for x in ls if x.isalpha()]
#     # f.write("\n".join(x for x in ls if x not in omitted_words))
    
#     print("That took "+ str(time.time()-start) + " seconds.")

f.close()


