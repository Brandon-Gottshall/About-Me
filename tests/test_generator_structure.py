import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


class GeneratorStructureTests(unittest.TestCase):
    def test_generate_script_is_only_a_compatibility_wrapper(self):
        source = (SCRIPTS / "generate.py").read_text()

        self.assertIn("document_generator", source)
        self.assertLessEqual(source.count("\ndef "), 1)
        self.assertLessEqual(len(source.splitlines()), 80)

    def test_generator_has_small_named_modules(self):
        expected_modules = [
            "__init__.py",
            "cli.py",
            "content.py",
            "cover_letters.py",
            "entries.py",
            "html.py",
            "latex.py",
            "text.py",
        ]

        package_dir = SCRIPTS / "document_generator"
        missing = [
            module_name
            for module_name in expected_modules
            if not (package_dir / module_name).exists()
        ]

        self.assertEqual([], missing)

    def test_default_documents_are_declared_in_one_place(self):
        from document_generator import DEFAULT_DOCUMENTS, normalize_document_type

        self.assertEqual(
            ["resume", "cv", "cover_letter", "leadership_resume"],
            DEFAULT_DOCUMENTS,
        )

        self.assertEqual("cover_letter", normalize_document_type("cover-letter"))
        self.assertEqual(
            "leadership_resume",
            normalize_document_type("leadership-resume"),
        )

    def test_generator_source_lines_stay_readable(self):
        source_paths = [
            *sorted((SCRIPTS / "document_generator").glob("*.py")),
            SCRIPTS / "build.py",
            SCRIPTS / "generate.py",
            SCRIPTS / "validate_yaml.py",
            *sorted((ROOT / "tests").glob("test_*.py")),
        ]

        long_lines = []
        for path in source_paths:
            for line_number, line in enumerate(path.read_text().splitlines(), 1):
                if len(line) > 88:
                    long_lines.append(f"{path.relative_to(ROOT)}:{line_number}")

        self.assertEqual([], long_lines)


if __name__ == "__main__":
    unittest.main()
