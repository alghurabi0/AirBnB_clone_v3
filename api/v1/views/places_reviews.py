#!/usr/bin/python3
"""Review restful API"""
from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.review import Review
from models.place import Place
from models.user import User


@app_views.route('/places/<place_id>/reviews', methods=['GET'])
def get_reviews(place_id):
    """get all reviews"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    reviews = [review.to_dict() for review in place.reviews]
    return jsonify(reviews)


@app_views.route('/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    """get a review"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    """delete a review"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    storage.delete(review)
    storage.save()
    return jsonify({}), 200


@app_views.route('/places/<place_id>/reviews', methods=['POST'])
def post_review(place_id):
    """create a review"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.json:
        abort(400, 'Not a JSON')
    if 'user_id' not in request.json:
        abort(400, 'Missing user_id')
    if 'text' not in request.json:
        abort(400, 'Missing text')
    user = storage.get(User, request.json['user_id'])
    if user is None:
        abort(404)
    review = Review(**request.get_json())
    review.place_id = place_id
    review.save()
    return jsonify(review.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['PUT'])
def put_review(review_id):
    """update a review"""
    review = storage.get(Review, review_id)
    if review is None:
        abort(404)
    if not request.json:
        abort(400, 'Not a JSON')
    for k, v in request.json.items():
        if k not in ['id', 'user_id', 'place_id', 'created_at', 'updated_at']:
            setattr(review, k, v)
    review.save()
    return jsonify(review.to_dict()), 200
