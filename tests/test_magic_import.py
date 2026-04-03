import importlib
import sys


def test_app_imports_without_python_magic(monkeypatch, caplog):
    monkeypatch.delitem(sys.modules, "magic", raising=False)
    sys.modules.pop("app", None)
    imported_app = importlib.import_module("app")
    assert imported_app.app is not None
    assert "python-magic" in caplog.text
