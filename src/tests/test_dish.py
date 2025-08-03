from .test_base import SQLTestCase, Dish

class TestDishYearValid(SQLTestCase):
    ### Check Dish.first_appeared year is between 1500 and 2025
    def test_first_appeared(self):
        res1 = self.session.query(Dish).filter(Dish.first_appeared < 1500).all()
        res2 = self.session.query(Dish).filter(Dish.first_appeared > 2025).all()
        self.assertEmpty(res1, 'Found Dish rows with first_appeared less than 1500')
        self.assertEmpty(res2, 'Found Dish rows with first_appeared greater than 2025')

    ### Check Dish.last_appeared year is between 1500 and 2025
    def test_last_appeared(self):
        res1 = self.session.query(Dish).filter(Dish.last_appeared < 1500).all()
        res2 = self.session.query(Dish).filter(Dish.last_appeared > 2025).all()
        self.assertEmpty(res1, 'Found Dish rows with last_appeared less than 1500')
        self.assertEmpty(res2, 'Found Dish rows with last_appeared greater than 2025')

class TestDisPriceValid(SQLTestCase):
    ### Check Dish.lowest_price has no negative values
    def test_lowest_price(self):
        res1 = self.session.query(Dish).filter(Dish.lowest_price < 0).all()
        self.assertEmpty(res1, 'Found Dish rows with lowest_price less than 0')

    ### Check Dish.highest_price has no negative values
    def test_highest_price(self):
        res1 = self.session.query(Dish).filter(Dish.highest_price < 0).all()
        self.assertEmpty(res1, 'Found Dish rows with highest_price less than 0')