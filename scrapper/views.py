from rest_framework.views import APIView
from rest_framework.response import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from rest_framework import status
import pandas as pd
import time
import datetime
from .scrapper_utils import getlinks, product_scraper


class MattressScrapperView(APIView):
    driver = webdriver.Firefox()
    driver.maximize_window()

    def get(self, request, asin):
        """
        Function to get product urls from main page,
        call product scraper to get raw data and return the response
        """

        # Getting the home page url of Amazon and wait to load
        url = "https://www.amazon.in/"
        self.driver.get(url)
        time.sleep(15)

        # Clicking on the delivery to box to change to the desired pin
        self.driver.find_element(By.ID, "nav-global-location-popover-link").click()
        time.sleep(3)
        pin = self.driver.find_element(By.ID, "GLUXZipInputSection").find_element(By.TAG_NAME, "input")
        pin.clear()

        # Passing the zip code and wait then apply
        pin.send_keys("560038")  # hard coded
        time.sleep(3)
        self.driver.find_element(By.ID, "GLUXZipInputSection").find_element(By.CLASS_NAME, "a-button-input").click()

        # Calling the function to get links
        links = getlinks(self.driver, asin)

        # Creating a dataframe to merge all the data which are coming from product scraper
        final_df = pd.DataFrame()
        count = 0

        # Iterating through the list of urls and concating dataframes
        for num, url in enumerate(links):
            if num >= len(final_df):
                df = product_scraper(self.driver, url)
                try:
                    if df == 'No data':
                        continue
                except:
                    pass
                final_df = pd.concat([df, final_df], ignore_index=True)
                count += 1
                print('++++++++++++++', count)

        # Dropping the duplicate rows
        final_df.drop_duplicates(keep='first', inplace=True)

        # Adding Date, Pin, Marketplace and Location to the dataframe
        final_df['Date'] = datetime.date.today()
        final_df['MarketPlace'] = 'AMAZON'
        final_df['Pin'] = "560038"

        # Update Location column
        city_map = {
            # "400050": "Bandra West, Mumbai",
            # "500034": "Banjara Hills, Hyderabad",
            "560038": "Indiranagar, Bengaluru"
        }
        final_df['Location'] = city_map.get("560038", "Unknown")

        # def find_type(product_name, special_features):
        #     '''Function which return Type of Mattress based on Porduct Name'''
        #     # Creating a empty list for type
        #     types = []
        #     # Making the columns in lower
        #     product_name_lower = product_name.lower()
        #     if isinstance(special_features, str):
        #         special_features_lower = special_features.lower()
        #     else:
        #         special_features_lower = ""
        #     # Checks
        #     if 'dual comfort' in product_name_lower:
        #         types.append('Dual Comfort')
        #     if 'pocket spring' in product_name_lower or 'pocketed spring' in product_name_lower:
        #         types.append('Pocket Spring')
        #     if 'memory foam' in product_name_lower:
        #         types.append('Memory Foam')
        #     if 'bonnell spring' in product_name_lower:
        #         types.append('Bonnell Spring')
        #     if 'beddy' in product_name_lower:
        #         types.append('Beddy')
        #     if 'ortho' in product_name_lower or 'ortho' in special_features_lower:
        #         types.append('Orthopedic')
        #     # Returning the string of types
        #     return ', '.join(types)
        # # Applying the function
        # print(final_df['Product Name'].isna().sum())
        # final_df.dropna(subset=['Product Name'], inplace=True)
        # final_df['Type of Mattress'] = final_df.apply(lambda x: find_type(x['Product Name'], x['Special Feature']), axis=1)

        # Returning the response
        return Response(final_df.to_dict('records'), status=status.HTTP_200_OK)
