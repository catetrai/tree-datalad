from pathlib import Path
import subprocess
import pytest
from datalad import api as dl
from datalad.distribution.dataset import require_dataset
from datalad.support.exceptions import NoDatasetFound


def is_datalad_dataset(path: str) -> bool:
    try:
        require_dataset(path, check_installed=True)
        return True
    except NoDatasetFound:
        return False


@pytest.fixture(scope="session")
def has_dataset_marker(ds_marker):
    """Function to check if tree output line has been marked as dataset"""

    def _has_dataset_marker(line: str) -> bool:
        return line.endswith(ds_marker)

    return _has_dataset_marker


@pytest.fixture(scope="session")
def testdir(tmp_path_factory):
    """
    Creates a temporary directory tree on which to run the 'tree' and 'tree-datalad' commands.
    Uses pytest's `tmp_path_factory` session fixture to create a temp dir that will be deleted
    at the end of the test session.
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


@pytest.fixture(scope="session", params=["-a", "-f", "--du"])
def opts(request):
    """Parametrized fixture for possible options of 'tree' command (only the subset we want to test)"""
    return request.param


@pytest.fixture(scope="session", params=[1, 4])
def depth(request):
    """Parametrized fixture for directory depth levels to be tested"""
    return request.param


@pytest.fixture(scope="function")
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
    return _tree_like_command("tree-datalad", depth, opts + "-f", testdir)


def test_extracted_paths_are_valid(tree_datalad, extract_path):
    """Test that lines of tree-datalad output contain valid paths"""
    for line in tree_datalad:
        path = extract_path(line)
        if path:
            assert Path(path).exists()


def test_tree_output_differs_only_by_marker(tree, tree_datalad, ds_marker):
    output_tree = "".join(tree)
    output_tree_datalad = "".join(tree_datalad)
    output_tree_datalad_stripped = output_tree_datalad.replace(ds_marker, "")
    assert output_tree == output_tree_datalad_stripped


def test_same_ds_markers_if_full_path_option(
    tree_datalad, tree_datalad_full_paths, has_dataset_marker
):
    marker_indices_regular_paths = [
        ix for ix, line in enumerate(tree_datalad) if has_dataset_marker(line)
    ]
    marker_indices_full_paths = [
        ix
        for ix, line in enumerate(tree_datalad_full_paths)
        if has_dataset_marker(line)
    ]
    assert marker_indices_regular_paths == marker_indices_full_paths


def test_has_marker_if_dataset(tree_datalad, extract_path, has_dataset_marker):
    for line in tree_datalad:
        path = extract_path(line)
        if is_datalad_dataset(path):
            assert has_dataset_marker(line)


def test_has_no_marker_if_not_dataset(tree_datalad, extract_path, has_dataset_marker):
    for line in tree_datalad:
        path = extract_path(line)
        if not is_datalad_dataset(path):
            assert not has_dataset_marker(line)
