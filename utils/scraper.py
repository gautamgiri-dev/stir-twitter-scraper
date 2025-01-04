from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import os
import datetime

def get_driver(headless: bool = False, use_profile: bool = False, logging_func = print, proxy: str | None = None) -> Chrome:
    # using webdriver manager to automatically detect the current chrome version
    # installed on the system and download appropriate chromedriver
    exec_path = ChromeDriverManager().install()
    service = ChromeService(
        exec_path
    )

    options = ChromeOptions()
    if headless:
        logging_func('Using headless chrome')
        options.add_argument('--headless=new')
    if proxy:
        logging_func(f'Using proxy: {proxy}')
        options.add_argument(f'--proxy-server={proxy}')
    if use_profile:
        profile_path = os.environ.get('CHROME_PROFILE_DIR')
        data_dir = os.environ.get('CHROME_USER_DATA_DIR')
        if not profile_path:
            raise Exception("CHROME_PROFILE_DIR env not set")
        if not data_dir:
            raise Exception("CHROME_USER_DATA_DIR env not set")
        options.add_argument(f'--user-data-dir={data_dir}')
        options.add_argument(f'--profile-directory={profile_path}')

    return Chrome(options, service)

def random_delay(max: float = 3.0):
    wait_time = random.random() * max
    time.sleep(wait_time)

def wait_for_element(driver: Chrome, by: str, identifier: str):
    try:
        wait = WebDriverWait(driver, 120)
        return wait.until(EC.presence_of_element_located((by, identifier)))
    except TimeoutException:
        raise Exception(f"[TimeoutException] Couldn't find element by: {by} identifier: {identifier}")

def login_twitter(driver: Chrome, logging_func):
    username, password = os.environ.get('TWITTER_EMAIL'), os.environ.get('TWITTER_PASSWORD')
    
    login_btn = wait_for_element(driver, By.CSS_SELECTOR, "a[href='/login']")
    random_delay()

    logging_func("Clicking login button...")
    login_btn.click()
    
    username_input = wait_for_element(driver, By.CSS_SELECTOR, "input[autocomplete='username']")
    logging_func(f"Entering username: {username}")
    username_input.send_keys(username)
    random_delay(1)
    username_input.send_keys(Keys.ENTER)

    logging_func('Checking if phone/username verification is requested...')
    pass_username_test(driver, logging_func)

    password_input = wait_for_element(driver, By.CSS_SELECTOR, "input[type='password']")
    logging_func(f"Entering password: {password}")
    password_input.send_keys(password)
    random_delay(1)
    password_input.send_keys(Keys.ENTER)

def scrape_top_trending(driver: Chrome, logging_func):
    wait_for_element(driver, By.CSS_SELECTOR, "div[aria-label*='Trending']")
    random_delay(2)

    print("Waiting for 4 seconds...")
    time.sleep(4)
    try:
        wait = WebDriverWait(driver, 10)
        trending_topics = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[aria-label*='Trending'] div[data-testid='trend'] div:nth-child(2)")))
        topics = []
        for topic in trending_topics:
            title = topic.text
            topics.append(title)
        return topics
    except TimeoutException as e:
        logging_func("Error occurred while finding trending section")
        logging_func(e)

def get_current_ip_being_used(driver: Chrome):
    driver.get('https://api.ipify.org/')
    time.sleep(3)
    return driver.find_element(By.TAG_NAME, "body").text

def pass_username_test(driver: Chrome, logging_func):
    try:
        ec_challenge = EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'unusual login activity')
        ec_password = EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
        WebDriverWait(driver, 20).until(EC.any_of(ec_challenge, ec_password))

        if 'unusual login activity' not in driver.find_element(By.TAG_NAME, 'body').text:
            logging_func('Phone/Username verification not found...')
            return

        logging_func('Phone/Username verification found...')
        username_input = wait_for_element(driver, By.TAG_NAME, 'input')
        random_delay(2)
        # can use ActionChains to mimic more human like behaviour
        username_input.send_keys(os.environ.get('TWITTER_USERNAME'))
        random_delay(1)
        username_input.send_keys(Keys.ENTER)
    except TimeoutException:
        logging_func('Phone/Username verification not found...')
        pass

def check_already_logged_in(driver: Chrome):
    try:
        ec_homepage = EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'For you')
        ec_login_page = EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'Sign in')
        WebDriverWait(driver, 30).until(EC.any_of(ec_homepage, ec_login_page))
        return 'For you' in driver.find_element(By.TAG_NAME, 'body').text
    except TimeoutException:
        return False
    
def logger_and_emitter(logging_func, emitting_func):
    def log_and_emit(message):
        logging_func(message)
        emitting_func('log', message)
    return log_and_emit

def scrape_topics(use_proxy=False, headless=False, use_profile=False, logging_func=print, event_emitter=print):
    proxy = None
    if use_proxy:
        proxy = f'{os.environ.get("PROXY_MESH_HOSTNAME")}:{os.environ.get("PROXY_MESH_PORT")}'
    
    start_time = datetime.datetime.now()
    logger = logging_func

    logger(f'Started at: {start_time.strftime("%d/%m/%Y, %H:%M:%S")}')
    driver = get_driver(headless=headless, use_profile=use_profile, logging_func=logger, proxy=proxy)
    current_ip = get_current_ip_being_used(driver)
    logger(f'Current IP: {current_ip}')
    topics = None
    try:
        logger('Opening twitter homepage...')
        driver.get('https://x.com')

        is_logged_in = check_already_logged_in(driver)
        if not is_logged_in:
            logger('Trying to login...')
            login_twitter(driver, logger)
            logger('Logged in successfully!')
        else:
            logger("Previous login detected...")
        
        logger('Trying to scrape top trending topics...')
        topics = scrape_top_trending(driver, logger)
        logger(f'Top trending topics found: {topics}')
    except Exception as e:
        logger("Something went wrong.")
        logger(str(e))
    finally:
        driver.quit()
    return topics, current_ip, start_time