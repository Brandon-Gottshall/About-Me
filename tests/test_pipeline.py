import json
import os
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator
import yaml

from document_pipeline.export import build_profile_export
from document_pipeline.generator import escape_latex, format_date_range
from document_pipeline.models import ProjectData
from document_pipeline.privacy import scan_pdf_locations, scan_text_files
from document_pipeline.renderer import normalize_doc_type
from document_pipeline.validate import PROJECT_ROOT, validate_project


def test_yaml_content_and_config_are_valid():
    assert validate_project(PROJECT_ROOT) == []


def test_project_data_models_load_official_documents():
    data = ProjectData.load(PROJECT_ROOT)
    assert data.personal.name.first == "Brandon"
    assert data.documents.resume.sections[0] == "summary"
    assert data.documents.cover_letter.variant in {"default", "academic_music"}


def test_document_type_aliases_are_normalized():
    assert normalize_doc_type("cover-letter") == "cover_letter"
    assert normalize_doc_type("leadership-resume") == "leadership_resume"
    assert normalize_doc_type("resume") == "resume"


def test_agent_workflow_files_are_present():
    expected = [
        "CLAUDE.md",
        ".claude/skills/document-generator/SKILL.md",
        ".claude/commands/validate.md",
        ".claude/commands/build-official.md",
        ".claude/commands/tailored-draft.md",
        ".claude/commands/archive-run.md",
        "prompts/document-generator/tailored-system.md",
        "prompts/document-generator/tailored-task.md",
        "prompts/document-generator/archive-checklist.md",
    ]
    assert all((PROJECT_ROOT / path).exists() for path in expected)


def test_codex_plugin_manifest_points_to_about_me_repo():
    manifest = json.loads(
        (
            PROJECT_ROOT
            / "plugins"
            / "document-generator"
            / ".codex-plugin"
            / "plugin.json"
        ).read_text()
    )
    about_me_url = "https://github.com/Brandon-Gottshall/About-Me"
    assert manifest["homepage"] == about_me_url
    assert manifest["repository"] == about_me_url
    assert manifest["interface"]["websiteURL"] == about_me_url
    assert (
        manifest["interface"]["privacyPolicyURL"]
        == f"{about_me_url}/blob/master/AGENTS.md"
    )
    assert (
        manifest["interface"]["termsOfServiceURL"]
        == f"{about_me_url}/blob/master/PROVENANCE.md"
    )
    assert "Brandon-Gottshall/document-generator" not in json.dumps(manifest)


def test_github_actions_use_node24_action_versions():
    workflow = yaml.safe_load((PROJECT_ROOT / ".github/workflows/verify.yml").read_text())
    steps = [
        step
        for job in workflow["jobs"].values()
        for step in job["steps"]
        if "uses" in step
    ]
    action_refs = {step["uses"] for step in steps}
    assert "actions/checkout@v5" in action_refs
    assert "actions/setup-python@v6" in action_refs
    assert "actions/upload-artifact@v7" in action_refs
    assert action_refs.isdisjoint(
        {
            "actions/checkout@v4",
            "actions/setup-python@v5",
            "actions/upload-artifact@v4",
        }
    )


def test_archive_helper_writes_synthetic_run_outside_public_repo(tmp_path):
    archive_root = tmp_path / "archive"
    env = os.environ.copy()
    env["CUSTOM_GENERATION_ARCHIVE_ROOT"] = str(archive_root)

    result = subprocess.run(
        [
            sys.executable,
            str(
                PROJECT_ROOT
                / "plugins"
                / "document-generator"
                / "scripts"
                / "archive_generation.py"
            ),
            "--company",
            "Synthetic Company",
            "--role",
            "Synthetic Role",
            "--source-url",
            "https://example.invalid/jobs/synthetic-role",
            "--tool",
            "claude",
        ],
        cwd=PROJECT_ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert str(PROJECT_ROOT) not in result.stdout
    manifests = list(archive_root.glob("runs/*/*/manifest.json"))
    assert len(manifests) == 1
    manifest_path = manifests[0]
    run_root = manifest_path.parent
    manifest_path = run_root / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["agent"]["tool"] == "claude"
    assert manifest["agent"]["plugin"] == "document-generator"
    assert manifest["target"]["company"] == "Synthetic Company"
    assert manifest["publication"] == "private"


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
