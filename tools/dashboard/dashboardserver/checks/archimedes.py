import os
from selenium import webdriver
from selenium.webdriver import FirefoxProfile, DesiredCapabilities
from checks import celery_app, CheckException
import time


@celery_app.task(name="check.archimedes")
def check_archimedes(experiment_url, user, password):
    # Initialize the driver

    if not os.environ.get("SELENIUM_NON_HEADLESS"):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/30.0.87"
        )
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
    else:
        profile = FirefoxProfile()
        profile.set_preference("intl.accept_languages", "en")
        driver = webdriver.Firefox(profile)

    driver.set_window_size(1400, 1000)

    driver.implicitly_wait(30)
    base_url = experiment_url

    try:

        # Go to the experiment and login
        driver.get(base_url)

        time.sleep(2)

        # Find username & password fields.
        usernameField = driver.find_element_by_css_selector("input[type=text]")
        usernameField.send_keys(user)
        passwordField = driver.find_element_by_css_selector("input[type=password]")
        passwordField.send_keys(password)
        loginButton = driver.find_element_by_css_selector("button")
        if loginButton.text != u"Log in": raise CheckException("Log in button not found")
        loginButton.click()

        # Find the reserve button.
        archimedes = driver.find_element_by_xpath("//button[text()='Reserve']")
        archimedes.click()

        # Switch to the iframe context.
        frame = driver.find_element_by_css_selector("#wlframe")
        driver.switch_to.frame(frame)

        # Find all the up buttons and ensure they are disabled.
        buttons = driver.find_elements_by_css_selector("img.arch-control")

        # Wait a while before checking
        time.sleep(2)

        print "Buttons found: %d" % len(buttons)
        if len(buttons) != 4 * 7: raise CheckException("Not the expected number of buttons")

        # Check that the up buttons are all disabled
        for i in range(7):
            up = buttons[0+i*4]
            bn = os.path.basename(up.get_attribute("src"))
            if bn != "up.png": raise CheckException("Button is not disabled (basename: %s)" % bn)

        # Lower each ball
        for i in range(7):
            down = buttons[2+i*4]
            up = buttons[0+i*4]
            down.click()

        time.sleep(7)
        for i in range(7):
            down = buttons[2+i*4]
            up = buttons[0+i*4]

            # Check that indeed the ball was apparently lowered and raise again.
            if os.path.basename(up.get_attribute("src")) != "up_green.png": raise CheckException("Up button not enabled after lowering ball (instance %d)" % i)
            if os.path.basename(down.get_attribute("src")) != "down.png": raise CheckException("Down button not disabled after lowering ball (instance %d)" % i)
            up.click()

        time.sleep(7)
        for i in range(7):
            down = buttons[2+i*4]
            up = buttons[0+i*4]
            # Check that it was re-raised properly.
            if os.path.basename(up.get_attribute("src")) != "up.png": raise CheckException("Up button not disabled after raising ball again (instance %d)" % i)
            if os.path.basename(down.get_attribute("src")) != "down_green.png": raise CheckException("Down button not enabled after raising ball again (instance %d)" % i)

        print "[ARCHIMEDES]: Everything seems all right"

    except:
        driver.save_screenshot("out.png")
        raise

    driver.close()


if __name__ == "__main__":
    url = "https://weblab.deusto.es/weblab/client/#page=experiment&exp.category=Aquatic%20experiments&exp.name=archimedes"
    import config

    user = config.WEBLAB_USER
    password = config.WEBLAB_PASSWORD

    check_archimedes(url, user, password)


