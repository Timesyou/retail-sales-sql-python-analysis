import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from safe_extract_archive import UnsafeArchiveError, validate_and_extract

class SafeArchiveTests(unittest.TestCase):
    def _zip(self, root: Path, entries: list[tuple[str, bytes, int | None]]) -> Path:
        path = root / "sample.zip"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                for name, data, mode in entries:
                    info = zipfile.ZipInfo(name)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    if mode is not None:
                        info.external_attr = mode << 16
                    archive.writestr(info, data)
        return path

    def _valid(self):
        return [
            ("shelfsense/pyproject.toml", b"[project]\n", None),
            ("shelfsense/src/shelfsense/__init__.py", b"__version__='1'\n", None),
            ("shelfsense/data/sales.csv", b"date,amount\n", None),
            ("shelfsense/data/inventory.csv", b"sku,stock\n", None),
        ]

    def test_valid_archive_extracts_expected_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self._zip(root, self._valid())
            destination = root / "out"
            count = validate_and_extract(archive, destination)
            self.assertEqual(count, 4)
            self.assertTrue((destination / "shelfsense/src/shelfsense/__init__.py").is_file())

    def test_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self._zip(root, self._valid() + [("shelfsense/../../escape.txt", b"x", None)])
            with self.assertRaises(UnsafeArchiveError):
                validate_and_extract(archive, root / "out")

    def test_rejects_absolute_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self._zip(root, self._valid() + [("/tmp/escape.txt", b"x", None)])
            with self.assertRaises(UnsafeArchiveError):
                validate_and_extract(archive, root / "out")

    def test_rejects_backslash_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self._zip(root, self._valid() + [(r"shelfsense\\..\\escape.txt", b"x", None)])
            with self.assertRaises(UnsafeArchiveError):
                validate_and_extract(archive, root / "out")

    def test_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self._zip(root, self._valid() + [("shelfsense/link", b"target", 0o120777)])
            with self.assertRaises(UnsafeArchiveError):
                validate_and_extract(archive, root / "out")

    def test_rejects_environment_secrets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self._zip(root, self._valid() + [("shelfsense/.env", b"SECRET=x", None)])
            with self.assertRaises(UnsafeArchiveError):
                validate_and_extract(archive, root / "out")

    def test_rejects_case_colliding_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = self._zip(root, self._valid() + [("shelfsense/README.md", b"a", None), ("shelfsense/readme.md", b"b", None)])
            with self.assertRaises(UnsafeArchiveError):
                validate_and_extract(archive, root / "out")

if __name__ == "__main__":
    unittest.main()
