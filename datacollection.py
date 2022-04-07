from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk
import nltk

nltk.data.path.append("D:\Coding Apps\\nltk_data")
from nltk import word_tokenize
from nltk.corpus import stopwords
import string

# Creates Tkinter window
root = tk.Tk()
root.title("Keyword Tally")

# input fields
search = ttk.Entry(width=25)  # Elevation change input box
location = ttk.Entry(width=25)  # Trail Distance input box
job_number = ttk.Entry(width=25)

# Default text for above input fields
search.insert(0, "Enter Search Query")
location.insert(0, "Enter Location")
job_number.insert(0, "How many jobs to search?")

# Input field locations
search.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
location.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
job_number.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Radio button to select search type
var = IntVar()
all_words = tk.Radiobutton(root, text="All Words", variable=var, value=1)
all_words.grid(row=4, column=0, columnspan=1, padx=0, pady=0)
sw_words = tk.Radiobutton(root, text="Software Words Only", variable=var, value=2)
sw_words.grid(row=5, column=0, columnspan=1, padx=0, pady=0)

# Status text to display after search
status_text = ttk.Label(text="Enter a search query", justify=LEFT)
status_text.grid(row=0, column=0, padx=10, pady=10)


# Sends user input to search fields in Selenium Window
def inputQueries(driver):
    search_input = driver.find_element(By.NAME, 'keywords')
    search_input.send_keys(search.get())

    location_input = driver.find_element(By.NAME, 'location')
    location_input.clear()
    location_input.send_keys(location.get())

    search_button = driver.find_element(By.XPATH, '//*[@id="main-content"]/section[1]/div/section/div[2]/button[2]')
    search_button.click()

    time.sleep(3)


# Filters search by remote jobs
def inputFilter(driver):
    remote_filter = driver.find_element(By.XPATH, '//*[@id="jserp-filters"]/ul/li[7]/div/div/button')
    remote_filter.click()

    time.sleep(1)

    remote_checkbox = driver.find_element(By.XPATH, '//*[@id="jserp-filters"]/ul/li[7]/div/div/div/div/div/div[2]')
    remote_checkbox.click()

    remote_done = driver.find_element(By.XPATH, '//*[@id="jserp-filters"]/ul/li[7]/div/div/div/button')
    remote_done.click()

    time.sleep(5)


# Scrolls through search result list until the bottom is reached, clicking the "Show More Jobs" button as necessary
def scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(3)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        try:
            see_more_button = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, '// *[ @ id = "main-content"] / section[2] / button')))
            see_more_button.click()
        except:
            continue


# Tallies up instances of all words in job description
def countAllWords(word, keyword_dict):
    if word not in keyword_dict:
        keyword_dict[word] = 1
    else:
        keyword_dict[word] += 1


# Initializes dictionary to contain all job description words, returns tallies of all words
def scrapeAllWords(driver):
    word_dict = {}
    return scrapeData(driver, word_dict)


def scrapeData(driver, keyword_dict):
    # Find all li items in job post list
    job_list = driver.find_element(By.CLASS_NAME, 'jobs-search__results-list')
    job_posts = job_list.find_elements(By.TAG_NAME, 'li')

    # Initialize job_increment to 0
    job_increment = 0

    # Sets list of stop words to include punctuation
    stop = set(stopwords.words('english') + list(string.punctuation))

    # For each job in the job post, click the show more button and gather the job description text
    for job in job_posts:
        time.sleep(2)
        job.click()
        time.sleep(3)

        # Show more button X-Path may be different depending on format of job description.
        # Program will test the two most common, and continue to the next post if the show more button is not found
        try:
            show_more_button = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section/div[2]/div/section['
                                                          '1]/div/div/section/button[1]')))
            show_more_button.click()
            job_text = driver.find_element(By.XPATH, '/html/body/div[1]/div/section/div[2]/div/section[1]/div').text
        except:
            try:
                show_more_button = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/section/div[2]/div[1]/section['
                                                              '2]/div/div[2]/section/button[1]')))
                show_more_button.click()
                job_text = driver.find_element(By.XPATH,
                                               '/html/body/div[1]/div/section/div[2]/div[1]/section[2]/div/div['
                                               '2]/section/div').text
            except:
                continue

        # Creates list of individual words from job description
        job_text_token = set([i for i in word_tokenize(job_text.lower()) if i not in stop])

        # If Radio Option 1 is selected (Scrape All Words), execute countAllWords for each word in job description
        # If Radio Option 2 is selected (SW words only), tally instances of keywords from hardcoded dictionary
        if var.get() == 1:
            for word in job_text_token:
                countAllWords(word, keyword_dict)
        else:
            for key in keyword_dict:
                if key in job_text.lower():
                    keyword_dict[key] += 1

        # Increment job increment
        job_increment += 1

        # Exit loop if number of jobs to search is finite
        if job_number.get() != 'inf':
            if job_increment == int(job_number.get()):
                break

    # Update status text with number of jobs searched
    status_text["text"] = f"{job_increment} jobs searched"

    # Return keyword dictionary with totals
    return keyword_dict


