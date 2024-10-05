import os
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


def get_coffee_houses_with_distance(coffee_houses):
	cofe_coords = []
	for coffee_house in coffee_houses:
		latitude, longitude = coffee_house["geoData"]["coordinates"]
		coffe_coordinates = {
			'title': coffee_house['Name'],
			'Latitude': latitude,
			'Longitude': longitude,
			'Distance': distance.distance((latitude, longitude), (user_latitude, user_longitude)).km,
			}
		cofe_coords.append(coffe_coordinates)
		return cofe_coords


def get_coffee_distance(coffee_coordinates):
	return coffee_coordinates['Distance']


def get_nearest_coffee_houses(coffee_house_coordinates):
	sorted_coffee = sorted(coffee_house_coordinates, key=get_coffee_distance)
	nearest_coffee_houses = sorted_coffee[:coffee_in_page]
	return nearest_coffee_houses


def read_file():
	with open('index.html') as file:
		return file.read()


def main():
	with open(coffee_path, 'r', encoding=encode) as coffee:
		coffee_file = coffee.read()
		coffee_houses = json.loads(coffee_file)
	apikey_of_user_coordinates = os.environ['API_KEY']
	coffee_coordinates = []
	pages = []
	tooltip = "Вот одно место!"	

	your_place = input("Ваше местоположение - ")
	user_coords = fetch_coordinates(apikey_of_user_coordinates, your_place)

	number_of_cafes_per_page = 5
	coffee_in_page = number_of_cafes_per_page

	coffee_houses = get_coffee_file_content("coffee.json", "CP1251")

	user_latitude, user_longitude = user_coords

	coffee_house_coordinates = get_coffee_houses_with_distance(coffee_houses)

	sorted_coffee_houses = get_nearest_coffee_houses(coffee_house_coordinates)

	map_of_coffee = folium.Map(location=[user_longitude, user_latitude])

	for one_coffee_house in sorted_coffee_houses:
		folium.Marker(
			[one_coffee_house['Longitude'], one_coffee_house['Latitude']],
			popup=one_coffee_house['title'], tooltip=tooltip).add_to(map_of_coffee)

	map_of_coffee.save("index.html")

	app = Flask(__name__)
	app.add_url_rule('/', 'hello', read_file)
	app.run('0.0.0.0')


if __name__ == '__main__':
	main