"""This file contains tests for the API."""

from app import app
import unittest
from unittest.mock import patch


class TestAPIClownGet:
    """Contains tests for the /clown GET route"""

    @patch("app.conn")
    def test_get_clown_returns_200(self, mock_conn, test_app, fake_clown):
        """Tests that the /clown endpoint returns 200 on a GET request."""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchall.return_value = [fake_clown]

        res = test_app.get("/clown")

        assert res.status_code == 200

    @patch("app.conn")
    def test_get_clown_returns_list_of_dicts(self, mock_conn, test_app, fake_clown):
        """Tests that the /clown endpoint returns a list of valid dicts 
        on a GET request"""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchall.return_value = [fake_clown]

        res = test_app.get("/clown")
        data = res.json

        assert isinstance(data, list)
        assert all(isinstance(c, dict) for c in data)
        assert all("clown_id" in c
                   for c in data)

    @patch("app.conn")
    def test_get_clown_accesses_database(self, mock_conn, test_app):
        """Tests that the /clown endpoint makes expected calls to the database
        on a GET request."""

        mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
        mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchall

        test_app.get("/clown")

        assert mock_execute.call_count == 2
        assert mock_fetch.call_count == 2


class TestAPIClownPost:
    """Contains tests for the /clown POST route"""

    @patch("app.conn")
    def test_post_clown_returns_201(self, mock_conn, test_app, fake_clown):
        """Tests that the /clown endpoint returns 201 on a POST request."""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone.return_value = [fake_clown]

        res = test_app.post("/clown", json=fake_clown)

        assert res.status_code == 201

    @patch("app.conn")
    def test_post_clown_returns_400_on_invalid(self, mock_conn, test_app):
        """Tests that the /clown endpoint returns 400 on a POST request
        with an invalid body."""

        mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone.return_value = {}

        assert test_app.post("/clown", json={}).status_code == 400
        assert test_app.post("/clown", json={"clown_name": "A",
                                             "speciality_id": "r"}).status_code == 400

    @patch("app.conn")
    def test_post_clown_calls_db(self, mock_conn, test_app):
        """Tests that the /clown endpoint makes the expected calls to the db
        on a POST request."""

        mock_execute = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .execute
        mock_fetch = mock_conn.cursor.return_value\
            .__enter__.return_value\
            .fetchone

        mock_fetch.return_value = {}

        _ = test_app.post("/clown", json={"clown_name": "Miriam",
                                          "speciality_id": 1})

        assert mock_fetch.call_count == 1
        assert mock_execute.call_count == 1


    @patch('app.get_db_connection')
    def test_get_clown_by_id(self, mock_get_db_connection, test_app, new_fake_clown_with_ratings):
        """Tests that the /clown/1 endpoint returns clown data"""
        mock_get_db_connection.return_value.cursor.return_value\
            .execute.return_value\
            .fetchall.return_value = [new_fake_clown_with_ratings]

        response = test_app.get('/clown/1')
        returned_clown = response.json
        assert returned_clown == [new_fake_clown_with_ratings]


    @patch('app.get_db_connection')
    def test_get_clowns_endpoint(self, mock_get_db_connection, test_app, new_fake_clown_with_ratings):
        mock_get_db_connection.return_value.cursor.return_value\
            .execute.return_value\
            .fetchall.return_value = [new_fake_clown_with_ratings]

        response = test_app.get('/clown')
        
        assert 'clown_name' in response.json[0]
        assert 'speciality_name' in response.json[0]


if __name__ == '__main__':
    unittest.main()
