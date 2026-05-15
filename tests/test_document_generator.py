import sys
import unittest
import json
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import build  # noqa: E402
import generate  # noqa: E402


class DocumentGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.content_core_dir = PROJECT_ROOT / "content" / "core"
        self.content_optional_dir = PROJECT_ROOT / "content" / "optional"
        self.config_dir = PROJECT_ROOT / "config"
        self.config = generate.load_yaml(self.config_dir / "documents.yaml")

    def test_latex_cv_omits_empty_optional_sections(self):
        sections = generate.generate_sections(
            self.content_core_dir,
            self.content_optional_dir,
            self.config,
            "cv",
        )

        self.assertNotIn(r"\cvsection{Projects}", sections)
        self.assertNotIn(r"\cvsection{Publications}", sections)
        self.assertNotIn(r"\cvsection{Presentation}", sections)
        self.assertNotIn(r"\cvsection{Teaching Experience}", sections)
        self.assertNotIn(r"\cvsection{Volunteer Work}", sections)
        self.assertIn(r"\cvsection{Languages}", sections)

    def test_html_cv_omits_empty_optional_sections(self):
        sections = generate.generate_html_sections(
            self.content_core_dir,
            self.content_optional_dir,
            self.config,
            "cv",
        )

        self.assertNotIn("projects-section", sections)
        self.assertNotIn("publications-section", sections)
        self.assertNotIn("presentations-section", sections)
        self.assertNotIn("teaching-section", sections)
        self.assertNotIn("volunteer-section", sections)
        self.assertIn("languages-section", sections)

    def test_html_inline_text_converts_latex_commands(self):
        text = r"Adel, GA \textbullet{} brandongottshall.com \& LinkedIn"

        self.assertEqual(
            generate.format_inline_html(text),
            "Adel, GA &bull; brandongottshall.com &amp; LinkedIn",
        )

    def test_build_main_exits_nonzero_when_latex_build_fails(self):
        failed_generate = SimpleNamespace(returncode=0)

        with mock.patch.object(sys, "argv", ["build.py", "cv"]):
            with mock.patch.object(build, "run_command", return_value=failed_generate):
                with mock.patch.object(build, "build_latex", return_value=False):
                    with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                        with self.assertRaises(SystemExit) as cm:
                            build.main()

        self.assertNotEqual(cm.exception.code, 0)

    def test_build_normalizes_document_aliases(self):
        self.assertEqual("cover-letter", build.normalize_doc_type("cover_letter"))
        self.assertEqual(
            "leadership-resume",
            build.normalize_doc_type("leadership_resume"),
        )

    def test_document_manifest_lists_public_documents_only(self):
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            manifest_path = generate.write_document_manifest(
                output_dir,
                generated_at="2026-05-14T00:00:00Z",
            )

            manifest = json.loads(manifest_path.read_text())

        self.assertEqual(1, manifest["version"])
        self.assertEqual("2026-05-14T00:00:00Z", manifest["generatedAt"])
        self.assertEqual(
            ["resume", "cv"],
            [document["type"] for document in manifest["documents"]],
        )
        self.assertEqual(
            {
                "resume": ("resume.pdf", "resume.html"),
                "cv": ("cv.pdf", "cv.html"),
            },
            {
                document["type"]: (document["pdf"], document["html"])
                for document in manifest["documents"]
            },
        )

    def test_html_theme_uses_portfolio_tokens(self):
        html_templates_dir = PROJECT_ROOT / "templates" / "html"
        css = "\n".join(
            path.read_text()
            for path in html_templates_dir.glob("*.css")
        )

        self.assertIn("--portfolio-navy", css)
        self.assertIn("Inter", css)
        self.assertNotIn("#039BE5", css)
        self.assertNotIn("#DC143C", css)
        self.assertNotIn("Source Sans Pro", css)


if __name__ == "__main__":
    unittest.main()
