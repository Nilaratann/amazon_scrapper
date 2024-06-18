import time
import pandas as pd
from selenium.webdriver.common.by import By


def getlinks(driver, asin):
    """Getting the links for the different brands"""

    # Creating the blank list to store all the links of products
    links = []

    # Getting the Home page of Amazon
    driver.get('https://www.amazon.in/')
    # Rotating through list
    try:
        url_links = "https://www.amazon.in/dp/{}?th=1"
        url = url_links.format(asin)
        links.append(url)
    except:
        pass

    # Returning the links
    return links


def scroller(driver):
    """Scrolling the webpage"""

    # Scroll pausing time to load the page
    scroll_pause_time = 1
    # get the screen height of the web
    screen_height = driver.execute_script("return window.screen.height;")
    i = 1
    while True:
        # scroll one screen height each time
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
        i += 1
        time.sleep(scroll_pause_time)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = driver.execute_script("return document.body.scrollHeight;")
        # Break the loop when the height we need to scroll is larger than the total scroll height
        if (screen_height) * i > scroll_height * (3 / 4):
            break


def product_scraper(driver, url):
    """Scraping the details on the product page"""

    # Passing the url to driver and wait for loading the page
    driver.get(url)
    time.sleep(3)

    # Creating a dataframe to store the data
    df_prod = pd.DataFrame()

    # URL
    df_prod['Product url'] = pd.Series(url)

    # Image URL
    try:
        img_url = driver.find_element(By.ID, 'imageBlock').find_element(By.ID, 'imgTagWrapperId').find_element(
            By.TAG_NAME, 'img').get_attribute('src')
        df_prod['Image url'] = pd.Series(img_url)
    except:
        pass

    # Product name
    try:
        prod_name = driver.find_element(By.CLASS_NAME, 'a-container').find_element(By.ID, 'ppd').find_element(By.ID,
                                                                                                              'productTitle').text.strip()
        df_prod['Product Name'] = pd.Series(prod_name)
    except:
        df_prod['Product Name'] = pd.Series(driver.title)

    # Brand
    try:
        BRAND = driver.find_element(By.XPATH, '//*[@id="bylineInfo"]').text.strip()
        df_prod['Brand'] = pd.Series(BRAND)
    except:
        pass

    # Buy Box Availability check keeping the specific values for that
    try:
        Box_availabitiy = driver.find_element(By.CLASS_NAME, "a-box-group").find_element(By.ID,
                                                                                         "desktop_qualifiedBuyBox").find_element(
            By.ID, "availability")
        df_prod['BuyBox'] = "Available"
    except:
        df_prod['BuyBox'] = "Unavailable"

    # Total ratings
    try:
        no_rat = driver.find_element(By.ID, 'averageCustomerReviews_feature_div').find_element(By.ID,
                                                                                               'acrCustomerReviewText').text.strip()
        df_prod['Total Ratings'] = pd.Series(no_rat)
    except:
        pass

    # Average rating
    try:
        avg_rating = driver.find_element(By.XPATH, '//*[@id="acrPopover"]/span[1]/a/span').text.strip()
        df_prod['Product Rating'] = pd.Series(avg_rating)
    except:
        pass

    # Past purchase
    try:
        past_pur = driver.find_element(By.CLASS_NAME,
                                       "a-section.social-proofing-faceout-title.social-proofing-faceout-title-alignment-left").text.strip()
        df_prod['Past Purchase'] = pd.Series(past_pur)
    except:
        pass

    # MRP, Selling price and Discount percentage
    try:
        try:
            mrp = driver.find_element(By.ID, 'corePriceDisplay_desktop_feature_div').find_element(By.CLASS_NAME,
                                                                                                  'basisPrice').text.strip()
            df_prod['MRP'] = pd.Series(mrp)
        except:
            pricing = driver.find_element(By.ID, 'corePrice_desktop').find_elements(By.TAG_NAME, 'tr')
            for i in pricing:
                mrp = pricing[0].text.split('\n')[1]
            df_prod['MRP'] = pd.Series(mrp)

        try:
            sell = driver.find_element(By.ID, 'corePriceDisplay_desktop_feature_div').find_element(By.CLASS_NAME,
                                                                                                   'priceToPay').text.strip()
            df_prod['Discounted Price'] = pd.Series(sell)
        except:
            pricing = driver.find_element(By.ID, 'corePrice_desktop').find_elements(By.TAG_NAME, 'tr')
            for i in pricing:
                sell = pricing[1].text.split('\n')[1]
            df_prod['Discounted Price'] = pd.Series(sell)

        try:
            dis = driver.find_element(By.ID, 'corePriceDisplay_desktop_feature_div').find_element(By.CLASS_NAME,
                                                                                                  'savingsPercentage').text.strip()
            df_prod['Discount_percentage'] = pd.Series(dis)
        except:
            pricing = driver.find_element(By.ID, 'corePrice_desktop').find_elements(By.TAG_NAME, 'tr')
            for i in pricing:
                dis = pricing[2].text
            df_prod['Discount_percentage'] = pd.Series(dis)

    except:
        try:
            sell = driver.find_element(By.CLASS_NAME, 'reinventPricePriceToPayMargin').text
            df_prod['Discounted Price'] = pd.Series(sell)
        except:
            pass

    # Clicking on the see more button
    try:
        driver.find_element(By.ID, 'productOverview_feature_div').find_element(By.ID, 'poToggleButton').find_element(
            By.CLASS_NAME, 'a-expander-prompt').click()
        print("Clicked")
    except:
        pass

    # Product Features
    try:
        x = driver.find_element(By.ID, 'productOverview_feature_div').find_element(By.CLASS_NAME,
                                                                                   'a-section').find_element(
            By.TAG_NAME, 'table').find_elements(By.TAG_NAME, 'tr')
        for i in x:
            a = i.find_element(By.CLASS_NAME, 'a-span3').text.strip()
            b = i.find_element(By.CLASS_NAME, 'a-span9').text.strip()
            # print(a ,' ========= ', b)
            df_prod[a] = pd.Series(b)
    except:
        pass

    # Other features
    try:
        y = driver.find_element(By.ID, 'productOverview_feature_div').find_element(By.ID,
                                                                                   'glance_icons_div').find_elements(
            By.CLASS_NAME, 'a-span6')
        for j in y:
            a = j.find_elements(By.CLASS_NAME, "a-size-base")[0].text
            b = j.find_elements(By.CLASS_NAME, "a-size-base")[1].text
            print(a, "---------------------", b)
            df_prod[a] = pd.Series(b)
    except:
        pass

    # Feature Ratings
    try:
        z = driver.find_element(By.ID, "customerReviewsAttribute_feature_div").find_element(By.CLASS_NAME,
                                                                                            "a-row.a-spacing-none").find_elements(
            By.CLASS_NAME, "a-section.a-spacing-none")
        for k in z:
            m = k.find_element(By.CLASS_NAME, "a-fixed-right-grid-col.a-col-left").text
            n = k.find_element(By.CLASS_NAME, "a-text-right.a-fixed-right-grid-col.a-col-right").text
            print(m, '--------------------------', n)
            df_prod[m] = pd.Series(n)
    except:
        pass

    # About the product
    try:
        feature = driver.find_element(By.XPATH, '//*[@id="feature-bullets"]/ul').text.strip()
        df_prod['Features_1'] = pd.Series(feature)
    except:
        pass

    # Scrolling the page
    scroller(driver)

    # Product details
    try:
        details = driver.find_element(By.ID, 'prodDetails').find_element(By.TAG_NAME, 'table').find_elements(
            By.TAG_NAME, 'tr')
        for i in details:
            m = i.find_element(By.TAG_NAME, 'th').text
            n = i.find_element(By.TAG_NAME, 'td').text
            df_prod[m] = pd.Series(n)
    except:
        pass

    try:
        details = driver.find_element(By.ID, 'productDetails_db_sections').find_element(By.TAG_NAME,
                                                                                        'table').find_elements(
            By.TAG_NAME, 'tr')
        for i in details:
            m = i.find_element(By.TAG_NAME, 'th').text
            n = i.find_element(By.TAG_NAME, 'td').text
            df_prod[m] = pd.Series(n)
    except:
        pass

    # Returning the dataframe
    return df_prod
