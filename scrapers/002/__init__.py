#%%

import os
import pandas as pd
import subprocess as sp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains


from scrapers.utils import (
    dump_tsv,
    hover_and_click,
    load_dict,
    randomize_sleep,
    sanitize_float,
    scroll_upon,
)


secret_dict = load_dict("secret.json")

proc = sp.Popen([
    secret_dict["driver_bin"],
    "--incognito",
    "--remote-debugging-port={}".format(secret_dict["driver_port"]),
    "--window-size={}".format(secret_dict["driver_window_sizes"]),
    secret_dict["main_url"],
])

#%%

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("debuggerAddress", "localhost:{}".format(secret_dict["driver_port"]))

driver = webdriver.Chrome(options=chrome_options)

#%%


city_select_div = driver.find_element(
    By.CLASS_NAME,
    secret_dict["city_select_div_class"]
)

confirm_city_span = city_select_div.find_element(
    By.CLASS_NAME,
    secret_dict["confirm_city_span_class"]
)

if confirm_city_span.text != secret_dict["target_city"]:
    hover_and_click(driver, city_select_div)

city_table_div = driver.find_element(
    By.CLASS_NAME,
    secret_dict["city_table_div_class"]
)

for district_li in driver.find_elements(
    By.CLASS_NAME,
    secret_dict["district_li_class"]
):
    try:
        district_name = district_li.text
        if district_name == secret_dict["target_district"]:
            hover_and_click(driver, district_li)
    except StaleElementReferenceException:
        pass


for region_li in driver.find_elements(
    By.CLASS_NAME,
    secret_dict["region_li_class"]
):
    try:
        region_name = region_li.text
        if region_name == secret_dict["target_region"]:
            hover_and_click(driver, region_li)
    except StaleElementReferenceException:
        pass


for city_li in driver.find_elements(
    By.CLASS_NAME,
    secret_dict["city_li_class"]
):
    try:
        city_name = city_li.text
        if city_name == secret_dict["target_city"]:
            scroll_upon(driver, city_li)
            hover_and_click(driver, city_li)
        else:
            driver.execute_script("window.scrollTo(0, 30);")
    except StaleElementReferenceException:
        pass


#%%


driver.find_element(By.CLASS_NAME, secret_dict["catalog_spoiler_class"]).click()


for catalog_div in driver.find_elements(By.CLASS_NAME, secret_dict["catalog_div_class"]):
    catalog_div_name = catalog_div.text
    hover = ActionChains(driver).move_to_element(catalog_div)
    hover.perform()
    randomize_sleep(1)
    if catalog_div_name == secret_dict["target_category_name"]:
        driver.execute_script("arguments[0].click();", catalog_div)
        break

catalog_submenu_div = driver.find_element(
    By.CLASS_NAME,
    secret_dict["catalog_submenu_div_class"]
)


for catalog_submenu_span in catalog_submenu_div.find_elements(By.TAG_NAME, "span"):
    try:
        randomize_sleep(1)
        if catalog_submenu_span.text == secret_dict["target_subcategory_name"]:
            hover_and_click(driver, catalog_submenu_span)
            break
    except StaleElementReferenceException:
        pass


#%%


page_as = driver.find_elements(
    By.CLASS_NAME,
    secret_dict["page_a_class"]
)

item_dicts = list()
for page_number in range(len(page_as)):
    page_number += 1
    if page_number > 1:
        page_a = [
            i for i in driver.find_elements(
                By.CLASS_NAME,
                secret_dict["page_a_class"]
            )
            if i.text == str(page_number)
        ][0]
        hover_and_click(driver, page_a)
        randomize_sleep(5)
        footer = WebDriverWait(driver, 30).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, secret_dict["footer_class"])
            )
        )
    product_divs = driver.find_elements(
        By.CLASS_NAME,
        secret_dict["product_div_class"]
    )
    for product_div in product_divs:
        scroll_upon(driver, product_div)
        title = product_div.find_element(
            By.CLASS_NAME,
            secret_dict["product_name_span_class"]
        ).text
        price = sanitize_float(
            product_div.find_element(
                By.CLASS_NAME,
                secret_dict["product_price_span_class"]
            ).text
        )
        item_dicts.append(dict(
            category=secret_dict["target_category_name"],
            subcategory=secret_dict["target_subcategory_name"],
            title=title,
            price=price,
        ))


#%%

item_df = pd.DataFrame(item_dicts)
dump_tsv(item_df, os.path.join(os.getcwd(), "out.tsv"))

#%%

proc.kill()
