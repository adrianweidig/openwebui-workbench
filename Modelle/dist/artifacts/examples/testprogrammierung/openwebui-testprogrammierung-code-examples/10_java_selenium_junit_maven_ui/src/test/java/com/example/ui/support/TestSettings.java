package com.example.ui.support;

import java.net.URI;
import java.time.Duration;

public record TestSettings(URI baseUrl, boolean headless, Duration waitTimeout, String artifactDirectory) {
    public static TestSettings fromEnvironment() {
        var rawBaseUrl = System.getenv().getOrDefault("APP_BASE_URL", "https://example.test");
        var headless = !"0".equals(System.getenv().getOrDefault("HEADLESS", "1"));
        var artifactDirectory = System.getenv().getOrDefault("TEST_ARTIFACT_DIR", "target/selenium-artifacts");

        return new TestSettings(URI.create(rawBaseUrl), headless, Duration.ofSeconds(15), artifactDirectory);
    }
}
