#%%

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
import os
import pandas as pd

from scrapers.utils import dump_tsv, load_dict


secret_dict = load_dict("secret.json")

chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("user-agent='{}'".format(secret_dict["user_agent"]))

driver = webdriver.Chrome(options=chrome_options)

#%%

driver.get(secret_dict["main_url"])

footer = WebDriverWait(driver, 30).until(
    expected_conditions.presence_of_element_located(
        (By.CLASS_NAME, secret_dict["style_footer"])
    )
)

#%%

item_dicts = list()
for unparametrized_div in driver.find_elements(
    By.XPATH,
    "//div[not(@*)]"
):
    children_div = unparametrized_div.find_elements(
        By.TAG_NAME,
        "div"
    )
    if len(children_div) == 0:
        continue
    first_child_div = children_div[0]
    if first_child_div.get_attribute("class") != secret_dict["style_category_container"]:
        continue
    categories = unparametrized_div.find_elements(
        By.CLASS_NAME,
        secret_dict["style_category_header"]
    )
    for category in categories:
        item_containers = first_child_div.find_elements(
            By.CLASS_NAME,
            secret_dict["style_menu_item_container"]
        )
        for item_container in item_containers:
            d = dict(
                category=category.text,
                title=item_container.find_element(
                    By.CLASS_NAME,
                    secret_dict["style_title"]
                ).text,
                description=item_container.find_element(
                    By.CLASS_NAME,
                    secret_dict["style_description"]
                ).text,
                price=item_container.find_element(
                    By.CLASS_NAME,
                    secret_dict["style_price"]
                ).text,
            )
            item_dicts.append(d)

#%%

driver.close()
driver.quit()
del driver

#%%

item_df = pd.DataFrame(item_dicts)
dump_tsv(item_df, os.path.join(os.getcwd(), "out.tsv"))
