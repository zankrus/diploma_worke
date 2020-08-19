import logging
import os

import allure
import pytest

from pages.application import Application

logger = logging.getLogger()


@pytest.fixture(scope="session")
def app(request):
    base_url = request.config.getoption("--base-url")
    headless = request.config.getoption("--headless")
    fixture = Application(base_url, headless)
    logger.info(f"Запуск браузера с base url = {base_url} , headless - {headless}")
    fixture.wd.implicitly_wait(10)
    fixture.wd.maximize_window()
    yield fixture
    fixture.teardown()


@pytest.fixture(scope="session")
def authorized_user(app, request):
    fixture = app
    fixture.open_login_page()
    fixture.login_page.click_enter_button()
    fixture.login_page.click_enter_button()
    fixture.open_main_page()
    return fixture


def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default="https://idemo.bspb.ru",
        help="enter base_url",
    ),
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="launching browser without gui",
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        mode = "a" if os.path.exists("failures") else "w"
        try:
            with open("failures", mode):
                if "app" in item.fixturenames:
                    web_driver = item.funcargs["app"]
                else:
                    print("Fail to take screen-shot")
                    return
            allure.attach(
                web_driver.wd.get_screenshot_as_png(),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception as e:
            print("Fail to take screen-shot: {}".format(e))
