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

def forecast_one(location_key): # добавила прогноз погоды на 7 день + анализ
    try:
        url = f"{BASE_URL}forecasts/v1/daily/5day/{location_key}"
        params = {"apikey": API_KEY, "metric": "true"}  # Используем метрику (градусы Цельсия)
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return None, "Forecast data not found"

        # Берем только первый день
        day = data["DailyForecasts"][6]
        avg_temp = (day["Temperature"]["Minimum"]["Value"] + day["Temperature"]["Maximum"]["Value"]) / 2
        analysis = weather_analysis({
            # в прогнозе нет влажности и ветра, добавила среднюю температуру и описание дня и ночи
            "temperature_celsius": avg_temp,
            "humidity": None,
            "wind_speed_kmh": None,
            "weather_text": day["Day"]["IconPhrase"]
        })
        forecast = {
            "date": day["Date"],
            "avg_temp": avg_temp,
            "day_text": day["Day"]["IconPhrase"],
            "night_text": day["Night"]["IconPhrase"],
            "analysis": analysis
        }
        return forecast, None
    except requests.RequestException as e:
        return None, str(e)

@app.route('/')
def home():
    # Отображение главной страницы
    return render_template('index.html')


@app.route('/route-weather', methods=['POST']) #маршрут польщователя на сайте
def route_weather():
    start_city = request.form.get('start')
    end_city = request.form.get('end')

    if not start_city or not end_city:
        return render_template('index.html', error="Please enter both start and end cities.") #добавляю предупреждение об ошибке

    try:
        # Данные для начального города
        start_location_key, error_start = coordinates_by_city(start_city)
        #все if обрабатывают потенциальные ошибки
        if error_start:
            return render_template('index.html', error=f"Error for start city: {error_start}")

        start_weather, error_start_weather = weather_by_location(start_location_key)
        if error_start_weather:
            return render_template('index.html', error=f"Error getting weather for start city: {error_start_weather}")

        start_precipitation_probability, error_start_precipitation = precipitation_probability(start_location_key)
        if error_start_precipitation:
            return render_template('index.html', error=f"Error getting precipitation data for start city: {error_start_precipitation}")

        start_forecast, error_start_forecast = forecast_one(start_location_key)
        if error_start_forecast:
            return render_template('index.html', error=f"Error getting forecast for start city: {error_start_forecast}")

        # Данные для конечного города
        end_location_key, error_end = coordinates_by_city(end_city)
        if error_end:
            return render_template('index.html', error=f"Error for end city: {error_end}")

        end_weather, error_end_weather = weather_by_location(end_location_key)
        if error_end_weather:
            return render_template('index.html', error=f"Error getting weather for end city: {error_end_weather}")

        end_precipitation_probability, error_end_precipitation = precipitation_probability(end_location_key)
        if error_end_precipitation:
            return render_template('index.html', error=f"Error getting precipitation data for end city: {error_end_precipitation}")

        end_forecast, error_end_forecast = forecast_one(end_location_key)
        if error_end_forecast:
            return render_template('index.html', error=f"Error getting forecast for end city: {error_end_forecast}")

        # Анализ
        start_analysis = weather_analysis(start_weather)
        end_analysis = weather_analysis(end_weather)

        # Передача данных в шаблон html
        return render_template(
            'result.html',
            start_city=start_city,
            end_city=end_city,
            start_weather=start_weather,
            end_weather=end_weather,
            start_precipitation_probability=start_precipitation_probability,
            end_precipitation_probability=end_precipitation_probability,
            start_forecast=start_forecast,
            end_forecast=end_forecast,
            start_analysis=start_analysis,
            end_analysis=end_analysis
        )

    except requests.RequestException as e:
        return render_template('index.html', error="Network error or API unavailable.")
    except Exception as e:
        return render_template('index.html', error="An unexpected error occurred.")



if __name__ == '__main__':
    app.run(debug=True)
