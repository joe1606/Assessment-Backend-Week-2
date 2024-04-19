"""This file defines the API routes."""

# pylint: disable = no-name-in-module
from flask import Flask, Response, request, jsonify
from psycopg2.errors import ForeignKeyViolation

from database import get_db_connection, get_cursor

app = Flask(__name__)
conn = get_db_connection()


@app.route("/", methods=["GET"])
def index() -> Response:
    """Returns a welcome message."""
    return jsonify({
        "title": "Clown API",
        "description": "Welcome to the world's first clown-rating API."
    })

def show_all_clowns_with_ratings(order) -> str:
    """SQL query for all movies with ratings"""
    return f"""SELECT c.clown_id, c.clown_name, s.speciality_name,
            AVG(r.rating) AS average_rating,COUNT(r.review_id) AS review_count
            FROM clown AS c
            LEFT JOIN review AS r ON c.clown_id = r.clown_id
            JOIN speciality AS s ON c.speciality_id = s.speciality_id
            WHERE r.review_id IS NOT NULL
            GROUP BY c.clown_id, c.clown_name, s.speciality_name
            ORDER BY average_rating {order};"""


def show_all_clowns_without_ratings() -> str:
    """SQL query for all movies with ratings"""
    return """SELECT c.clown_id, c.clown_name, s.speciality_name
            FROM clown AS c
            LEFT JOIN review AS r ON c.clown_id = r.clown_id
            JOIN speciality AS s ON c.speciality_id = s.speciality_id
            WHERE r.review_id IS NULL
            GROUP BY c.clown_id, c.clown_name, s.speciality_name;"""


@app.route("/clown", methods=["GET", "POST"])
def get_clowns() -> Response:
    """Returns a list of clowns in response to a GET request;
    Creates a new clown in response to a POST request."""
    if request.method == "GET":
        with conn.cursor() as cur:

            order = request.args.get("order")
            if not order:
                order = 'descending'

            if order not in {'ascending':'ASC', 'descending':'DESC'}.keys():
                return jsonify({'error': 'order is ascending or descending'}), 404

            order = {'ascending': 'ASC', 'descending': 'DESC'}[order]

            cur.execute(show_all_clowns_with_ratings(order))
            results_with_ratings = cur.fetchall()

            cur.execute(show_all_clowns_without_ratings())
            results_without_ratings = cur.fetchall()

            return jsonify(results_with_ratings + results_without_ratings), 200


    else:
        data = request.json
        try:
            if "clown_name" not in data or "speciality_id" not in data:
                raise KeyError("New clowns need both a name and a speciality.")
            if not isinstance(data["speciality_id"], int):
                raise ValueError("Clown speciality must be an integer.")

            with conn.cursor() as cur:
                cur.execute("""INSERT INTO clown
                                 (clown_name, speciality_id)
                               VALUES (%s, %s)
                               RETURNING *;""",
                            (data["clown_name"], data["speciality_id"]))
                new_clown = cur.fetchone()
                conn.commit()
            return jsonify(new_clown), 201
        except (KeyError, ValueError, ForeignKeyViolation) as err:
            print(err.args[0])
            conn.rollback()
            return jsonify({
                "message": err.args[0]
            }), 400

def find_clown_from_id(cursor, clown_id) -> bool:
    """Returns true if the clown exists in the database"""
    cursor.execute("SELECT clown_id FROM clown", (clown_id, ))
    valid_id = cursor.fetchall()
    return clown_id in [id['clown_id'] for id in valid_id]


def check_if_clown_has_reviews(cursor, clown_id: int) -> bool:
    """Returns true if clown has more than 0 reviews"""
    cursor.execute(
        """SELECT COUNT(review_id) FROM review WHERE clown_id = %s""", (clown_id, ))
    count = cursor.fetchall()
    return count[0]['count']


def query_for_clown_with_reviews() -> str:
    """SQL query including avergage rating and number of ratings"""
    return """SELECT c.clown_id, c.clown_name, s.speciality_name,
                    AVG(r.rating) AS average_rating, COUNT(r.review_id) AS number_of_ratings
                    FROM clown AS c
                    LEFT JOIN review AS r ON c.clown_id = r.clown_id
                    JOIN speciality AS s ON c.speciality_id = s.speciality_id
                    WHERE c.clown_id = %s
                    GROUP BY c.clown_id, c.clown_name, s.speciality_name
                    HAVING COUNT(r.review_id) IS NOT NULL;"""


def query_for_clown_with_no_reviews() -> str:
    """SQL query not showing ratings"""
    return """SELECT c.clown_id, c.clown_name, s.speciality_name
                    FROM clown AS c
                    LEFT JOIN review AS r ON c.clown_id = r.clown_id
                    JOIN speciality AS s ON c.speciality_id = s.speciality_id
                    WHERE c.clown_id = %s
                    GROUP BY c.clown_id, c.clown_name, s.speciality_name
                    HAVING COUNT(r.review_id) IS NOT NULL;"""


@app.route("/clown/<int:clown_id>", methods=["GET"])
def get_clown(clown_id: int) -> Response:
    """Returns clown information based on ID input"""

    connection = get_db_connection()
    cursor = get_cursor(connection)

    if not find_clown_from_id(cursor, clown_id):
        return jsonify({'error': 'matching ID not found for clown'}), 404

    if check_if_clown_has_reviews(cursor, clown_id):
        cursor.execute(query_for_clown_with_reviews(), (clown_id, ))
        return_data = cursor.fetchall()
    else:
        cursor.execute(query_for_clown_with_no_reviews(), (clown_id, ))
        return_data = cursor.fetchall()

    return jsonify(return_data), 200


@app.route("/clown/<int:clown_id>/review", methods=["POST"])
def review_clown(clown_id: int) -> Response:
    """Returns clown information based on ID input"""
    data = request.json
    connection = get_db_connection()
    cursor = get_cursor(connection)

    if "rating" not in data:
        return {'error': 'Need clown rating.'}, 400

    rating = data['rating']
    if rating < 1 or rating > 5:
        return {'error': 'Rating must be from 1 to 5'}, 400

    cursor.execute(
        """INSERT INTO review(clown_id, rating)
            VALUES (%s, %s);""", (clown_id, rating))

    connection.commit()
    cursor.close()
    conn.close()

    return {'success': 'rating for clown added'}, 200



if __name__ == "__main__":
    app.run(port=8080, debug=True)
