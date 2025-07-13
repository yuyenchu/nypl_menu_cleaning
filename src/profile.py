import pandas as pd

if __name__=='__main__':
    menu_page = pd.read_csv('/home/dev/MenuPage.csv')
    print(menu_page.head())