import requests
from lxml import html
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials

DO_UPDATE_SHEET = True

TOEFL_SCORE_THRESHOLD = 100
GRE_SCORE_THRESHOLD = 300
DECISION_LIST = ["admit", "applied"]
PERCENTAGE_THRESHOLD = 70.0
DESIRED_COURSES = ["computer", "data", "management", "information", "product"]
GPA_THRESHOLD = 7.5

USERNAME = "<YOUR YOCKET EMAIL ADDR>"
PASSWORD = "<YOUR YOCKET PASSWORD>"
BASE_URL = "https://yocket.in"
LOGIN_URL = "https://yocket.in/account/login"
URL = "https://yocket.in/recent-admits-rejects?page="


def read_document():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    # Requesting Google sheets API. You can generate your own json file from developer console.
    creds = ServiceAccountCredentials.from_json_keyfile_name('yocket-scraper.json', scope)
    client = gspread.authorize(creds)
    return client.open("Data").sheet1


def update_sheet(sheet, results):
    # This cell range can change as per your requirement
    cell_list = sheet.range("A2:J300")

    index = 0
    index_val = 0
    for cell in cell_list:
        print("sheet index ", cell.row, " ", cell.col)

        if index_val >= len(results[0]):
            index += 1
            index_val = 0

        if index >= len(results):
            break

        cell.value = results[index][index_val]
        index_val += 1

    # Update in batch
    if DO_UPDATE_SHEET:
        print("updating sheet...")
        sheet.update_cells(cell_list)


def upload_to_sheets(results):
    # if not results:
    #     return

    sheet = read_document()
    update_sheet(sheet, results)


def scrape_results(session_requests):
    collective = []
    for num in range(4):
        # Scrape url
        result = session_requests.get(URL + str(num + 1), headers=dict(referer=URL))
        tree = html.fromstring(result.content)
        bucket_names = tree.xpath('//*[@class="panel-body"]')
        for x in range(0, len(bucket_names)):
            print("Checking page ", num, " result ", x + 1, "....")

            # Checking for desired courses
            course = str(bucket_names[x].xpath('./div[1]/div[2]/h4/strong/text()')[1]).replace('\n', '').lower()
            if not is_item_in_list(course, DESIRED_COURSES):
                continue

            decision = str(bucket_names[x].xpath('./div[1]/div[2]/h4/label/text()')[0]).replace('\n', '').lower()
            if not is_item_in_list(decision, DECISION_LIST):
                continue

            # Checking for decision
            if DECISION_LIST not in decision.lower():
                continue

            # Checking for GPA and Percentage
            gpa = str(bucket_names[x].xpath('./div[2]/div[3]/text()')[1]).replace('\n', '').lower()
            if "gpa" in gpa and float(gpa.replace("cgpa", "").strip()) < GPA_THRESHOLD:
                continue
            if "%" in gpa and float(gpa.replace("%", "").strip()) < PERCENTAGE_THRESHOLD:
                continue

            # Checking for GRE score
            gre = str(bucket_names[x].xpath('./div[2]/div[1]/text()')[1]).replace('\n', '').lower().strip()
            if gre.isnumeric() and int(gre) < GRE_SCORE_THRESHOLD:
                continue

            # Checking for TOEFL score
            toefl = str(bucket_names[x].xpath('./div[2]/div[2]/text()')[1]).replace('\n', '').lower().strip()
            if toefl.isnumeric() and int(toefl) < TOEFL_SCORE_THRESHOLD:
                continue

            university = str(bucket_names[x].xpath('./div[1]/div[2]/h4/strong/text()')[0]).replace('\n', '')
            year = str(bucket_names[x].xpath('./div[1]/div[2]/h4/small/text()')[0]).replace('\n', '')
            # last_updated = str(bucket_names[x].xpath('./div[1]/div[2]/p/text()')[0]).replace('\n', '')
            name = str(bucket_names[x].xpath('./div[1]/div[2]/p/a/text()')[0]).replace('\n', '')
            profile_link = BASE_URL + str(bucket_names[x].xpath('./div[1]/div[2]/p/a/@href')[0]).replace('\n', '')
            wex = str(bucket_names[x].xpath('./div[2]/div[4]/text()')[1]).replace('\n', '')
            obj = [name, university, course, gre, toefl, gpa, wex, profile_link, decision, year]
            collective.append(obj)
    return collective


def is_item_in_list(datalist, itemlist):
    item_found = False
    for word in itemlist:
        if word in datalist:
            item_found = True
            break
    return item_found


def main():
    session_requests = requests.session()

    # Get login csrf token
    result = session_requests.get(LOGIN_URL)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='_csrfToken']/@value")))[0]

    # Create payload
    payload = {
        "email": USERNAME,
        "password": PASSWORD,
        "_csrfToken": authenticity_token
    }

    # Perform login
    login_req = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))

    # Scrape Results
    results = scrape_results(session_requests)

    # Upload to Google Sheets
    upload_to_sheets(results)
    # upload_to_sheets([])


if __name__ == '__main__':
    main()
