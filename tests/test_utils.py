from src.agentic.utils import read_ignore_file, get_project_name, get_files_in_dir, get_subdirs
from pathlib import Path

def test_read_ignore_file(tmp_path):
    ignore = tmp_path / ".agenticignore"
    ignore.write_text("# comment\nfoo.py\nbar/\n")
    patterns = read_ignore_file(tmp_path)
    assert "foo.py" in patterns
    assert "bar/" in patterns

def test_get_project_name(tmp_path):
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "myproj"\n')
    assert get_project_name(tmp_path) == "myproj"

def test_get_project_name_fallback(tmp_path):
    assert get_project_name(tmp_path) == tmp_path.name

def test_get_files_in_dir(tmp_path):
    f = tmp_path / "a.py"
    f.write_text("x=1")
    files = list(get_files_in_dir(tmp_path))
    assert f in files

def test_get_subdirs(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    subdirs = list(get_subdirs(tmp_path))
    assert d in subdirs
