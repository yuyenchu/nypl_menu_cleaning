from sqlalchemy import func

from test_base import SQLTestCase, MenuPage

class TestMenuPageNumberValid(SQLTestCase):
    def test_page_number(self):
        res1 = self.session.query(MenuPage).filter(MenuPage.page_number < 0).all()
        self.assertEmpty(res1, 'Found MenuPage rows with page_number less than 0')

    def test_full_height(self):
        res1 = self.session.query(MenuPage).filter(MenuPage.full_height < 0).all()
        self.assertEmpty(res1, 'Found MenuPage rows with full_height less than 0')

    def test_full_width(self):
        res1 = self.session.query(MenuPage).filter(MenuPage.full_width < 0).all()
        self.assertEmpty(res1, 'Found MenuPage rows with full_width less than 0')

class TestMenuPageDuplicate(SQLTestCase):
    def test_uuid(self):
        res1 = (
            self.session.query(MenuPage.uuid)
            .group_by(MenuPage.uuid)
            .having(func.count(MenuPage.uuid) > 1)
            .subquery()
        )
        res2 = (
            self.session.query(MenuPage)
            .filter(MenuPage.uuid.in_(res1))
            .all()
        )

        self.assertEmpty(res2, 'Found MenuPage rows with duplicated uuid')