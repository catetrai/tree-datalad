from pathlib import Path
import subprocess
import pytest
from datalad import api as dl
from datalad.distribution.dataset import require_dataset
from datalad.support.exceptions import NoDatasetFound


# --- Tree command options to be tested
TREE_OPTS = [
    "-a",
    "-c",
    "-d",
    "-f",
    "-g",
    "-h",
    "-l",
    "-n",
    "-p",
    "-q",
    "-r",
    "-s",
    "-t",
    "-u",
    "-v",
    "-A",
    "-C",
    "-D",
    "-F",
    "-N",
    "--inodes",
    "--device",
    "--noreport",
    "--dirsfirst",
    "--prune",
    "--du",
]


def build_tree_opts_params() -> list:
    """
    Build combinations of options of 'tree' command to be used as pytest parameters.
    Each option combination is a list of option strings.
    :return: a list of option combination lists
    """
    params = [[opt] for opt in TREE_OPTS]  # each individual option on its own
    params.append(TREE_OPTS)  # all options combined
    return params


@pytest.fixture(scope="session", params=build_tree_opts_params())
def opts(request):
    """Parametrized fixture for options of 'tree' command to be tested"""
    return request.param


@pytest.fixture(scope="session", params=[1, 4])
def depth(request):
    """Parametrized fixture for directory depth levels to be tested (tree option '-L')"""
    return request.param


# --- Fixtures and helper functions for tree-datalad
@pytest.fixture(scope="session")
def testdir(tmp_path_factory):
    """
    Creates a temporary directory tree on which to run the
    'tree' and 'tree-datalad' commands.
    Uses pytest's `tmp_path_factory` session fixture to create a
    temp dir that will be deleted at the end of the test session.
    """
    temp_dir_name = "tree_datalad"
    temp_dir = tmp_path_factory.mktemp(temp_dir_name)

    superds_path = Path(temp_dir.absolute(), "superds")
    superds = dl.create(path=superds_path, cfg_proc="text2git")

    subds_path = Path(superds_path.absolute(), "subds")
    subds = dl.create(dataset=superds, path=subds_path, cfg_proc="text2git")

    subsubdir_path = Path(temp_dir, "subdir1", "subsubdir1")
    Path.mkdir(subsubdir_path, parents=True)

    Path(subds_path, "annexed-file.dat").write_bytes(b"\x01")
    Path(subds_path, "git-file-subds.txt").write_text(
        "regular file in subds", encoding="utf-8"
    )
    Path(subsubdir_path, "git-file-subdir.txt").write_text(
        "regular file in subdir", encoding="utf-8"
    )
    dl.save(dataset=superds, recursive=True)

    yield superds_path

    dl.remove(dataset=superds_path, reckless="kill")


def _tree_like_command(command: str, depth: int, opts: list, testdir: str) -> list:
    """
    Output of 'tree-*' command run with given options and input directory.

    :param command: either 'tree' or 'tree-datalad'
    :param depth: integer specifying directory hierarchy level ('-L' option of tree)
    :param opts: list of tree options
    :param testdir: path to input directory on which to run tree
    :return: stdout of tree command as list (one item per line of stdout)
    """
    depth = str(int(depth))
    all_options = []
    all_options.extend(["-I", ".git"])  # ignore .git directory
    all_options.extend(["-L", depth])  # set hierarchy level
    all_options.append(opts) if type(opts) is str else all_options.extend(opts)
    out = subprocess.run(
        [command, *all_options, testdir],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    print(f"Command:  {' '.join([command, *all_options, str(testdir)])}")
    print(f"Output:")
    print(out.stdout)
    return out.stdout.splitlines()


@pytest.fixture(scope="function")
def tree(depth, opts, testdir):
    """Output of 'tree' command run with given options and input directory"""
    return _tree_like_command("tree", depth, opts, testdir)


@pytest.fixture(scope="function")
def tree_datalad(depth, opts, testdir):
    """Output of 'tree-datalad' command run with given options and input directory"""
    return _tree_like_command("tree-datalad", depth, opts, testdir)


@pytest.fixture(scope="function")
def tree_datalad_full_paths(depth, opts, testdir):
    """Output of 'tree-datalad -f' command run with given options and input directory"""
    return _tree_like_command("tree-datalad", depth, opts + ["-f"], testdir)


@pytest.fixture(scope="session")
def ds_marker():
    """
    Returns marker appended to dataset paths in the output of 'tree-datalad'.
    Calls the function from the tree-datalad shell script by sourcing the script.
    """
    function_name = "ds_marker"  # shell function from tree-datalad script
    out = subprocess.run(
        f"bash -c 'source tree-datalad && {function_name}'",
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return out.stdout.splitlines()[0]


@pytest.fixture(scope="session")
def has_dataset_marker(ds_marker):
    """Function to check if tree output line has been marked as dataset"""

    def _has_dataset_marker(line: str) -> bool:
        return line.endswith(ds_marker)

    return _has_dataset_marker


@pytest.fixture(scope="session")
def extract_path(ds_marker):
    """
    Function to extract path from line of 'tree'/'tree-datalad' output.
    Calls the function from the tree-datalad shell script by sourcing the script.
    """

    def _extract_path(line: str) -> str:
        out = subprocess.run(
            f"bash -c \"source tree-datalad && extract_path '{line}'\"",
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
        path_raw = out.stdout.splitlines()[0]
        return path_raw.removesuffix(ds_marker)  # strip DS marker if present

    return _extract_path


def is_datalad_dataset(path: str) -> bool:
    """Function to check if a given path is a dataset using the DataLad API"""
    try:
        if path is None or path == "":
            return False

        Path(path).resolve(strict=True)  # raise exception if path does not exist
        require_dataset(path, check_installed=True)
        return True
    except (FileNotFoundError, NoDatasetFound):
        return False


# --- Pytest hooks
def pytest_make_parametrize_id(config, val, argname):
    if isinstance(val, list):
        return f"{argname}={val}"
    if isinstance(val, int):
        return f"{argname}={val}"
    # return None to let pytest handle the formatting
    return None
