from django.test import TestCase, Client
from .models import News

from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from django.contrib.auth.models import User

class MainTest(TestCase):
    def test_main_url_is_exist(self):
        response = Client().get("")
        self.assertEqual(response.status_code, 200)

    def test_main_using_main_template(self):
        response = Client().get("")
        self.assertTemplateUsed(response, "main.html")

    def test_nonexistent_page(self):
        response = Client().get("/burhan_always_exists/")
        self.assertEqual(response.status_code, 404)

    def test_news_creation(self):
        news = News.objects.create(
            title="BURHAN FC MENANG",
            content="BURHAN FC 1-0 PANDA BC",
            category="match",
            news_views=1001,
            is_featured=True
        )
        self.assertTrue(news.is_news_hot)
        self.assertEqual(news.category, "match")
        self.assertTrue(news.is_featured)

    def test_news_default_values(self):
        news = News.objects.create(
            title="Test News",
            content="Test content"
        )
        self.assertEqual(news.category, "update")
        self.assertEqual(news.news_views, 0)
        self.assertFalse(news.is_featured)
        self.assertFalse(news.is_news_hot)

    def test_increment_views(self):
        news = News.objects.create(
            title="Test News",
            content="Test content"
        )
        initial_views = news.news_views
        news.increment_views()
        self.assertEqual(news.news_views, initial_views + 1)

    def test_is_news_hot_threshold(self):
        news_20 = News.objects.create(
            title="News with 20 views",
            content="Test content",
            news_views=20
        )

        self.assertFalse(news_20.is_news_hot)

        news_21 = News.objects.create(
            title="News with 21 views",
            content="Test content",
            news_views=21
        )
        self.assertTrue(news_21.is_news_hot)

class FootballNewsFunctionalTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Di saya, entah kenapa hanya bisa berjalan menggunakan WebDriver Edge.
        # Jadi di sini saya menggunakan WebDriver Edge. Seharusnya tidak berbeda dengan Chrome karena basisnya sama-sama Chrome.
        cls.browser = webdriver.Edge()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        cls.browser.quit()

    def setUp(self):
        self.test_user = User.objects.create_user(
            username="testadmin",
            password="testpassword"
        )

    def tearDown(self):
        self.browser.delete_all_cookies()
        self.browser.execute_script("window.localStorage.clear();")
        self.browser.execute_script("window.sessionStorage.clear();")
        self.browser.get("about:blank")

    def login_user(self):
        self.browser.get(f"{self.live_server_url}/login/")
        username_input = self.browser.find_element(By.NAME, "username")
        password_input = self.browser.find_element(By.NAME, "password")
        username_input.send_keys("testadmin")
        password_input.send_keys("testpassword")
        password_input.submit()

    def test_login_page(self):
        self.login_user()

        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Football News")

        logout_link = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Logout")
        self.assertTrue(logout_link.is_displayed())

    def test_register_page(self):
        self.browser.get(f"{self.live_server_url}/register/")

        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Register")

        username_input = self.browser.find_element(By.NAME, "username")
        password1_input = self.browser.find_element(By.NAME, "password1")
        password2_input = self.browser.find_element(By.NAME, "password2")

        username_input.send_keys("newuser")
        password1_input.send_keys("complexpass123")
        password2_input.send_keys("complexpass123")
        password2_input.submit()

        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        login_h1 = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(login_h1.text, "Login")

    def test_create_news(self):
        self.login_user()

        add_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Add News")
        add_button.click()

        title_input = self.browser.find_element(By.NAME, "title")
        content_input = self.browser.find_element(By.NAME, "content")
        category_select = self.browser.find_element(By.NAME, "category")
        thumbnail_input = self.browser.find_element(By.NAME, "thumbnail")
        is_featured_checkbox = self.browser.find_element(By.NAME, "is_featured")

        title_input.send_keys("Test News Title")
        content_input.send_keys("Test news content for selenium testing")
        thumbnail_input.send_keys("https://example.com/image.jpg")

        select = Select(category_select)
        select.select_by_value("match")

        is_featured_checkbox.click()

        title_input.submit()

        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Football News"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Football News")

        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Test News Title")))
        news_title = self.browser.find_element(By.PARTIAL_LINK_TEXT, "Test News Title")
        self.assertTrue(news_title.is_displayed())

    def test_news_detail(self):
        self.login_user()

        news = News.objects.create(
            title="Detail Test News",
            content="Content for detail testing",
            user=self.test_user
        )

        self.browser.get(f"{self.live_server_url}/news/{news.id}")

        self.assertIn("Detail Test News", self.browser.page_source)
        self.assertIn("Content for detail testing", self.browser.page_source)

    def test_logout(self):
        self.login_user()

        logout_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Logout')]")
        logout_button.click()

        wait=WebDriverWait(self.browser, 120)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Login"))
        h1_element = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertEqual(h1_element.text, "Login")

    def test_filter_main_page(self):
        News.objects.create(
            title="My Test News",
            content="My news content",
            user=self.test_user
        )
        News.objects.create(
            title="Other User News",
            content="Other content",
            user=self.test_user
        )

        self.login_user()

        wait = WebDriverWait(self.browser, 120)
        wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "All Articles")))
        all_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "All Articles")
        all_button.click()
        self.assertIn("My Test News", self.browser.page_source)
        self.assertIn("Other User News", self.browser.page_source)

        my_button = self.browser.find_element(By.PARTIAL_LINK_TEXT, "My Articles")
        my_button.click()
        self.assertIn("My Test News", self.browser.page_source)
