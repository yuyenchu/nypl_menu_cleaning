from test_base import SQLTestCase, Dish

class TestDishYearValid(SQLTestCase):
    def test_first_appeared(self):
        res1 = self.session.query(Dish).filter(Dish.first_appeared < 1500).all()
        res2 = self.session.query(Dish).filter(Dish.first_appeared > 2025).all()
        self.assertEmpty(res1, 'Found Dish rows with first_appeared less than 1500')
        self.assertEmpty(res2, 'Found Dish rows with first_appeared greater than 2025')

    def test_last_appeared(self):
        res1 = self.session.query(Dish).filter(Dish.last_appeared < 1500).all()
        res2 = self.session.query(Dish).filter(Dish.last_appeared > 2025).all()
        self.assertEmpty(res1, 'Found Dish rows with last_appeared less than 1500')
        self.assertEmpty(res2, 'Found Dish rows with last_appeared greater than 2025')

class TestDisPriceValid(SQLTestCase):
    def test_lowest_price(self):
        res1 = self.session.query(Dish).filter(Dish.lowest_price < 0).all()
        self.assertEmpty(res1, 'Found Dish rows with lowest_price less than 0')

    def test_highest_price(self):
        res1 = self.session.query(Dish).filter(Dish.highest_price < 0).all()
        self.assertEmpty(res1, 'Found Dish rows with highest_price less than 0')