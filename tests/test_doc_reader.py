from factchecker.doc_reader import sanitize_text

def test_sanitize_text():
    raw = "foo   bar \n\nbaz"
    assert sanitize_text(raw) == "foo bar\nbaz"
