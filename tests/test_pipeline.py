import json
import os
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator
import yaml

from document_pipeline.export import (
    build_documents_manifest,
    build_profile_export,
    write_documents_manifest,
)
from document_pipeline.generator import escape_latex, format_date_range
from document_pipeline.html import (
    html_escape_text,
    normalize_latex_text,
    skill_items_text,
)
from document_pipeline.html_renderer import (
    HTML_DOCUMENT_TYPES,
    DEFAULT_DOCUMENTS_BASE_URL,
    render_html_documents,
)
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
    assert data.documents.resume.settings.font_size == "10pt"


def test_current_career_profile_identifies_scrutable_not_moons_out():
    data = ProjectData.load(PROJECT_ROOT)
    experience_entries = data.core["experience"]["entries"]
    current_roles = [
        entry for entry in experience_entries if entry["end_date"] == "Present"
    ]
    assert len(current_roles) == 1
    assert current_roles[0]["organization"] == "Scrutable™"
    assert current_roles[0]["title"] == "Founder & Managing Alchemist"

    moons_out_roles = [
        entry
        for entry in experience_entries
        if "Moons Out" in entry["organization"]
    ]
    assert len(moons_out_roles) == 1
    assert moons_out_roles[0]["end_date"] == "Mar 2026"
    assert moons_out_roles[0]["organization"] == "Moons Out Media"
    assert (
        moons_out_roles[0]["title"]
        == "Lab Director & Systems Alchemist — Moons Out Labs"
    )
    assert "moonsoutmedia.com" not in json.dumps(data.personal.model_dump())


def test_verified_timeline_and_credentials_are_preserved():
    data = ProjectData.load(PROJECT_ROOT)

    nebula = next(
        entry
        for entry in data.core["experience"]["entries"]
        if entry["organization"] == "Nebula Academy"
    )
    assert nebula["start_date"] == "Sep 2022"
    assert nebula["end_date"] == "Mar 2025"

    education = data.core["education"]["entries"]
    vsu = next(entry for entry in education if entry["institution"] == "Valdosta State University")
    assert vsu["end_date"] == "Present"
    aiu = next(
        entry
        for entry in education
        if entry["institution"] == "American InterContinental University Online"
    )
    assert aiu["date_range"] == "2017"
    assert "49 Credits Earned" in aiu["degree"]

    certifications = data.optional["certifications"]["entries"]
    instructor_badge = next(
        entry
        for entry in certifications
        if entry["name"] == "Accredited Technology Instructor"
    )
    assert instructor_badge["date_range"] == "Issued 2023"
    assert "end_date" not in instructor_badge


def test_service_record_and_document_scope_are_preserved():
    data = ProjectData.load(PROJECT_ROOT)
    experience = data.core["experience"]["entries"]

    technician = next(
        entry
        for entry in experience
        if entry["title"] == "Engineer Electrical Systems Technician"
    )
    technician_text = " ".join(technician["items"])
    assert "AMMPS" in technician_text
    assert "Incirlik Air Base" in technician_text
    assert "VMAQ-3" in technician_text
    assert "two-Marine power team" in technician_text

    maintenance_chief = next(
        entry for entry in experience if entry["title"] == "Assistant Maintenance Chief"
    )
    assert "sergeant's (E-5) billet as a corporal (E-4)" in maintenance_chief["items"][0]
    assert "life-sustaining critical utilities infrastructure" in " ".join(
        maintenance_chief["items"]
    )

    quality_control = next(
        entry
        for entry in experience
        if entry["title"] == "Quality Control Non-Commissioned Officer"
    )
    assert "turning the Assistant Maintenance Chief role over" in quality_control["items"][0]

    assert data.personal.position["cv"] == "Software Engineer • Marine~Corps Veteran"
    assert "projects" not in data.documents.resume.sections
    assert "projects" in data.documents.cv.sections
    assert data.optional["projects"]["entries"]


def test_scrutable_identity_registry_and_trademark_contract():
    data = ProjectData.load(PROJECT_ROOT)
    marks = data.identity["marks"]
    assert marks == {
        "parent": "Scrutable™",
        "wordmark": "SCRUTABLE™",
        "promise": "We show our work.™",
        "labs": "Scrutable Labs™",
        "media": "Scrutable Media™",
        "works": "Scrutable Works™",
        "commons": "Scrutable Commons™",
        "execos": "ExecOS™",
    }
    official_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PROJECT_ROOT / "content" / "core").glob("*.yaml"))
    )
    assert "Scrutable™" in official_source
    assert "Scrutable," not in official_source
    assert "Scrutable " not in official_source
    assert "®" not in official_source


