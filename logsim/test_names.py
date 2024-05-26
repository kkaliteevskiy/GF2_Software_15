"""Test the mynames module."""
import pytest

from names import Names


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()

def test_default_initial_name(new_names):
    assert new_names.names == []
    assert new_names.error_code_count == 0

def test_unique_error_codes(new_names):
    new_names.unique_error_codes(0)
    assert new_names.error_code_count == 0

def test_unique_error_codes_raises_exception(new_names):
    with pytest.raises(TypeError):
        new_names.unique_error_codes('i')
    with pytest.raises(TypeError):
        new_names.unique_error_codes(0.9)


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Alice", "Bob", "Eve"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    my_name.lookup(name_string_list)
    return my_name

@pytest.mark.parametrize("expected_name_id, name_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
])

def test_query(new_names, used_names, expected_name_id, name_string):
    assert new_names.query(name_string) == None
    assert used_names.query(name_string) == expected_name_id


@pytest.mark.parametrize("expected_name_ids, string_list", [
    ([0], ["Alice"]),
    ([1, 2], ["Bob", "Eve"]),
    ([2, 3], ["Eve", "Alex"]), 
    ([3, 4, 5, 6], ['a', 'b', 'c', 'd']),
])

def test_lookup(used_names, string_list, expected_name_ids):
    assert used_names.lookup(string_list) == expected_name_ids

# add test to check if invalid name (according EBNF)
def test_lookup_raises_exception(used_names):
    with pytest.raises(TypeError):
        used_names.lookup("Alice")
    with pytest.raises(TypeError):
        used_names.lookup(12)
    with pytest.raises(TypeError):
        used_names.lookup(['a', 12])
    with pytest.raises(TypeError):
        used_names.lookup(['13', 'a12'])
    with pytest.raises(TypeError):
        used_names.lookup(['1gf', 'a12'])

@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
    (3, None),
])

def test_get_name_string(new_names, used_names, name_id, expected_string):
    assert new_names.get_name_string(name_id) == None
    assert used_names.get_name_string(name_id) == expected_string

# check input id is an int
def test_get_name_string_raises_exception(used_names):
    with pytest.raises(TypeError):
        used_names.get_name_string("Alice")
    with pytest.raises(TypeError):
        used_names.get_name_string(0.4)
    with pytest.raises(ValueError):
        used_names.get_name_string(-6)



# parameterized test cannot be used twice?
