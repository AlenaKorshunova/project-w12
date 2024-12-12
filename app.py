import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_folder='static')

API_KEY = "pXN7tx3DfnwpGo58RXMVMbvBs7RksoGM"
BASE_URL = "http://dataservice.accuweather.com/"

@app.route('/weather/<float:latitude>/<float:longitude>', methods=['GET'])
# функция для получения данных о погоде по заданным координатам
def get_weather(latitude, longitude):
    # сформируем URL для запроса
    url = f"{BASE_URL}currentconditions/v1/{latitude},{longitude}?apikey={API_KEY}&language=ru"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # проверим на ошибки
        weather_data = response.json()
        
        # извлечем нужные параметры
        weather = {
            'temperature_celsius': weather_data[0]['Temperature']['Metric']['Value'],
            'humidity_percentage': weather_data[0]['RelativeHumidity'],
            'wind_speed_kmh': weather_data[0]['Wind']['Speed']['Metric']['Value'],
            'precipitation_probability_percentage': weather_data[0]['PrecipitationProbability']
        }
        
        return jsonify(weather), 200
    
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 400

if name == 'main':
    app.run(debug=True)
