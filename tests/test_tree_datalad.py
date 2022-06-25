from pathlib import Path

from conftest import is_datalad_dataset


def test_extracted_paths_are_valid(tree_datalad_full_paths, extract_path):
    """
    Test that lines of 'tree-datalad -f' output contain valid paths.
    We need to use '-f' option to print full paths (otherwise, would need to
    reconstruct path from the tree hierarchy on multiple lines).
    """
    for line in tree_datalad_full_paths:
        path = extract_path(line)
        if path:
            assert Path(path).exists()


def test_tree_output_differs_only_by_marker(tree, tree_datalad, ds_marker):
    """
    Test that outputs of 'tree' and 'tree-datalad' are identical,
    bar the dataset marker.
    """
    output_tree = "".join(tree)
    output_tree_datalad = "".join(tree_datalad)
    output_tree_datalad_stripped = output_tree_datalad.replace(ds_marker, "")
    assert output_tree == output_tree_datalad_stripped


def test_same_ds_markers_if_full_path_option(
    tree_datalad, tree_datalad_full_paths, has_dataset_marker
):
    """
    Since we test path extraction using the '-f' option,
    we need to make sure that results would be identical without the '-f' option.
    """
    marker_indices_regular_paths = [
        ix for ix, line in enumerate(tree_datalad) if has_dataset_marker(line)
    ]
    marker_indices_full_paths = [
        ix
        for ix, line in enumerate(tree_datalad_full_paths)
        if has_dataset_marker(line)
    ]
    assert marker_indices_regular_paths == marker_indices_full_paths


def test_has_marker_if_dataset(
    tree_datalad_full_paths, extract_path, has_dataset_marker
):
    """Test dataset detection (true positive case)"""
    for line in tree_datalad_full_paths:
        path = extract_path(line)
        if is_datalad_dataset(path):
            assert has_dataset_marker(line)


def test_has_no_marker_if_not_dataset(
    tree_datalad_full_paths, extract_path, has_dataset_marker
):
    """Test dataset detection (true negative case)"""
    for line in tree_datalad_full_paths:
        path = extract_path(line)
        if not is_datalad_dataset(path):
            assert not has_dataset_marker(line)
