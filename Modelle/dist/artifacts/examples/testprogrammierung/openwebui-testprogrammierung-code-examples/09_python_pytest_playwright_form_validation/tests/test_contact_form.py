from __future__ import annotations

import os

from playwright.sync_api import Page, expect

from pages.contact_form_page import ContactFormPage


def test_invalid_email_shows_inline_validation(page: Page) -> None:
    base_url = os.environ.get("APP_BASE_URL", "https://example.test")
    form = ContactFormPage(page)

    form.open(base_url)
    form.submit_with_invalid_email()

    expect(form.email_error).to_have_text("Enter a valid email address")


def test_valid_message_shows_success_banner(page: Page) -> None:
    base_url = os.environ.get("APP_BASE_URL", "https://example.test")
    test_email = os.environ.get("CONTACT_TEST_EMAIL", "qa@example.test")
    form = ContactFormPage(page)

    form.open(base_url)
    form.submit_valid_message(test_email)

    expect(form.success_banner).to_have_text("Your message was sent")
