import requests
from flask import Flask
from flask import request
from flask import Response
import json
import re

from flask_sslify import SSLify

# importing request object from flask framework not same as request library

app = Flask(__name__)
sslify = SSLify(app)  # comment this if testing locally

token = 'xxxxxxxxxxxxxxxxx'
APP_ID = 'xxxxxxxxxxxxxxxx'


def write_json(data, filename='response.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_weather_data(district):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'.format(district, APP_ID)
    r = requests.get(url).json()
    if str(r["cod"]) == "404":
        return r["message"]
    lat = "Latitude: " + str(r['coord']['lat'])
    lon = "Longitude: " + str(r['coord']['lon'])
    main = "Main: " + str(r["weather"][0]["main"])
    description = "Description: " + str(r["weather"][0]["description"])
    wind_speed = "Wind speed:" + str(r["wind"]["speed"])
    result = '\n'.join([lat, lon, main, description, wind_speed])
    print(result)
    return result


def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    pattern = r'/[a-zA-Z]{2,10}'
    ticker = re.findall(pattern, txt)  # if not command->list !empty

    if ticker:
        symbol = ticker[0][1:]  # returns the first /{cmd} > cmd
    else:
        symbol = ''

    return chat_id, symbol  # returning tuple


def send_message(chat_id, text='default_text'):
    url = "https://api.telegram.org/bot{}/sendMessage".format(token)
    payload = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=payload)
    return r


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()  # msg contain JSON sent by telegram
        print(msg)
        chat_id, symbol = parse_message(msg)
        print("===========" + str(chat_id) + "=================")
        if not symbol:  # i.e. if symbol is ''
            send_message(chat_id, 'Invalid Input')
            return Response('Ok', status=200)

        print("=================================")
        weather_data = get_weather_data(symbol)
        send_message(chat_id, weather_data)
        # write_json(msg, 'telegram_request.json')
        return Response('Ok', status=200)
    else:
        return '<h1 style="color:green;">Success</h1>'


if __name__ == '__main__':
    app.run(debug=False)
