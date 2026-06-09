package com.example.ui.support;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;

public final class WebDriverFactory {
    private WebDriverFactory() {
    }

    public static WebDriver createChrome(TestSettings settings) {
        var options = new ChromeOptions();

        if (settings.headless()) {
            options.addArguments("--headless=new");
        }

        // These arguments make execution more stable on Linux CI agents.
        options.addArguments("--window-size=1280,720");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--no-sandbox");

        var driver = new ChromeDriver(options);
        driver.manage().timeouts().implicitlyWait(Duration.ZERO);
        driver.manage().timeouts().pageLoadTimeout(Duration.ofSeconds(30));

        return driver;
    }
}
