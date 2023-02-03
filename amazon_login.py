from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from getpass import getpass
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from cleantext import clean
import time
import re

options = Options()

#We accept the input from the user - Username and Password required to SignIn to the application
username = input("Enter in your username: ")
password = getpass("Enter in your password: ")

#Load the website under test - amazon.in is chosen, amazon.com has delivery to location problem, so chose this
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(10)
driver.get("https://www.amazon.in/")

SignIn_button = driver.find_element(by=By.XPATH, value='//*[@id="nav-link-accountList"]/span')
SignIn_button.click()

#time.sleep(2)

'''
The below section retrieves all the links present on the SignIn Page,
 i) Checks if they are actually shown on the page (there are a few hidden links which are ignored)
 ii) Checks if the displayed links are clickable
 iii) The links are printed on the output screen for reference
'''
total=driver.find_elements(By.TAG_NAME,"a")
for elem in total:
    print("Printing all the links that are on the SignIn Page")
    print(elem.get_attribute("href"))
    if elem.is_displayed():
        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(elem))

'''
TestUserSignIn

i) Username is sent as input
ii) Continue button is clicked
iii) Password is sent as input
iv) SignIn is pressed

'''
username_textbox = driver.find_element(By.ID, "ap_email")
username_textbox.send_keys(username)

Continue_button = driver.find_element(By.ID, "continue")
Continue_button.submit()

password_textbox = driver.find_element(By.ID, "ap_password")
password_textbox.send_keys(password)

SignIn_button = driver.find_element(By.ID, "auth-signin-button-announce")
SignIn_button.submit()

#time.sleep(5)


'''
TestAddDeleteItemsToCart

Description : Add multiple items to the cart, 
              check if the items added are the ones that were actually added
              validate the total cart value
              Delete the items from the cart, validate the same

TestSteps :
    1. Enter iphone as the element to be searched via search bar displayed on top of the screen
    2. Add the first 3 phones displayed on the screen as a result of the search
    3. Store the values - Title, Size, Color, Price onto a disctionary which can be later used for cart validation
    4. Go to Cart
    5. Retrieve the elements present in the cart
    6. Cross check if the Title, Size, Color, Price of the items in the cart are the same as the added ones using the stored value previously
    7. Check the total of the cart value is same as expected
    8. Delete the items one by one and validate the same

Validation :
    1. Cart value == calculated value
    2. If title, size, color, price is same as expected 
    3. Delete items and check if they were deleted

Enhancements/To do:
    1. Currently the price says mismatched, since the product page shows as x,000 and cart page shows it as x,000.00
       This needs to return TRUE, currently it just prints the not matching values.

'''


iphone_results = driver.find_element(By.CSS_SELECTOR, "input[id='twotabsearchtextbox']")    #retrieves the search box
iphone_results.send_keys("iphone")
enter_button = driver.find_element(By.CSS_SELECTOR, "input[id='twotabsearchtextbox']")
enter_button.send_keys(Keys.RETURN)

parent_window = driver.window_handles[0]
iphonelist = driver.find_elements(By.XPATH, '//span[@class="a-size-medium a-color-base a-text-normal"]')   #retrieves the individual product on the results page

product_details = {}
total_price = 0
for i in range(3):
    iphonelist[i].click()
    #time.sleep(5)
    child_window = driver.window_handles[i+1]                #when we click the product, it is opened on new tab, so we have used this mechanism
    driver.switch_to.window(child_window)
    time.sleep(2)
    #Each of the element mentioned below is retrieved, its text is added onto the product_details variable
    productName = driver.find_element(By.ID, "productTitle").text
    productSize = driver.find_element(By.ID, "variation_size_name").text.split('\n')
    productColor = driver.find_element(By.ID, "variation_color_name").text.split('\n')
    productPrice = driver.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[2]/span[2]/span[2]').text
    product_details[productName] = list()
    if len(productSize) > 0:
        product_details[productName].append(productSize[0])
    else:
        product_details[productName].append(productSize)
    if len(productColor) > 0:
        product_details[productName].append(productColor[0])
    else:
        product_details[productName].append(productColor)
    product_details[productName].append(productPrice)
    driver.find_element(By.ID, "submit.add-to-cart").click()                   #Add to cart button
    #time.sleep(5)
    total_price += float(productPrice.replace(',',''))
    if i + 1 == 3:
        break
    else:
        driver.switch_to.window(parent_window)                                #Proceed back to parent window which has search results
time.sleep(2)

driver.find_element(By.XPATH, '//*[@id="attach-sidesheet-view-cart-button"]').click()    #Go to cart button
#time.sleep(5)
#Get each element in the cart
get_active_elements = driver.find_elements(By.XPATH, '//div[@class="a-section a-spacing-mini sc-list-body sc-java-remote-feature"]/descendant::div[@class="sc-list-item-content"]')
cart_products = {}

#Form the cart_products variable similar to product_details, to get the actual cart related details
for item in get_active_elements:
    key = item.text.split('\n')[0]
    cart_products[key] = []
    for value in item.text.split('\n'):
        if value != key:
            cart_products[key].append(value.strip())

#compare the cart items with the product page items
error_count = 0
for item in product_details:
    cart_details = cart_products[item]
    for added_item in product_details[item]:
        if added_item not in cart_details:
            print("Mismatch elements")
            print(added_item)
            error_count += 1

subtotal = driver.find_element(By.XPATH, '//span[@class="a-color-price sc-price-container a-text-bold"]')
cart_price = subtotal.text
cart_price = float(cart_price.strip().replace(',',''))

#Comapre the total value of the cart
assert cart_price == total_price, "Cart Value not matching the price of the added items!"


