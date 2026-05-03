import json
from pathlib import Path

from jsonschema import Draft202012Validator

from document_pipeline.export import build_profile_export
from document_pipeline.generator import escape_latex, format_date_range
from document_pipeline.privacy import scan_pdf_locations, scan_text_files
from document_pipeline.validate import PROJECT_ROOT, validate_project


def test_yaml_content_and_config_are_valid():
    assert validate_project(PROJECT_ROOT) == []


def test_date_range_formatting():
    assert format_date_range("Jan 2020", "Present") == "Jan 2020 - Present"
    assert format_date_range("Jan 2020", "") == "Jan 2020"
    assert format_date_range("", "Present") == "Present"
    assert format_date_range("", "") == ""


def test_latex_escape_preserves_allowed_commands():
    text = r"Cloud & DevOps with \textbf{bold signal} and 50% ownership"
    escaped = escape_latex(text)
    assert r"\textbf{bold signal}" in escaped
    assert r"\&" in escaped
    assert r"\%" in escaped


def test_static_export_shape():
    payload = build_profile_export(PROJECT_ROOT)
    assert payload["profile"]["name"] == "Brandon Gottshall"
    assert {doc["id"] for doc in payload["documents"]} == {
        "resume",
        "cv",
        "leadership_resume",
        "coverletter",
    }
    assert all(doc["publicPath"].startswith("output/") for doc in payload["documents"])


def test_privacy_scan_has_no_unexpected_public_findings():
    assert scan_text_files() == []
    assert scan_pdf_locations() == []


def test_official_outputs_are_tracked_under_output():
    expected = {
        "coverletter.pdf",
        "cv.pdf",
        "leadership_resume.pdf",
        "resume.pdf",
    }
    output_files = {path.name for path in (PROJECT_ROOT / "output").glob("*.pdf")}
    assert expected.issubset(output_files)
    assert not list(Path(PROJECT_ROOT).glob("*.pdf"))


def test_sanitized_archive_example_matches_schema():
    schema = json.loads(
        (PROJECT_ROOT / "schemas/archive/custom-generation-run.schema.json").read_text()
    )
    manifest = json.loads(
        (PROJECT_ROOT / "examples/archive/sanitized-run/manifest.json").read_text()
    )
    errors = list(Draft202012Validator(schema).iter_errors(manifest))
    assert errors == []
