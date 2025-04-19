from flask import Flask
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from app import app, db  # assuming your Flask app is named 'app'

class IntegrationTest(LiveServerTestCase):

    def create_app(self):
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 8943
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        return app

    def setUp(self):
        self.driver = webdriver.Chrome()
        db.create_all()

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()

    def test_gatepass_request_flow(self):
        driver = self.driver
        driver.get(self.get_server_url() + "/login")  # adjust as needed

        # Log in as a student
        driver.find_element(By.NAME, "username").send_keys("student1")
        driver.find_element(By.NAME, "password").send_keys("password")
        driver.find_element(By.NAME, "submit").click()

        # Navigate to gatepass request form
        driver.get(self.get_server_url() + "/gpassreq/1")

        # Fill in gatepass form
        driver.find_element(By.NAME, "pass_type").send_keys("Home")
        driver.find_element(By.NAME, "reason").send_keys("Family Visit")
        driver.find_element(By.NAME, "place").send_keys("Kochi")
        driver.find_element(By.NAME, "gdate").send_keys("2025-04-12")
        driver.find_element(By.NAME, "going_time").send_keys("09:00")
        driver.find_element(By.NAME, "rdate").send_keys("2025-04-13")

        driver.find_element(By.NAME, "submit").click()
        time.sleep(2)

        # Assert redirect to student portal (integration success)
        self.assertIn("sportal", driver.current_url)
