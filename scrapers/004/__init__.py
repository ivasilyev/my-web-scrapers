#%%

import networkx as nx
import numpy as np
import os
import subprocess as sp
from collections import deque
from fake_useragent import UserAgent
from matplotlib import pyplot as plt
from selenium import webdriver
from selenium.webdriver.common.by import By

from scrapers.utils import (
    dump_tsv,
    load_dict,
)

graph = nx.DiGraph()

secret_dict = load_dict("secret.json")
user_agent = UserAgent().random


proc = sp.Popen([
    secret_dict["driver_bin"],
    "--incognito",
    "--remote-debugging-port={}".format(secret_dict["driver_port"]),
    "--user-agent={}".format(user_agent),
    "--window-size={}".format(secret_dict["driver_window_sizes"]),
    secret_dict["main_url"],
])

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option(
    "debuggerAddress",
    "localhost:{}".format(secret_dict["driver_port"])
)

driver = webdriver.Chrome(options=chrome_options)



#%%

intermediate_products_table = driver.find_element(
    By.XPATH,
    "//table[@class='navbox-inner']"
)

#%%



intermediate_products_urls = deque()
intermediate_product_hrefs = intermediate_products_table.find_elements(By.TAG_NAME, "a")
for intermediate_product_href in intermediate_product_hrefs:
    if len(intermediate_product_href.find_elements(By.TAG_NAME, "img")) > 0:
        intermediate_products_urls.append(intermediate_product_href.get_attribute("href"))

driver.close()
proc.kill()
intermediate_products_urls

#%%

intermediate_products_url = intermediate_products_urls[0]
intermediate_products_url

#%%

for intermediate_products_url in intermediate_products_urls:
    print(f"Start Chrome at URL: '{intermediate_products_url}'")
    proc = sp.Popen([
        secret_dict["driver_bin"],
        "--incognito",
        "--remote-debugging-port={}".format(secret_dict["driver_port"]),
        "--user-agent={}".format(user_agent),
        "--window-size={}".format(secret_dict["driver_window_sizes"]),
        intermediate_products_url,
    ])
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option(
        "debuggerAddress",
        "localhost:{}".format(secret_dict["driver_port"])
    )
    driver = webdriver.Chrome(options=chrome_options)

    infobox_tbody = driver.find_element(
        By.XPATH,
        "//div[@class='infobox']/table/tbody"
    )
    infobox_tbody_trows = infobox_tbody.find_elements(
        By.TAG_NAME,
        "tr"
    )
    subject = os.path.basename(intermediate_products_url)
    print("Process subject: 'subject'")
    if subject not in graph:
        graph.add_node(subject)

    is_produced = False
    is_consumed = False
    for infobox_tbody_trow in infobox_tbody_trows:
        if infobox_tbody_trow.text == "Produced by":
            print("Looking for producer row")
            is_produced = True
            continue
        elif is_produced:
            print("Producer row found")
            producer_aa = infobox_tbody_trow.find_elements(By.TAG_NAME, "a")
            producer_urls = [i.get_attribute("href") for i in producer_aa]
            for producer_url in producer_urls:
                producer = os.path.basename(producer_url)
                print(f"Process producer: '{producer}' -> '{subject}'")
                if producer not in graph:
                    graph.add_node(producer)
                graph.add_edge(producer, subject)
            is_produced = False
        elif infobox_tbody_trow.text == "Consumed by":
            print("Looking for consumer row")
            is_consumed = True
            continue
        elif is_consumed:
            print("Consumer row found")
            consumer_aa = infobox_tbody_trow.find_elements(By.TAG_NAME, "a")
            consumer_urls = [i.get_attribute("href") for i in consumer_aa]
            for consumer_url in consumer_urls:
                consumer = os.path.basename(consumer_url)
                print(f"Process consumer: '{consumer}' <- '{subject}'")
                if consumer not in graph:
                    graph.add_node(consumer)
                graph.add_edge(subject, consumer)
            is_consumed = False

    print(f"Stop Chrome at URL: '{intermediate_products_url}'")
    driver.close()
    proc.kill()

#%%

plt.clf()
plt.close()
plt.rcParams.update({
    "figure.figsize": (90, 90)
})

colormap = plt.get_cmap("prism")(np.linspace(0, 1, graph.number_of_edges()))
layout = nx.shell_layout(graph)
ax = nx.draw_networkx(
    graph,
    arrows=True,
    pos=layout,
    with_labels=True,
)
nx.draw_networkx_edges(
    graph,
    edge_color=colormap,
    pos=layout,
)
text = nx.draw_networkx_labels(
    graph,
    pos=layout,
)
for _, t in text.items():
    t.set_rotation('vertical')
#edge_color=plt.get_cmap("nipy_spectral"),
plt.savefig("factorio_directed_graph.pdf")

#%%

pairs_df = nx.to_pandas_edgelist(graph)
dump_tsv(pairs_df, "pairs_table.tsv")
