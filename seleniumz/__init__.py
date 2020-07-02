from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from lxml import etree
from bs4 import BeautifulSoup


class Page(object):
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def find_element_by_text(self, text):
        xpath = '//*[text()="%s"]' % text
        return self.driver.find_element('xpath', xpath)

    def find_element_by_partial_text(self, text):
        xpath = '//*[contains(text(), "%s")]' % text
        return self.driver.find_element('xpath', xpath)

    def find_element_by_class_names(self, class_names):
        selector = ' '.join(['.'+name for name in class_names.split(' ')])
        return self.driver.find_element('css selector', selector)

    def find_input_by_value(self, value):
        selector = 'input[value="%s"]' % value
        return self.driver.find_element('css selector', selector)

    def find_input_by_hint(self, value):
        selector = 'input[placeholder="%s"]' % value
        return self.driver.find_element('css selector', selector)

    def find(self, by, value, frame=None, remove_style=False, highlight=False):
        by_dict = {
            'text': self.find_element_by_text,
            'partial text': self.find_element_by_partial_text,
            'value': self.find_input_by_value,
            'hint': self.find_input_by_hint,
            'class_names': self.find_element_by_class_names,
        }
        find_by = by_dict.get('by')
        if frame:
            self.driver.switch_to(frame)
        element = find_by(value) if find_by else self.driver.find_element(by, value)
        if remove_style:
            self.remove_style(element)
        if highlight is True:
            self.highlight(element)
        if frame:
            self.driver.switch_to.parent_frame()
        return element

    def try_find(self, by, value):
        try:
            return self.find(by, value)
        except NoSuchElementException:
            # self.driver.save_screenshot('%s_%s' % (by, value))
            return False

    def exist(self, by, value):
        return True if self.try_find(by, value) else False

    def loop_find(self, by, value, timeout=30, interval=0.5):
        return WebDriverWait(self.driver, timeout, interval).until(
            lambda driver: self.find(by, value)
        )

    def open(self, url, timeout=None):
        if timeout:
            self.driver.set_page_load_timeout(timeout)
        self.driver.get(url)
        return self

    def wait(self, seconds=1):
        sleep(seconds)
        return self

    def click(self, by, value, frame=None, remove_style=False):
        element = self.find(by, value, frame, remove_style)
        element.click()
        return self

    def input_to(self, by, value, text, frame=None, remove_style=False):
        element = self.find(by, value, frame, remove_style)
        element.clear()
        element.send_keys(text)
        return self

    def submit(self):
        selector = 'input[type="submit"]'
        return self.click('css selector', selector)

    def upload(self, file_path):
        selector = 'input[type="submit"]'
        return self.input_to('css selector', selector, file_path, remove_style=True)

    def get_page_height(self):
        js = 'return document.documentElement.scrollHeight;'
        return self.driver.execute_script(js)

    def set_style(self, element, style):
        js = 'arguments[0].setAttribute("style", arguments[1]);'
        self.driver.execute_script(js, element, style)
        return self

    def highlight(self, element):
        style = "background: red; border: 2px solid yellow;"
        return self.set_style(element, style)

    def remove_style(self, element):
        js = 'arguments[0].removeAttribute("style")'
        self.driver.execute_script(js, element)
        return self

    def scroll_down(self, height):
        js = 'document.documentElement.scrollTop=%s;' % height
        self.driver.execute_script(js)
        return self

    def switch_to_new_window(self):
        windows = self.driver.window_handles
        assert len(windows) == 2, 'just support 2 windows opened'
        self.driver.switch_to.window(windows[1])
        return self

    def move_to(self, by, value):
        element = self.find(by, value)
        ActionChains(self.driver).move_to_element(element).perform()
        return self

    def add_cookies(self, cookies: dict):
        cookies = [{'name': key, 'value': value} for key, value in cookies.items()]
        [self.driver.add_cookie(cookie) for cookie in cookies]
        return self

    # 页面解析
    @property
    def soup(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        return soup

    def xpath(self, value):
        """find element by lxml"""
        root = etree.HTML(self.driver.page_source)
        return root.xpath(value)


class Chrome(object):
    def __init__(self, headless=False, timeout=30, device=None):
        pass
