import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__, static_folder='static')

API_KEY = "pXN7tx3DfnwpGo58RXMVMbvBs7RksoGM"
BASE_URL = "http://dataservice.accuweather.com/"


def coordinates_by_city(city): #получаем координаты города по названию, чтобы потом использовать их
    try:
        url = f"{BASE_URL}locations/v1/cities/search"  #отдельно на accuweather
        params = {"apikey": API_KEY, "q": city}  #стандартные
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None, f"City '{city}' not found."  #сразу добавляю проверку на неправильно введенный город

        location_key = data[0]["Key"]
        return location_key, None
    except requests.RequestException as e:
        return None, f"API error for city '{city}': {e}"  #если проблемы с API

# функция для получения данных о погоде по заданным координатам
def get_weather(location_key):
    # сформируем URL для запроса
    url = f"{BASE_URL}currentconditions/v1/{location_key}"
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

def precipitation_probability(location_key): #получаем вероятности осадков из другого url
    try:
        url = f"{BASE_URL}forecasts/v1/hourly/1hour/{location_key}"
        params = {
            "apikey": API_KEY,
            "metric": "true"  # Используем метрическую систему
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None, "Precipitation data not found"

        precipitation_probability = data[0].get("PrecipitationProbability", 0)
        return precipitation_probability, None
    except requests.RequestException as e:
        return None, str(e)

def check_bad_weather(temperature, wind_speed, precipitation_probability, humidity):
    temperature = weather_data.get("temperature_celsius")
    wind_speed = weather_data.get("wind_speed_kmh")
    humidity = weather_data.get("humidity")
    weather_text = weather_data.get("weather_text", "").lower()
    precipitation_probability = weather_data.get("PrecipitationProbability", 0)
    
    if temperature > 25:
        return "там слишком жарко, сиди дома и ешь мороженое"
    if temperature < -10:
        return "ты замерзнешь, лучше дома попить чай"
    if wind_speed > 20:
        return "тебя снесет вихрем переживаний, сегодня лючше остаться дома"
    if precipitation_probability > 70:
        return "its goona be rain outside"
    if humidity > 50:
        return "its too wet outside"
    return "its fine go play outside!!!"


@app.route('/weather/<float:latitude>/<float:longitude>', methods=['GET'])

if name == 'main':
    app.run(debug=True)
