import pytest

from fuzzy import app


def test_index_route():
    response = app.test_client().get("/")

    assert response.status_code == 200


def test_ajax_route():
    response = app.test_client().post(
        "/query_ajax", json={"words": "عربي,عرابي"}
    )

    assert response.status_code == 201
    transliterations = {
        analysis["transliteration"] for analysis in response.json["analyses"]
    }
    assert {
        "ʿarrābīya",
        "ʿarrābī",
        "ʿarabī",
        "ʿarrābayya",
        "ʿarabīy",
        "ʿarrābay",
    } == transliterations
