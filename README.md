flask-test
==========

Various unit test helpers for Flask applications


Method level setup
==================


    class TestSomeView(IntegrationTestCase):
        def test_some_method(self):
            assert True


Class level setup
==================


    class TestSomeView(IntegrationTestCase):
        def test_some_method(self):
            assert True
