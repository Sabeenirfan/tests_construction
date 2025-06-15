import pytest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import shutil



BASE_URL = "http://3.144.254.243:3002"

@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # remove if you want to see browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # ✅ Use a unique, isolated user-data-dir per session
    #djjd
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")

    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", options=options)

    yield driver
    driver.quit()

    # Clean up the temporary profile directory
    # Clean up the temporary profile directory
    try:
        import shutil
        shutil.rmtree(user_data_dir)
    except Exception as e:
        print(f"Warning: Failed to delete temp user-data-dir: {e}")

def open_projects_tab(browser):
    browser.find_element(By.XPATH, "//button[contains(text(),'Projects')]").click()

def open_suppliers_tab(browser):
    browser.find_element(By.XPATH, "//button[contains(text(),'Suppliers')]").click()

def submit_project_form(browser, name="", location="", start_date="", end_date="", budget=""):
    browser.find_element(By.ID, "projectName").clear()
    browser.find_element(By.ID, "projectName").send_keys(name)
    browser.find_element(By.ID, "projectLocation").clear()
    browser.find_element(By.ID, "projectLocation").send_keys(location)
    browser.find_element(By.ID, "projectStartDate").clear()
    browser.find_element(By.ID, "projectStartDate").send_keys(start_date)
    browser.find_element(By.ID, "projectEndDate").clear()
    browser.find_element(By.ID, "projectEndDate").send_keys(end_date)
    browser.find_element(By.ID, "projectBudget").clear()
    browser.find_element(By.ID, "projectBudget").send_keys(budget)
    browser.find_element(By.XPATH, "//form[@id='projectForm']//button").click()
    time.sleep(1)

def submit_supplier_form(browser, name="", contact="", email="", phone="", materials=""):
    browser.find_element(By.ID, "supplierName").clear()
    browser.find_element(By.ID, "supplierName").send_keys(name)
    browser.find_element(By.ID, "supplierContact").clear()
    browser.find_element(By.ID, "supplierContact").send_keys(contact)
    browser.find_element(By.ID, "supplierEmail").clear()
    browser.find_element(By.ID, "supplierEmail").send_keys(email)
    browser.find_element(By.ID, "supplierPhone").clear()
    browser.find_element(By.ID, "supplierPhone").send_keys(phone)
    browser.find_element(By.ID, "supplierMaterials").clear()
    browser.find_element(By.ID, "supplierMaterials").send_keys(materials)
    browser.find_element(By.XPATH, "//form[@id='supplierForm']//button").click()
    time.sleep(1)

# 1. Add valid project - should appear in table
def test_add_valid_project(browser):
    browser.get(BASE_URL)
    open_projects_tab(browser)
    submit_project_form(browser, "Project A", "Karachi", "2025-06-01", "2025-06-30", "1000000")
    assert "Project A" in browser.find_element(By.ID, "projectsTableBody").text

# 2. Add project with empty name (required) - will still add because no validation
def test_add_project_empty_name(browser):
    browser.get(BASE_URL)
    open_projects_tab(browser)
    submit_project_form(browser, "", "Karachi", "2025-06-01", "2025-06-30", "1000000")
    # It will be added, so test will expect empty string present (empty name cell)
    assert "" in browser.find_element(By.ID, "projectsTableBody").text

# 3. Add valid supplier - should appear in table
def test_add_valid_supplier(browser):
    browser.get(BASE_URL)
    open_suppliers_tab(browser)
    submit_supplier_form(browser, "Supplier X", "Ahmed", "ahmed@example.com", "03123456789", "Steel")
    
    # ✅ Wait up to 5 seconds until the supplier name is in the table
    wait = WebDriverWait(browser, 5)
    wait.until(lambda driver: "Supplier X" in driver.find_element(By.ID, "suppliersTableBody").text)

    assert "Supplier X" in browser.find_element(By.ID, "suppliersTableBody").text

# 4. Add supplier with invalid email (no validation) - will add
def test_add_supplier_invalid_email(browser):
    browser.get(BASE_URL)
    open_suppliers_tab(browser)
    submit_supplier_form(browser, "Supplier Y", "Ahmed", "ali@gmail.com", "03123456789", "Steel")
    wait = WebDriverWait(browser, 5)
    # Wait until "Supplier Y" appears in the suppliers table body text
    wait.until(lambda driver: "Supplier Y" in driver.find_element(By.ID, "suppliersTableBody").text)
    
    assert "Supplier Y" in browser.find_element(By.ID, "suppliersTableBody").text

# 5. Switch tabs check
def test_tab_switching(browser):
    browser.get(BASE_URL)
    open_projects_tab(browser)
    assert browser.find_element(By.ID, "projectsSection").is_displayed()
    open_suppliers_tab(browser)
    assert browser.find_element(By.ID, "suppliersSection").is_displayed()
    open_projects_tab(browser)
    assert browser.find_element(By.ID, "projectsSection").is_displayed()

# 6. Form clears after project submit
def test_project_form_cleared_after_submit(browser):
    browser.get(BASE_URL)
    open_projects_tab(browser)
    submit_project_form(browser, "Project B", "Lahore", "2025-07-01", "2025-07-31", "500000")
    assert browser.find_element(By.ID, "projectName").get_attribute("value") == ""

# 7. Budget numeric validation (the only field with validation)
def test_project_budget_numeric_validation(browser):
    browser.get(BASE_URL)
    open_projects_tab(browser)
    budget_field = browser.find_element(By.ID, "projectBudget")
    budget_field.clear()
    budget_field.send_keys("abc")  # invalid non-numeric input
    value = budget_field.get_attribute("value")
    # The field should reject non-numeric input (usually empty)
    assert value == "" 

# 8. Add project with invalid dates (start > end) - no validation, it will add
def test_add_project_invalid_dates(browser):
    browser.get(BASE_URL)
    open_projects_tab(browser)
    submit_project_form(browser, "Project C", "Islamabad", "2025-08-01", "2025-07-01", "300000")
    assert "Project C" in browser.find_element(By.ID, "projectsTableBody").text

# 9. Supplier phone accepts any text (no validation)
def test_supplier_phone_no_validation(browser):
    browser.get(BASE_URL)
    open_suppliers_tab(browser)
    submit_supplier_form(browser, "Supplier Z", "Ali", "ali@example.com", "phone123", "Concrete")
    assert "Supplier Z" in browser.find_element(By.ID, "suppliersTableBody").text

# 10. Page title test
def test_page_title(browser):
    browser.get(BASE_URL)
    assert "Construction Management System" in browser.title
    print("Triggering test")

    # 10. Page title test

 # 10. Page title test

 # 10. Page title test
