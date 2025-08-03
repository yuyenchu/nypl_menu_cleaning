from sqlalchemy import text

from .test_base import SQLTestCase, Menu

class TestMenuNumberValid(SQLTestCase):
    ### Check Menu.page_count has no negative values
    def test_page_count(self):
        res1 = self.session.query(Menu).filter(Menu.page_count < 0).all()
        self.assertEmpty(res1, 'Found Menu rows with page_count less than 0')

    ### Check Menu.dish_count has no negative values
    def test_dish_count(self):
        res1 = self.session.query(Menu).filter(Menu.dish_count < 0).all()
        self.assertEmpty(res1, 'Found Menu rows with dish_count less than 0')

class TestMenuDateValid(SQLTestCase):
    ### Check Menu.date is valid and parseable
    def test_date_parseable(self):
        query = text("""
            SELECT id, date FROM Menu
            WHERE STR_TO_DATE(date, '%Y-%m-%d') IS NULL
        """)
        res1 = self.session.execute(query).fetchall()
        self.assertEmpty(res1, 'Found Menu rows with non parseable date')

    ### Check Menu.date is not later than 2025
    def test_date_valid(self):
        query = text("""
            SELECT id, date
            FROM Menu
            WHERE 
              STR_TO_DATE(date, '%Y-%m-%d') IS NOT NULL AND
              YEAR(STR_TO_DATE(date, '%Y-%m-%d')) > 2025
        """)
        res1 = self.session.execute(query).fetchall()
        self.assertEmpty(res1, 'Found Menu rows with year greater than 2025')