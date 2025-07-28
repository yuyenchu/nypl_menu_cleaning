from test_base import SQLTestCase, Dish

class TestDishYearValid(SQLTestCase):
    def test_first_appeared(self):
        res1 = self.session.query(Dish).filter(Dish.first_appeared < 1800).all()
        res2 = self.session.query(Dish).filter(Dish.first_appeared > 2025).all()
        self.assertEqual(len(res1), 0)
        self.assertEqual(len(res2), 0)

    def test_last_appeared(self):
        res1 = self.session.query(Dish).filter(Dish.last_appeared < 1800).all()
        res2 = self.session.query(Dish).filter(Dish.last_appeared > 2025).all()
        self.assertEqual(len(res1), 0)
        self.assertEqual(len(res2), 0)

class TestDisPriceValid(SQLTestCase):
    def test_lowest_price(self):
        res1 = self.session.query(Dish).filter(Dish.lowest_price < 0).all()
        self.assertEqual(len(res1), 0)

    def test_highest_price(self):
        res1 = self.session.query(Dish).filter(Dish.highest_price < 0).all()
        self.assertEqual(len(res1), 0)
