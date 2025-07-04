from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Generated by Selenium IDE

def login():
  options = Options()
  # Ejecutar en segundo plano
  options.add_argument("--headless")
  driver = webdriver.Chrome(options=options)
  driver.get("https://playdede.me/")
  driver.set_window_size(1920, 1040)
  driver.find_element(By.LINK_TEXT, "Iniciar sesión").click()
  driver.find_element(By.NAME, "user").send_keys("Prueba983")
  driver.find_element(By.NAME, "pass").send_keys("Prueba983")
  driver.find_element(By.CSS_SELECTOR, ".buttons:nth-child(5) > button:nth-child(2)").click()
  WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "carousel")))
  driver.find_element(By.CSS_SELECTOR, "#menu-item-6892 > a").click()
  cookies= driver.get_cookie("PLAYDEDE_SESSION")["value"], driver.get_cookie("cf_clearance")["value"], driver.get_cookie("utoken")["value"]
  driver.quit()
  headers = {'PLAYDEDE_SESSION': cookies[0],
             'cf_clearance': cookies[1],
             'utoken': cookies[2]}
  return headers