#Delete the items present in the cart one by one and validate
#delete_button = driver.find_elements(By.XPATH, '//div[@class="a-section a-spacing-mini sc-list-body sc-java-remote-feature"]/descendant::div[@class="a-size-small sc-action-delete"]')
delete_button = driver.find_element(By.XPATH, '//input[@value="Delete"]')
delete_button.click()
time.sleep(2)

get_active_elements = driver.find_elements(By.XPATH, '//div[@class="a-section a-spacing-mini sc-list-body sc-java-remote-feature"]/descendant::div[@class="sc-list-item-content"]')
assert len(get_active_elements) == 2, "Item not deleted from cart!"

delete_button = driver.find_element(By.XPATH, '//input[@value="Delete"]')
delete_button.click()
time.sleep(2)

get_active_elements = driver.find_elements(By.XPATH, '//div[@class="a-section a-spacing-mini sc-list-body sc-java-remote-feature"]/descendant::div[@class="sc-list-item-content"]')
assert len(get_active_elements) == 1, "Item not deleted from cart!"

delete_button = driver.find_element(By.XPATH, '//input[@value="Delete"]')
delete_button.click()
time.sleep(2)


'''
TestFilterSortJump

Description : 
    Taking into consideration a clothing category, we are testing the sorting, filter and jump to next page cases

TestSteps :
    1. The category chosen is "women jeans", is entered onto the search bar
    2. Filter critera chosen is "Under 300" (price)
    3. Sort criteria chosen is "Price: Low to High"
    4. Both of these are combined for validation simultaneously
    5. Retrieve all the elements post applying these both and store the price in a list variable
    6. Validations as mentioned below
    7. Jump to the next page, and retrieve all the elements
    8. Compare it with elements on the previous page which was stored in a list variable

Validation:
    1. Check if the price < 300 for all the products retreived (Filter Validation)
    2. Check if the price appear in the ascending order
        a. Currently the price has a bit of deviation due to "Sponsored" products, 
           so I have made the assertion such that if about 5 products are not sorted, 
           I still go ahead and pass it, with the assumption that upto 5 sponsored products
           appear on a single page.
        b. Enhancement - check to see if the product is "Sponsored" and ignore the price for that
                         product while checking if the list is sorted
    3. Check if first_page contents != second_page contents
        a. There is a bit of deviation here as well due to "sponsored" products, which can appear 
           in the next page, so I have kept a limit of about 5
        b. Enhancement could be the same as above

'''

clothing_results = driver.find_element(By.CSS_SELECTOR, "input[id='twotabsearchtextbox']")    #enter women jeans in the search box
clothing_results.send_keys("women jeans")
enter_button = driver.find_element(By.CSS_SELECTOR, "input[id='twotabsearchtextbox']")
enter_button.send_keys(Keys.RETURN)



less_than_price = driver.find_element(By.XPATH, '//*[@id="p_36/4595084031"]/span/a/span').click()      #this is the element for "Under 300" filter criteria 
select = Select(driver.find_element(By.ID, "s-result-sort-select"))                                    #element for choosing the sort drop down menu
select.select_by_visible_text("Price: Low to High")                                                    #element for choosing the sort criteria -> Price: Low to High
time.sleep(2)
#price_list = driver.find_elements(By.XPATH, "//span[@class='a-price-whole']")
#price_list = driver.find_elements(By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')
price_list = []
#for a given product we can have whole part and decimal, so each of this is taken into account and merged to form the product price
price_list1 = driver.find_elements(By.XPATH, '//div[contains(@class, "s-result-item s-asin")]/descendant::span[@class="a-price-whole"]')          
price_list3 = driver.find_elements(By.XPATH, '//div[contains(@class, "s-result-item s-asin")]/descendant::span[@class="a-price-fraction"]')

for i in range(len(price_list1)):
    try:
        price_list.append(float(price_list1[i].text + "." + price_list3[i].text))
    except:
        price_list.append(float(price_list1[i].text))

#check if the price list is sorted, check if the price list hold true for filter criteria where price has to be < 300
sorted_count = 0
unsorted_count = 0
filtered = 0
unfiltered = 0
for i in range(len(price_list)-1):
    if price_list[i] <= price_list[i+1]:
        sorted_count += 1
    else:
        unsorted_count += 1
    
    if price_list[i] < 300:
        filtered += 1
    else:
        unfiltered += 1

assert len(price_list)-sorted_count <= 5, "The products are not sorted despite sorting in Low -> High manner"
assert unfiltered==0, "Filter mechanism not as expected!"


#This stores the Title of all the elements appearing in Page 1
#price_list = driver.find_elements(By.XPATH, '//div[contains(@class, "s-result-item s-asin")]/descendant::div[@class="a-row a-size-base a-color-base"]')
#print(price_list)
current_page = driver.find_elements(By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')
current_items = []
for i in current_page:
    current_items.append(i.text)

driver.find_element(By.LINK_TEXT, "Next").click()         #Next button is clicked
time.sleep(3)
#this stores the Title of all the elements appearing in Page 2
next_page = driver.find_elements(By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')
next_items = []
for j in next_page:
    next_items.append(j.text)
same_item = 0

#Page1 content and Page2 content are comapred, with upto 5 repeats allowed due to "sponsored" content
for current_product in current_items:
    for next_product in next_items:
        if current_product == next_product:
            same_item += 1
assert same_item<=5, "Multiple Same Items are appearing in the Next Page!!"

'''
TestSignOut 

'''
button = driver.find_element(by=By.XPATH, value='//*[@id="nav-link-accountList"]/span')
ActionChains(driver).move_to_element(button).click(driver.find_element(by=By.XPATH, value='//*[@id="nav-item-signout"]/span')).perform()
time.sleep(3)


