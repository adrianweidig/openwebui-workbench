package com.example.ui;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.example.ui.pages.HomePage;
import com.example.ui.support.ArtifactWriter;
import com.example.ui.support.TestSettings;
import com.example.ui.support.WebDriverFactory;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.openqa.selenium.WebDriver;

final class HomePageTest {
    private final TestSettings settings = TestSettings.fromEnvironment();
    private final WebDriver driver = WebDriverFactory.createChrome(settings);

    @Test
    void primaryActionShowsExpectedResult() {
        try {
            var page = new HomePage(driver, settings.waitTimeout());

            page.open(settings.baseUrl());

            assertEquals("Welcome", page.headingText());
            assertEquals("Action completed", page.clickPrimaryActionAndReadResult());
        } catch (RuntimeException | AssertionError failure) {
            ArtifactWriter.captureScreenshot(driver, settings.artifactDirectory(), "primaryActionShowsExpectedResult");
            throw failure;
        }
    }

    @AfterEach
    void tearDown() {
        driver.quit();
    }
}
