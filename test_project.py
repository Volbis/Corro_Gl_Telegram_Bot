import pytest
from project import (
    count_files_by_subject,
    get_file_statistics,
    format_message,
    truncate_text,
    get_safe_value
)


# Test pour count_files_by_subject
def test_count_files_by_subject():
    # Mock des données
    test_semester = "Semestre 1"
    test_part = "Partie 1"
    
    result = count_files_by_subject(test_semester, test_part)
    
    assert isinstance(result, dict)
    # Vérifie que chaque matière a les bonnes clés
    for subject_data in result.values():
        assert 'pdf' in subject_data
        assert 'images' in subject_data
        assert 'total' in subject_data
        assert subject_data['total'] == subject_data['pdf'] + subject_data['images']

# Test pour get_file_statistics
def test_get_file_statistics():
    stats = get_file_statistics()
    
    # Vérifie la présence de toutes les clés requises
    expected_keys = {'total_pdf', 'total_images', 'subjects_with_files', 'empty_subjects'}
    assert all(key in stats for key in expected_keys)
    
    # Vérifie que les valeurs sont des entiers positifs
    assert all(isinstance(stats[key], int) and stats[key] >= 0 for key in stats)

# Test pour format_message
def test_format_message():
    # Test avec un dictionnaire simple
    title = "Test Title"
    content = {"key1": "value1", "key2": "value2"}
    
    formatted = format_message(title, content, add_separators=True)
    
    assert "*Test Title*" in formatted
    assert "key1: value1" in formatted
    assert "key2: value2" in formatted

def test_format_message_nested():
    # Test avec un dictionnaire imbriqué
    title = "Nested Test"
    content = {
        "main": {
            "sub1": "value1",
            "sub2": "value2"
        }
    }
    
    formatted = format_message(title, content, add_separators=False)
    
    assert "*Nested Test*" in formatted
    assert "*main*:" in formatted
    assert "sub1: value1" in formatted
    assert "sub2: value2" in formatted

# Test pour truncate_text
def test_truncate_text():
    # Test sans troncature nécessaire
    assert truncate_text("Court texte", 20) == "Court texte"
    
    # Test avec troncature
    assert truncate_text("Un texte très long", 10) == "Un text..."
    
    # Test avec longueur exacte
    assert truncate_text("Exact", 5) == "Exact"
    
    # Test avec une chaîne vide
    assert truncate_text("", 5) == ""
    
    # Test avec une longueur plus courte
    assert truncate_text("Test", 3) == "..."

# Test pour get_safe_value
def test_get_safe_value():
    # Test dictionnaire simple
    test_dict = {"a": 1, "b": {"c": 2}}
    
    assert get_safe_value(test_dict, "a") == 1
    assert get_safe_value(test_dict, "b", "c") == 2
    assert get_safe_value(test_dict, "nonexistent") is None
    assert get_safe_value(test_dict, "b", "nonexistent") is None
    
    # Test avec valeur par défaut personnalisée
    assert get_safe_value(test_dict, "nonexistent", default="default") == "default"

def test_get_safe_value_empty():
    # Test avec dictionnaire vide
    empty_dict = {}
    assert get_safe_value(empty_dict, "any_key") is None
    
    # Test avec None
    assert get_safe_value(None, "any_key") is None