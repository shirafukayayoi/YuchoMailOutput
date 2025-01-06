import base64
import csv
import os
import re

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail APIとGoogleスプレッドシートAPIのスコープ
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]


# Gmail APIにログイン
def gmail_login():
    credentials_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "credentials.json"
    )
    token_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "token.json")

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service, creds


# Gmailから「ゆうちょデビット」メールを取得
def get_yucho_message(service):
    results = (
        service.users()
        .messages()
        .list(
            userId="me",
            q='subject:"【ゆうちょデビット】ご利用のお知らせ"',
            maxResults=5,
        )
        .execute()
    )
    messages = results.get("messages", [])
    while "nextPageToken" in results:
        page_token = results["nextPageToken"]
        results = (
            service.users()
            .messages()
            .list(
                userId="me",
                q='subject:"【ゆうちょデビット】ご利用のお知らせ"',
                maxResults=5,
                pageToken=page_token,
            )
            .execute()
        )
        messages.extend(results.get("messages", []))

    messages = list(reversed(messages))

    pattern_date = r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}"
    pattern_amount = r"\d{1,3}(,\d{3})*円"
    pattern_store = r"利用店舗\s+(.*)"

    dates = []
    amounts = []
    stores = []

    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        payload = msg["payload"]
        parts = payload.get("parts")
        text = ""
        if parts:
            for part in parts:
                if part["mimeType"] == "text/plain":
                    data = part["body"]["data"]
                    text = base64.urlsafe_b64decode(data).decode("utf-8")
        else:
            data = payload["body"]["data"]
            text = base64.urlsafe_b64decode(data).decode("utf-8")

        strings_date = re.search(pattern_date, text)
        strings_amount = re.search(pattern_amount, text)
        strings_store = re.search(pattern_store, text)

        if strings_date:
            dates.append(strings_date.group())
        if strings_amount:
            amount_value = strings_amount.group().replace("円", "").replace(",", "")
            amounts.append(int(amount_value))
        if strings_store:
            stores.append(strings_store.group(1))

    return dates, amounts, stores


# Googleスプレッドシートにログイン
def spreadsheet_login(creds, spreadsheet_id):
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(spreadsheet_id)
    sheet = spreadsheet.sheet1
    return sheet


# CSVファイルに書き込み
def write_to_csv(dates, amounts, stores):
    filename = "yucho_usage.csv"
    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["日付", "金額", "店舗"])
        for date, amount, store in zip(dates, amounts, stores):
            writer.writerow([date, amount, store])
    print(f"データを {filename} に出力しました。")


# スプレッドシートにデータを書き込み
def while_yuchomail_output(dates, amounts, stores, sheet):
    if len(dates) != len(amounts) or len(dates) != len(stores):
        print("Error: The lengths of dates, amounts, and stores lists do not match.")
        return

    sheet.clear()
    sheet.update("A1", [["日付", "金額", "店舗"]])
    rows = [[dates[i], amounts[i], stores[i]] for i in range(len(dates))]
    sheet.append_rows(rows)
    print("データをGoogleスプレッドシートに出力しました。")
    sheet.update("E1", [["合計"]])
    sheet.update("E2", [["=SUM(B2:B)"]], value_input_option="USER_ENTERED")


# メイン処理
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    service, creds = gmail_login()
    dates, amounts, stores = get_yucho_message(service)

    output_type = input("CSVとして出力しますか？（y/n）: ")

    if output_type.lower() == "y":
        write_to_csv(dates, amounts, stores)
    else:
        spreadsheet_id = input("スプレッドシートのIDを入力してください: ")
        sheet = spreadsheet_login(creds, spreadsheet_id)
        while_yuchomail_output(dates, amounts, stores, sheet)
