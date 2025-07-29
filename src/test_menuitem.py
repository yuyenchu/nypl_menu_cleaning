from sqlalchemy import func

from test_base import SQLTestCase, MenuItem

class TestMenuItemNumberValid(SQLTestCase):
    def test_price(self):
        res1 = self.session.query(MenuItem).filter(MenuItem.price < 0).all()
        self.assertEmpty(res1, 'Found MenuItem rows with price less than 0')

    def test_high_price(self):
        res1 = self.session.query(MenuItem).filter(MenuItem.high_price < 0).all()
        self.assertEmpty(res1, 'Found MenuItem rows with high_price less than 0')

    def test_price_high_price(self):
        res1 = self.session.query(MenuItem).filter(MenuItem.high_price < MenuItem.price).all()
        self.assertEmpty(res1, 'Found MenuItem rows with high_price less than price')

    def test_xpos(self):
        res1 = self.session.query(MenuItem).filter(MenuItem.xpos < 0).all()
        res2 = self.session.query(MenuItem).filter(MenuItem.xpos > 1).all()
        self.assertEmpty(res1, 'Found MenuItem rows with xpos less than 0')
        self.assertEmpty(res2, 'Found MenuItem rows with xpos greater than 1')

    def test_ypos(self):
        res1 = self.session.query(MenuItem).filter(MenuItem.ypos < 0).all()
        res2 = self.session.query(MenuItem).filter(MenuItem.ypos > 1).all()
        self.assertEmpty(res1, 'Found MenuItem rows with ypos less than 0')
        self.assertEmpty(res2, 'Found MenuItem rows with ypos greater than 1')

class TestMenuItemDateValid(SQLTestCase):
    def test_create_update(self):
        res1 = self.session.query(MenuItem).filter(MenuItem.created_at > MenuItem.updated_at).all()
        self.assertEmpty(res1, 'Found MenuItem rows with created_at later than updated_at')