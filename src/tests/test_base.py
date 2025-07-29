import contextvars
import json
import logging
import os
import time
import unittest
from sqlalchemy import (
    create_engine, 
    event,
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
RED     = '\033[31m'
GREEN   = '\033[32m'
YELLOW  = '\033[33m'
BLUE    = '\033[34m'
MAGENTA = '\033[35m'
CYAN    = '\033[36m'
RESET   = '\033[0m'

Base = declarative_base()
logger = logging.getLogger(__name__)
_current_test_id = contextvars.ContextVar('current_test_id', default='UNKNOWN')

def register_current_test(testcase_instance):
    # Registers the current test case ID from a unittest.TestCase instance
    _current_test_id.set(testcase_instance.id())

def setup_query_logger(engine, file_path='queries.txt'):
    # Always overwrite the file at start
    with open(file_path, 'w') as f:
        f.write('--- SQL Query Log ---\n')

    @event.listens_for(engine, 'before_cursor_execute')
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        test_id = _current_test_id.get()
        with open(file_path, 'a') as f:
            f.write(f'\n## Test: {test_id}\nSQL: {statement}\nParams: {parameters}\n')

class ConditionalFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, 'simple') and record.simple:
            return record.getMessage()
        else:
            return super().format(record)

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
    
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
    image_id = Column(Text)
    full_height = Column(Integer)
    full_width = Column(Integer)
    uuid = Column(String(36))  # UUIDs are typically 36 chars

class SQLTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ENGINE
        cls.logger = logger
        cls.logger.info(f'===> {MAGENTA}{cls.__name__}{RESET} <===')
        setup_query_logger(cls.engine)
        cls.clsStartTime = time.time()
        cls.failedIds = dict()

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose() # Dispose of the engine
        t = time.time() - cls.clsStartTime
        cls.logger.info(f'{MAGENTA}{cls.__name__}{RESET} Finish: {t:.4f}s')
        cls.logger.info('='*70, extra={'simple': True})
        with open(f'{cls.__name__}_FailedID.json', 'w') as f:
            json.dump(cls.failedIds, f, cls=SetEncoder)
    def setUp(self):
        # Create a new session for each test
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.startTime = time.time()
        self.fails = set()
        self.delay_asserts = []
        self.failedIds[self._testMethodName] = self.fails
        register_current_test(self)

    def tearDown(self):
        # Rollback and close the session after each test
        self.session.rollback() # Ensure changes are not persisted between tests
        self.session.close()
        t = time.time() - self.startTime
        self.logger.info(f'Finish: {t:.4f}s')

    def _callTestMethod(self, method):
        super()._callTestMethod(method)
        for asserter, args in self.delay_asserts:
            asserter(*args)

    def assertEmpty(self, res, msg=None):
        self.recordFails(res)
        self.delay_asserts.append((self.assertEqual, (len(res), 0, msg)))

    def recordFails(self, fails):
        if (not fails):
            return
        if (isinstance(fails, list)):
            self.fails.update([f.id for f in fails])
        else:
            self.add(fails)
class LoggerTestResult(unittest.TextTestResult):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.success = []

    def startTest(self, test):
        super().startTest(test)
        self.logger.info('', extra={'simple': True})
        self.logger.info(f'START => {CYAN}{test._testMethodName}{RESET}')

    def addSuccess(self, test):
        super().addSuccess(test)
        self.success.append(test)
        self.logger.info(f'Result: {GREEN}PASS{RESET}')

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.logger.info(f'Result: {RED}FAIL{RESET}\n{self._exc_info_to_string(err, test)}')

    def addError(self, test, err):
        super().addError(test, err)
        self.logger.error(f'ERROR: {test._testMethodName}\n{self._exc_info_to_string(err, test)}')

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.logger.warning(f'SKIP: {test._testMethodName} - {reason}')

class LoggerTestRunner(unittest.TextTestRunner):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs, stream=open(os.devnull, 'w'))
        self.logger = logger

    def _makeResult(self):
        return LoggerTestResult(self.logger, self.stream, self.descriptions, self.verbosity)

class TestTablesSchema(SQLTestCase):
    def test_dish(self):
        ### Check if 'Dish' table exists
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table('Dish'), 'Table "Dish" does not exist')
        rows = self.session.scalar(select(func.count()).select_from(Dish))
        self.assertEqual(rows, 423397, 'Dish rows missing')
        
    def test_menu(self):
        ### Check if 'Menu' table exists
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table('Menu'), 'Table "Menu" does not exist')
        rows = self.session.scalar(select(func.count()).select_from(Menu))
        self.assertEqual(rows, 17545, 'Menu rows missing')
        
    def test_menu_page(self):
        ### Check if 'MenuPage' table exists
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table('MenuPage'), 'Table "MenuPage" does not exist')
        rows = self.session.scalar(select(func.count()).select_from(MenuPage))
        self.assertEqual(rows, 66937, 'MenuPage rows missing')
        
    def test_menu_item(self):
        ### Check if 'MenuItem' table exists
        inspector = inspect(self.engine)
        self.assertTrue(inspector.has_table('MenuItem'), 'Table "MenuItem" does not exist')
        rows = self.session.scalar(select(func.count()).select_from(MenuItem))
        self.assertEqual(rows, 1332726, 'MenuItem rows missing')
        
    def test_menu_page_menu_id_fk(self):
        ### Check MenuPage.menu_id references existing Menu.id
        invalid_pages = (
            self.session.query(MenuPage)
            .outerjoin(Menu, MenuPage.menu_id == Menu.id)
            .filter(Menu.id == None)
            .all()
        )
        self.assertEmpty(invalid_pages, 'Found MenuPage rows with invalid menu_id')

    def test_menu_item_dish_id_fk(self):
        ### Check MenuItem.dish_id references existing Dish.id
        invalid_items = (
            self.session.query(MenuItem)
            .outerjoin(Dish, MenuItem.dish_id == Dish.id)
            .filter(Dish.id == None)
            .all()
        )
        self.assertEmpty(invalid_items, 'Found MenuItem rows with invalid dish_id')

    def test_menu_item_menu_page_id_fk(self):
        ### Check MenuItem.menu_page_id references existing MenuPage.id
        invalid_items = (
            self.session.query(MenuItem)
            .outerjoin(MenuPage, MenuItem.menu_page_id == MenuPage.id)
            .filter(MenuPage.id == None)
            .all()
        )
        self.assertEmpty(invalid_items, 'Found MenuItem rows with invalid menu_page_id')