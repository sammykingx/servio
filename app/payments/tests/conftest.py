import pytest

def pytest_collection_modifyitems(items):
    """
    Automatically assigns markers based on the directory name.
    If a test is in a folder named 'unit', it gets the 'unit' marker.
    """
    for item in items:
        path = str(item.fspath)
        
        if "/unit/" in path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in path:
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in path:
            item.add_marker(pytest.mark.e2e)