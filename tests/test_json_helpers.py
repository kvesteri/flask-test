from flask_test import (
    CreateTestMixin,
    UpdateTestMixin,
    DeleteTestMixin,
    ShowTestMixin,
    IndexTestMixin,
)
from tests import BasicTestCase


class TestTagResource(
        BasicTestCase,
        CreateTestMixin,
        UpdateTestMixin,
        DeleteTestMixin,
        ShowTestMixin,
        IndexTestMixin):
    resource = 'tag'
    identifier = 'tag_id'
