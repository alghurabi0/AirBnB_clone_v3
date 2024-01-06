#!/usr/bin/python3
"""Places view module"""
from api.v1.views import app_views
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from models.city import City
from models.user import User


@app_views.route('/cities/<city_id>/places', methods=['GET'])
def get_places(city_id):
    """get all places in a city"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'])
def get_place(place_id):
    """get a place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'])
def delete_place(place_id):
    """delete a place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places', methods=['POST'])
def post_place(city_id):
    """create a place"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")
    if 'name' not in request.get_json():
        abort(400, description="Missing name")
    user_id = request.get_json()['user_id']
    user = storage.get(User, user_id)
    if user is None:
        abort(404)
    place = Place(**request.get_json())
    place.city_id = city_id
    place.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'])
def put_place(place_id):
    """update a place"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    for key, value in request.get_json().items():
        if key not in ['id', 'user_id', 'city_id', 'created_at', 'updated_at']:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'])
def post_places_search():
    """search for places"""
    if not request.get_json():
        abort(400, description="Not a JSON")
    places = storage.all(Place).values()
    if 'states' in request.get_json() and request.get_json()['states']:
        places = [place for place in places if place.city.state_id in
                  request.get_json()['states']]
    if 'cities' in request.get_json() and request.get_json()['cities']:
        places = [place for place in places if place.city_id in
                  request.get_json()['cities']]
    if 'amenities' in request.get_json() and request.get_json()['amenities']:
        places = [place for place in places if all(amenity.id in
                  [amenity.id for amenity in place.amenities] for amenity in
                  request.get_json()['amenities'])]
    places = [place.to_dict() for place in places]
    return jsonify(places)