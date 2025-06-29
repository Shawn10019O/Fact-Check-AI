from factchecker.reliability import get_source_reliability

def test_reliability_high():
    label, score = get_source_reliability("https://www.nature.com/articles/123")
    assert (label, score) == ("高", 3)
