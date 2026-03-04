def test_artifact_temp_dir_fixture_writes_under_temp_root(tmp_artifacts_dir) -> None:
    artifact_path = tmp_artifacts_dir / "report.json"
    artifact_path.write_text('{"status":"ok"}', encoding="utf-8")

    assert artifact_path.exists()
    assert artifact_path.parent == tmp_artifacts_dir
