from .test_base import *
from .test_dish import *
from .test_menu import *
from .test_menupage import *
from .test_menuitem import *

TABLE_MAP = {
    'Dish': Dish,
    'Menu': Menu,
    'MenuPage': MenuPage,
    'MenuItem': MenuItem,
}
TEST_GROUPS = {
    'schema': [TestTablesSchema],
    'dish': [TestDishYearValid, TestDisPriceValid],
    'menu': [TestMenuNumberValid, TestMenuDateValid],
    'menupage': [TestMenuPageNumberValid, TestMenuPageDuplicate],
    'menuitem': [TestMenuItemNumberValid, TestMenuItemDateValid],
}