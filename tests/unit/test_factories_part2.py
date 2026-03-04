def test_factories_build_minimal_season_race_and_result(entity_factory) -> None:
    season = entity_factory.make_season(2024)
    driver = entity_factory.make_driver()
    constructor = entity_factory.make_constructor()
    race = entity_factory.make_race(season=season.season, round_number=1, name="Bahrain GP")
    result = entity_factory.make_result(
        race_id=race.race_id,
        driver_id=driver.driver_id,
        constructor_id=constructor.constructor_id,
        position=1,
        points=25.0,
    )

    assert season.season == 2024
    assert race.season == season.season
    assert result.race_id == race.race_id
    assert result.driver_id == driver.driver_id
    assert result.constructor_id == constructor.constructor_id
