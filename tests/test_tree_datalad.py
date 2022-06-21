import pytest
from datalad.distribution.dataset import require_dataset
from datalad.support.exceptions import NoDatasetFound


def is_datalad_dataset(path: str) -> bool:
    try:
        require_dataset(path, check_installed=True)
        return True
    except NoDatasetFound:
        return False


@pytest.fixture(scope="session")
def testdir():
    """Creates a temporary directory tree on which to run the 'tree' and 'tree-datalad' commands.
    Mixes regular directories and datalad datasets.
    Will be deleted at the end of the test session."""
    yield


@pytest.fixture(scope="session", params=["-a", "-f", "--du"])
def opts(request):
    """Parametrized fixture for possible options of 'tree' command (only the subset we want to test)"""
    return request.param


@pytest.fixture(scope="session", params=[1, 4])
def depth(request):
    """Parametrized fixture for directory depth levels to be tested"""
    return request.param


@pytest.fixture(scope="function")
def tree(depth, opts, testdir):
    """Output of 'tree' command run with given options and input directory"""
    yield


@pytest.fixture(scope="session")
def extract_path():
    """Function to extract path from line of 'tree'/'tree-datalad' output.
    Calls the function from the tree-datalad shell script by sourcing the script."""
    yield


@pytest.fixture(scope="session")
def ds_marker():
    """Returns marker appended to dataset paths in the output of 'tree-datalad'.
    Calls the function from the tree-datalad shell script by sourcing the script."""
    yield


@pytest.fixture(scope="function")
def tree_datalad(depth, opts, testdir):
    """Output of 'tree-datalad' command run with given options and input directory"""
    yield


def test_valid_paths(tree, tree_datalad, extract_path):
    pass


def test_diff_from_tree_output(tree, tree_datalad, ds_marker):
    pass


def test_same_output_if_full_path_opt(tree_datalad, ds_marker):
    pass


def test_has_marker_if_dataset(tree_datalad, ds_marker):
    pass


def test_has_no_marker_if_not_dataset(tree_datalad, ds_marker):
    pass
