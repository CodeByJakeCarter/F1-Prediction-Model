def test_factories_create_driver_and_constructor(entity_factory) -> None:
    driver = entity_factory.make_driver(code="HAM", name="Lewis Hamilton")
    constructor = entity_factory.make_constructor(name="Mercedes")

    assert driver.driver_id == 1
    assert driver.code == "HAM"
    assert constructor.constructor_id == 1
    assert constructor.name == "Mercedes"
