import logging
import unittest
from sqlalchemy import (
    create_engine, 
    func, 
    select,
    inspect, 
    Column, 
    ForeignKey,
    DateTime,
    Float, 
    Integer, 
    String, 
    Text, 
    CheckConstraint
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

USERNAME = 'devuser'
PASSWORD = 'devpass'
# create a SQLAlchemy engine
ENGINE = create_engine(f'mysql+mysqlconnector://{USERNAME}:{PASSWORD}@mysql/devdb')

Base = declarative_base()
logger = logging.getLogger(__name__)

class Dish(Base):
    __tablename__ = 'Dish'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    menus_appeared = Column(Integer)
    times_appeared = Column(Integer)
    first_appeared = Column(Integer)
    last_appeared = Column(Integer)
    lowest_price = Column(Float)
    highest_price = Column(Float)

    __table_args__ = (
        CheckConstraint('first_appeared BETWEEN 0 AND 9999'),
        CheckConstraint('last_appeared BETWEEN 0 AND 9999'),
    )

class Menu(Base):
    __tablename__ = 'Menu'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    sponsor = Column(Text)
    event = Column(Text)
    venue = Column(Text)
    place = Column(Text)
    physical_description = Column(Text)
    occasion = Column(Text)
    notes = Column(Text)
    call_number = Column(Text)
    keywords = Column(Text)
    language = Column(Text)
    date = Column(Text)
    location = Column(Text)
    location_type = Column(Text)
    currency = Column(Text)
    currency_symbol = Column(Text)
    status = Column(Text)
    page_count = Column(Integer)
    dish_count = Column(Integer)

class MenuItem(Base):
    __tablename__ = 'MenuItem'

    id = Column(Integer, primary_key=True)
    menu_page_id = Column(Integer)  # ForeignKey('MenuPage.id'), not added for later testcases
    price = Column(Float, nullable=True)
    high_price = Column(Float, nullable=True)
    dish_id = Column(Integer)  # ForeignKey('Dish.id'), not added for later testcases
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    xpos = Column(Float)
    ypos = Column(Float)

class MenuPage(Base):
    __tablename__ = 'MenuPage'

    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer)  # ForeignKey('Menu.id'), not added for later testcases
    page_number = Column(Integer)
    image_id = Column(Integer)
    full_height = Column(Integer)
    full_width = Column(Integer)
    uuid = Column(String(36))  # UUIDs are typically 36 chars

class SQLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ENGINE

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose() # Dispose of the engine
    
    def setUp(self):
        # Create a new session for each test
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def tearDown(self):
        # Rollback and close the session after each test
        self.session.rollback() # Ensure changes are not persisted between tests
        self.session.close()

class LoggerTestResult(unittest.TextTestResult):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger

    def startTest(self, test):
        super().startTest(test)
        self.logger.info(f"START: {test}")

    def addSuccess(self, test):
        super().addSuccess(test)
        self.logger.info(f"PASS: {test}")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.logger.error(f"FAIL: {test}\n{self._exc_info_to_string(err, test)}")

    def addError(self, test, err):
        super().addError(test, err)
        self.logger.error(f"ERROR: {test}\n{self._exc_info_to_string(err, test)}")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.logger.warning(f"SKIP: {test} - {reason}")

class LoggerTestRunner(unittest.TextTestRunner):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger

    def _makeResult(self):
        return LoggerTestResult(self.logger, self.stream, self.descriptions, self.verbosity)

class TestTablesSchema(SQLTestCase):
    def test_dish(self):
        ### Check if 'Dish' table exists
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table('Dish'), 'Table "Dish" does not exist')
        rows = self.session.scalar(select(func.count()).select_from(Dish))
        self.assertEqual(rows, 423397)
        
    def test_menu(self):
        ### Check if 'Menu' table exists
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table('Menu'), 'Table "Menu" does not exist')
        rows = self.session.scalar(select(func.count()).select_from(Menu))
        self.assertEqual(rows, 17545)
        
    def test_menu_page(self):
        ### Check if 'MenuPage' table exists
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table('MenuPage'), 'Table "MenuPage" does not exist')
        rows = self.session.scalar(select(func.count()).select_from(MenuPage))
        self.assertEqual(rows, 66937)
        
    def test_menu_item(self):
        ### Check if 'MenuItem' table exists
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table('MenuItem'), 'Table "MenuItem" does not exist')
        rows = self.session.scalar(select(func.count()).select_from(MenuItem))
        self.assertEqual(rows, 1332726)
        
    def test_menu_page_menu_id_fk(self):
        ### Check MenuPage.menu_id references existing Menu.id
        invalid_pages = (
            self.session.query(MenuPage)
            .outerjoin(Menu, MenuPage.menu_id == Menu.id)
            .filter(Menu.id == None)
            .all()
        )
        self.assertFalse(invalid_pages, f'Found MenuPage rows with invalid menu_id: {[p.id for p in invalid_pages]}')
        if (invalid_pages):
            logger.error('MenuPage invalid menu_id rows: %s', [p.id for p in invalid_pages])

    def test_menu_item_dish_id_fk(self):
        ### Check MenuItem.dish_id references existing Dish.id
        invalid_items = (
            self.session.query(MenuItem)
            .outerjoin(Dish, MenuItem.dish_id == Dish.id)
            .filter(Dish.id == None)
            .all()
        )
        self.assertFalse(invalid_items, f'Found MenuItem rows with invalid dish_id: {[i.id for i in invalid_items]}')
        if (invalid_items):
            logger.error('MenuItem invalid dish_id rows: %s', [i.id for i in invalid_items])

    def test_menu_item_menu_page_id_fk(self):
        ### Check MenuItem.menu_page_id references existing MenuPage.id
        invalid_items = (
            self.session.query(MenuItem)
            .outerjoin(MenuPage, MenuItem.menu_page_id == MenuPage.id)
            .filter(MenuPage.id == None)
            .all()
        )
        self.assertFalse(invalid_items, f'Found MenuItem rows with invalid menu_page_id: {[i.id for i in invalid_items]}')
        if (invalid_items):
            logger.error('MenuItem invalid menu_page_id rows: %s', [i.id for i in invalid_items])
