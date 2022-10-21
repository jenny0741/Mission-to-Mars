# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
# import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        mars_df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    mars_df.columns=['Description', 'Mars', 'Earth']
    mars_df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return mars_df.to_html(classes="table table-striped")

def mars_hemispheres(browser):

# 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    hem_soup = soup(html, 'html.parser')


# 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    titles = []
    imgs = []


# 3. Write code to retrieve the image urls and titles for each hemisphere.
    hem_info = hem_soup.find('div', class_='collapsible results')
    items = hem_info.find_all('div', class_='item')

    for item in items:
    
    #Scrape titles
        title = item.find('h3').text
        titles.append(title)
    
    # Find and click the full image button
        image_elem = browser.find_by_tag('a').click()
    
    #Scrape image urls
        url = item.find('img', class_='thumb').get('src')
        image_url = f'https://marshemispheres.com/{url}'
        imgs.append(image_url)
    
    for url,title in zip(imgs,titles):
    # Create the dictonary
        dict = {
            "img_url": url,
            "title": title,
        }
    
    # Add the objet to the list
        hemisphere_image_urls.append(dict)

# 5. Quit the browser
    browser.quit()

    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())