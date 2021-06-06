"""

"""
import json
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from datetime import date, timedelta
import requests
from nsepy import get_history
import telegram


def send_to_telegram_group(data, token, chat_id):
    """
    Send a message to a telegram user or group specified on chatId
    chat_id must be a number!
    """
    header = data[0].keys()
    rows = [x.values() for x in data]
    #TODO: instaed of showing the entire data just show the name of the stocks as below formart
    """
    BYG_<DATE>: The stocks that are in buy range today are below:
    stock names
    """
    html = tabulate(rows, headers=header, tablefmt="grid")
    bot = telegram.Bot(token=token)
    bot.sendMessage(chat_id=chat_id, text=html)


def date_from_timestamp(ts):
    """

    :param ts:
    :return:
    """
    dt = date.fromtimestamp(int(ts))
    return dt

def read_json(file_path="config.json"):
    """

    :param file_path:
    :return:
    """
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data


def get_data_from_url(url):
    """

    :return:
    """
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    else:
        raise ValueError(f"Error while fetching data from url : status code  is {resp.status_code} , and reason is {resp.reason}")


def get_latest_day_stock_data(symbol, start_date=date.today() - timedelta(days=4),
                              end_date=date.today() - timedelta(days=1)):
    """

    :param symbol:
    :param start_date:
    :param end_date:
    :return:
    """
    data = get_history(symbol, start=start_date, end=end_date)
    print(data)
    if data.empty:
        return {}
    row = data.tail(1)
    row = row.reset_index()
    return row.to_json(orient="records")

def suggestion(range_data, previous_day_data):
    """

    :param range_data:
    :param previous_day_data:
    :return:
    """
    suggest = {}
    buy_start_range = range_data["buy_start_range"]
    buy_end_range = range_data["buy_end_range"]
    stock_last_price = previous_day_data["Last"]
    if buy_start_range <= stock_last_price <= buy_end_range:
        suggest["in_range"] = "YES"
    else:
        suggest["in_range"] = "NO"
    suggest["buy_start_range"] = buy_start_range
    suggest["buy_end_range"] = buy_end_range
    suggest["stock_last_price"] = stock_last_price
    suggest["stock"] = range_data["stock_name"]
    suggest["group"] = range_data["group_name"]
    return suggest


def compare():
    """

    :return:
    """
    config = read_json()
    stock_lookup_by_group_api = config["stock_lookup_by_group_api"]
    groups = config["groups"]
    output = []
    for group in groups:
        uri = stock_lookup_by_group_api.format(group)
        symbols_data = get_data_from_url(uri)
        for symbol in symbols_data:
            symbol_hist = get_latest_day_stock_data(symbol["stock_name"].upper())
            if symbol_hist:
                suggest_data = suggestion(symbol, json.loads(symbol_hist)[0])
                output.append(suggest_data)
            else:
                print(f" stock : {symbol['stock_name']} has no data ")
    send_to_telegram_group(output, config["telegram_token"], config["chat_id"])

if __name__ == '__main__':
    compare()