# Removes "repeats" of specific SW terms that may be expressed in multiple formats
def cleanup(keyword_dict):
    keyword_dict["c"] = keyword_dict[" c "] + keyword_dict[" c,"] + keyword_dict[" c/"] + keyword_dict[" c."]
    keyword_dict.pop(" c ")
    keyword_dict.pop(" c,")
    keyword_dict.pop(" c/")
    keyword_dict.pop(" c.")

    keyword_dict["java"] = keyword_dict[" java "] + keyword_dict[" java,"] + keyword_dict[" java/"] + keyword_dict[
        " java."]
    keyword_dict.pop(" java ")
    keyword_dict.pop(" java,")
    keyword_dict.pop(" java/")
    keyword_dict.pop(" java.")

    keyword_dict["go"] = keyword_dict[" go "] + keyword_dict[" go,"] + keyword_dict[" go/"] + keyword_dict[" go."]
    keyword_dict.pop(" go ")
    keyword_dict.pop(" go,")
    keyword_dict.pop(" go/")
    keyword_dict.pop(" go.")

    keyword_dict["r"] = keyword_dict[" r "] + keyword_dict[" r,"] + keyword_dict[" r/"] + keyword_dict[" r."]
    keyword_dict.pop(" r ")
    keyword_dict.pop(" r,")
    keyword_dict.pop(" r/")
    keyword_dict.pop(" r.")

    return keyword_dict


# Scrapes job description and tallies total of hard coded key words
def scrapeSoftware(driver):
    word_dict = {" c ": 0, " c/": 0, " c,": 0, " c.": 0, "c++": 0, "python": 0, " java ": 0, "selenium": 0,
                 "sql": 0, "android": 0, "api": 0, "jenkins": 0, "appium": 0, "cypress": 0, "javascript": 0,
                 " java,": 0,
                 " java/": 0, " java.": 0, "spring": 0, "graphql": 0, "maven": 0, "docker": 0, "react": 0, "css": 0,
                 "storybook": 0, "html": 0, ".net": 0, "oracle": 0, "datastage": 0, "talend": 0, "cucumber": 0,
                 "kubernetes": 0,
                 " go ": 0, " go.": 0, " go/": 0, " go,": 0, "php": 0, "postman": 0, "jira": 0, "git": 0, "testrail": 0,
                 "ruby": 0, "aws": 0, "nosql": 0, "pytest": 0, "c#": 0, "perl": 0, " r ": 0, " r.": 0, " r,": 0,
                 " r/": 0,
                 "postgres": 0, "ios": 0, "rest": 0, "restful": 0, "django": 0, "flask": 0, "node": 0, "gui": 0}
    return cleanup(scrapeData(driver, word_dict))


# Prints results as a CSV
def printResults(keyword_dict):
    df = pd.DataFrame(data=keyword_dict, index=[0])
    df = df.T
    df.columns = ['Count']
    df = df.sort_values(by=['Count'], ascending=False)
    df.to_csv('JobKeywords.csv')


# Opens a Selenium Chrome window and executes script
def run():
    driver = webdriver.Chrome(executable_path="D:/Coding Apps/Selenium Drivers/chromedriver.exe")
    driver.get("https://www.linkedin.com/jobs/")
    driver.maximize_window()
    inputQueries(driver)
    inputFilter(driver)

    # Only scroll if the number of jobs to be searched is greater than 25
    if job_number.get() == 'inf' or int(job_number.get()) > 25:
        scroll(driver)

    # Selects which data collection type to execute based on Radio Input
    if var.get() == 1:
        results = scrapeAllWords(driver)
    else:
        results = scrapeSoftware(driver)

    printResults(results)
