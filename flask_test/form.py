from .base import BaseTestCase
from wtforms_test import FormTestCase as _FormTestCase


class FormTestCase(BaseTestCase, _FormTestCase):
    pass
