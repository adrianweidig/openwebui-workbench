package com.example.ui.support;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.openqa.selenium.OutputType;
import org.openqa.selenium.TakesScreenshot;
import org.openqa.selenium.WebDriver;

public final class ArtifactWriter {
    private ArtifactWriter() {
    }

    public static void captureScreenshot(WebDriver driver, String artifactDirectory, String testName) {
        if (!(driver instanceof TakesScreenshot screenshotDriver)) {
            return;
        }

        try {
            var safeName = testName.replaceAll("[^a-zA-Z0-9.-]", "_");
            var directory = Path.of(artifactDirectory);
            Files.createDirectories(directory);
            Files.write(directory.resolve(safeName + ".png"), screenshotDriver.getScreenshotAs(OutputType.BYTES));
        } catch (IOException exception) {
            throw new IllegalStateException("Could not write Selenium screenshot artifact.", exception);
        }
    }
}
