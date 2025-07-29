from test_base import SQLTestCase, Menu

class TestMenuNumberValid(SQLTestCase):
    def test_page_count(self):
        res1 = self.session.query(Menu).filter(Menu.page_count < 0).all()
        self.assertEmpty(res1, 'Found Menu rows with page_count less than 0')

    def test_dish_count(self):
        res1 = self.session.query(Menu).filter(Menu.dish_count < 0).all()
        self.assertEmpty(res1, 'Found Menu rows with dish_count less than 0')