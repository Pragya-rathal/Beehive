import importlib
import sys
import logging


def def test_app_imports_without_python_magic(monkeypatch, caplog):
    monkeypatch.delitem(sys.modules, "magic", raising=False)
    monkeypatch.syspath_prepend("/path/that/does/not/exist")
    sys.modules.pop("app", None)

    imported_app = importlib.import_module("app")

    assert imported_app.app is not None
    assert "python-magic is not installed; MIME detection is unavailable until dependency is installed." in caplog.text
