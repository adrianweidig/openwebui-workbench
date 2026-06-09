package com.example.ui.pages;

import java.net.URI;
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public final class HomePage {
    private static final By APP_SHELL = By.cssSelector("[data-testid='app-shell']");
    private static final By HEADING = By.cssSelector("[data-testid='home-heading']");
    private static final By PRIMARY_ACTION = By.cssSelector("[data-testid='primary-action']");
    private static final By RESULT = By.cssSelector("[data-testid='primary-action-result']");

    private final WebDriver driver;
    private final WebDriverWait wait;

    public HomePage(WebDriver driver, Duration waitTimeout) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, waitTimeout);
    }

    public void open(URI baseUrl) {
        driver.navigate().to(baseUrl.resolve("/").toString());
        wait.until(ExpectedConditions.visibilityOfElementLocated(APP_SHELL));
    }

    public String headingText() {
        return wait.until(ExpectedConditions.visibilityOfElementLocated(HEADING)).getText().trim();
    }

    public String clickPrimaryActionAndReadResult() {
        wait.until(ExpectedConditions.elementToBeClickable(PRIMARY_ACTION)).click();
        return wait.until(ExpectedConditions.visibilityOfElementLocated(RESULT)).getText().trim();
    }
}
