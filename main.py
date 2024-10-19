import json
import folium
import requests
from flask import Flask
from geopy import distance


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_coffee_distance(coffee_coordinates):
    return coffee_coordinates['Distance']


def read_file():
    with open('index.html') as file:
        return file.read()


def main():
    with open('coffee.json', 'r', encoding='CP1251') as coffee:
        coffee_file = coffee.read()
    coffee_houses = json.loads(coffee_file)
    yandex_apikey = '70c8480a-feed-4906-8c79-0d6744fe1cf5'

    your_place = input("Ваше местоположение - ")
    user_coords = fetch_coordinates(yandex_apikey, your_place)

    user_longitude, user_latitude = user_coords

    cofe_coords = []
    for coffee_house in coffee_houses:
        longitude, latitude = coffee_house["geoData"]["coordinates"]
        coffe_coordinates = {
            'title': coffee_house['Name'],
            'Latitude': latitude,
            'Longitude': longitude,
            'Distance': distance.distance((longitude, latitude), (user_longitude, user_latitude)).km,
            }
        cofe_coords.append(coffe_coordinates)

    sorted_coffee = sorted(cofe_coords, key=get_coffee_distance)
    nearest_coffee_houses = sorted_coffee[:5]

    coffee_map = folium.Map(location=[user_latitude, user_longitude])

    for one_coffee_house in nearest_coffee_houses:
        folium.Marker(
            [one_coffee_house['Latitude'], one_coffee_house['Longitude']],
            popup=one_coffee_house['title'], tooltip='').add_to(coffee_map)

    coffee_map.save("index.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'hello', read_file)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()