def test_leadership_resume_uses_current_scrutable_timeline():
    data = ProjectData.load(PROJECT_ROOT)
    business = next(
        category
        for category in data.optional["leadership"]["categories"]
        if category["name"] == "Business & Technical Leadership"
    )
    current = [entry for entry in business["entries"] if entry["end_date"] == "Present"]
    assert len(current) == 1
    assert current[0]["organization"] == "Scrutable™"
    assert current[0]["title"] == "Founder & Managing Alchemist"
    assert current[0]["start_date"] == "Mar 2026"
    nebula = next(entry for entry in business["entries"] if entry["organization"] == "Nebula Academy")
    assert nebula["start_date"] == "Sep 2022"


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
        ".claude/commands/promote-example.md",
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


def test_claude_workflow_documents_archive_and_fact_citation_contracts():
    skill = (PROJECT_ROOT / ".claude/skills/document-generator/SKILL.md").read_text()
    tailored = (PROJECT_ROOT / ".claude/commands/tailored-draft.md").read_text()
    archive = (PROJECT_ROOT / ".claude/commands/archive-run.md").read_text()
    promote = (PROJECT_ROOT / ".claude/commands/promote-example.md").read_text()

    assert "content/<file>.yaml:<key>" in skill
    assert "content/<file>.yaml:<key>" in tailored
    assert "CUSTOM_GENERATION_ARCHIVE_ROOT" in archive
    assert "make validate" in archive
    assert "docs/ARCHIVE_CONTRACT.md" in promote
    assert "checklist-only by default" in promote


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


def test_html_helpers_strip_latex_artifacts():
    assert normalize_latex_text(r"Cloud \& DevOps") == "Cloud & DevOps"
    assert normalize_latex_text("Marine~Corps Veteran") == "Marine Corps Veteran"
    assert normalize_latex_text(r"a \textbullet{} b") == "a • b"
    assert html_escape_text(r"R\&D & growth") == "R&amp;D &amp; growth"
    assert skill_items_text(["one", "", "two"]) == "one, two"
    assert skill_items_text("solo") == "solo"


def test_html_renderer_emits_expected_files(tmp_path):
    paths = render_html_documents()
    output_dir = PROJECT_ROOT / "output"
    expected = {f"{doc_type}.html" for doc_type in HTML_DOCUMENT_TYPES}
    actual = {path.name for path in paths}
    assert expected == actual
    for doc_type in HTML_DOCUMENT_TYPES:
        html_path = output_dir / f"{doc_type}.html"
        assert html_path.exists(), f"missing {html_path}"
        text = html_path.read_text(encoding="utf-8")
        # Self-contained styles, semantic markup, no stray LaTeX commands.
        assert "<style>" in text
        assert "<main" in text
        assert "\\textbullet" not in text
        assert "~Corps" not in text  # `~` from YAML must be non-breaking space
        assert "SCRUTABLE™" in text
        assert "We show our work.™" in text
        assert "PROFESSIONAL RECORD" in text
        assert data_record_id_for(doc_type) in text


def data_record_id_for(doc_type):
    return {
        "resume": "BG-CAREER-001",
        "cv": "BG-CAREER-002",
        "leadership_resume": "BG-CAREER-003",
    }[doc_type]


def test_html_renderer_links_to_pdf_counterpart():
    output_dir = PROJECT_ROOT / "output"
    for doc_type in HTML_DOCUMENT_TYPES:
        html_path = output_dir / f"{doc_type}.html"
        text = html_path.read_text(encoding="utf-8")
        assert f"{doc_type}.pdf" in text


def test_html_renderer_makes_phone_actionable():
    resume_html = (PROJECT_ROOT / "output" / "resume.html").read_text(encoding="utf-8")
    assert 'href="tel:+12295073499"' in resume_html


def test_documents_manifest_matches_portfolio_schema():
    manifest = build_documents_manifest()
    assert manifest["version"] == 1
    assert manifest["generatedAt"].endswith("Z")
    types_in_order = [document["type"] for document in manifest["documents"]]
    assert types_in_order == ["resume", "cv"]
    required = {"type", "title", "summary", "pdf", "html"}
    for document in manifest["documents"]:
        assert required <= set(document)
        assert document["type"] in {"resume", "cv"}
        assert document["pdf"].endswith(".pdf")
        assert document["html"].endswith(".html")


def test_documents_manifest_canonical_url_is_resolvable():
    expected_base = "https://brandon-gottshall.github.io/About-Me"
    assert DEFAULT_DOCUMENTS_BASE_URL == expected_base


def test_write_documents_manifest_writes_to_output(tmp_path):
    manifest_path = write_documents_manifest()
    assert manifest_path.exists()
    payload = json.loads(manifest_path.read_text())
    assert payload["version"] == 1
    assert len(payload["documents"]) == 2
