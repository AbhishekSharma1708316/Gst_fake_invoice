import pytest

from string_match import find_suspicious_name_pairs, levenshtein_distance


@pytest.mark.parametrize("a,b,expected", [
    ("kitten", "sitting", 3),
    ("flaw", "lawn", 2),
    ("abc", "abc", 0),
    ("", "abc", 3),
    ("abc", "", 3),
    ("", "", 0),
    ("a", "b", 1),
])
def test_known_distances(a, b, expected):
    assert levenshtein_distance(a, b) == expected


def test_distance_is_symmetric():
    assert levenshtein_distance("Shreeji Trading Co", "Shreeji Traderz Co") == \
           levenshtein_distance("Shreeji Traderz Co", "Shreeji Trading Co")


def test_distance_ignores_case_and_outer_whitespace():
    assert levenshtein_distance("  ACME Traders ", "acme traders") == 0


def test_similar_names_are_flagged():
    pairs = find_suspicious_name_pairs(
        ["Shreeji Trading Co", "Shreeji Traderz Co", "Kaveri Chemicals Ltd"]
    )
    assert len(pairs) == 1
    assert {pairs[0]["name_a"], pairs[0]["name_b"]} == \
           {"Shreeji Trading Co", "Shreeji Traderz Co"}
    assert pairs[0]["edit_distance"] == 3


def test_single_character_difference_is_flagged():
    pairs = find_suspicious_name_pairs(
        ["Ashirwad Metal Pvt Ltd", "Ashirwad Metals Pvt Ltd"]
    )
    assert len(pairs) == 1
    assert pairs[0]["edit_distance"] == 1


def test_unrelated_names_are_not_flagged():
    assert find_suspicious_name_pairs(
        ["Kaveri Chemicals Ltd", "Om Sai Logistics", "Prime Auto Parts"]
    ) == []


def test_same_firm_repeated_is_not_flagged():
    names = ["Om Sai Logistics"] * 5 + ["Prime Auto Parts"]
    assert find_suspicious_name_pairs(names) == []


def test_threshold_is_respected():
    names = ["Shreeji Trading Co", "Shreeji Traderz Co"]  # distance 3
    assert len(find_suspicious_name_pairs(names, max_distance=3)) == 1
    assert find_suspicious_name_pairs(names, max_distance=2) == []


def test_each_pair_is_reported_once():
    pairs = find_suspicious_name_pairs(["abcd", "abce", "abcf"], max_distance=1)
    keys = {frozenset((p["name_a"], p["name_b"])) for p in pairs}
    assert len(pairs) == len(keys) == 3
