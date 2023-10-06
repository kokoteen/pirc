import os
import pytest
from pirg.pirg import (
    create_requirements,
from pirg.utils import (
    PYPI_URL,
    check_for_pip_args,
    load_requirements_file,
    get_name_version,
    create_requirements,
    run_subprocess,
    find_requirements_file,
)


@pytest.fixture
def temporary_requirements_file(tmpdir):
    requirements_path = os.path.join(tmpdir, "requirements.txt")
    with open(requirements_path, "w") as req_file:
        req_file.write("package1==1.0.0\n")

    yield requirements_path

    os.remove(requirements_path)


def test_create_requirements(temporary_requirements_file):
    package_names = {"package2==2.0.0", "package3==3.0.0"}
    create_requirements(package_names, temporary_requirements_file)

    with open(temporary_requirements_file, "r") as req_file:
        lines = req_file.readlines()
        assert "package1==1.0.0\n" not in lines
        assert "package2==2.0.0\n" in lines
        assert "package3==3.0.0\n" in lines


def test_load_requirements_file(temporary_requirements_file):
    requirements = load_requirements_file(temporary_requirements_file)
    assert len(requirements) == 1
    assert "package1" in [pkg.name for pkg in requirements]


def test_get_name_version():
    package_names = {"numpy", "pandas"}
    installed_pkgs = get_name_version(package_names)
    package_name = ["package1"]
    mock_response_body = {
        "releases": {
            "1.0.0": [{"requires_python": ">=3.8"}],
            "1.1.0": [{"requires_python": ">=3.8"}],
            "1.2.0": [{"requires_python": ">=3.8"}],
        }
    }

    for pkg in package_name:
        url = PYPI_URL(pkg)

        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, url, json=mock_response_body)
            result = get_name_version(pkg)

            assert result.name == pkg
            assert str(result.version) == "1.2.0"


def test_find_requirements_file(tmpdir):
    root_dir = tmpdir.mkdir("project")
    sub_dir1 = root_dir.mkdir("subdirectory1")
    sub_dir2 = sub_dir1.mkdir("subdirectory2")

    root_dir.join("requirements.txt").write("Test requirements file content")

    os.chdir(str(sub_dir2))
    assert find_requirements_file() == str(root_dir.join("requirements.txt"))

    os.chdir(str(tmpdir))
    assert find_requirements_file() is None


    for pkg, pkg_name in zip(installed_pkgs, package_names):
        assert pkg_name == pkg.name
