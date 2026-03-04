def test_http_client_helper_calls_health_endpoint(http_client) -> None:
    response = http_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
