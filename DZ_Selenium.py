import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd


def fetch_vacancies(page):
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36")
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.get(url=f"https://hh.ru/vacancies/specialist_po_logistike?page={page-1}&searchSessionId=e1e0606e-6e73-4eee-9e73-7f35fbc64c5d")

    try:
        with open("index_selenium.html", 'w', encoding="utf-8") as file:
            file.write(driver.page_source)

    except Exception as er:
        print(f'Ошибка {er}')

    finally:
        driver.close()
        driver.quit()
    with open("index_selenium.html", 'r', encoding="utf-8") as file:
        scr = file.read()
    soup = BeautifulSoup(scr, "html.parser")

    vacancies = []
    for vacancy in soup.find_all("div", class_="magritte-card___bhGKz_6-1-15 magritte-card-border-radius-24___o72BE_6-1-15 magritte-card-stretched___0Uc0J_6-1-15 magritte-card-action___4A43B_6-1-15 magritte-card-shadow-on-hover___BoRL3_6-1-15 magritte-card-with-border___3KsrG_6-1-15"):
        v_name = vacancy.find("h2", attrs={"data-qa" : "bloko-header-2"})
        v_url = v_name.find("a").get('href')
        v_salary_experience = vacancy.find("div", class_="adv-mark-container--rB5pzIrX1X4VJHh8")
        if v_salary_experience:
            v_salary_experience = v_salary_experience
            v_salary = v_salary_experience.find("span", class_="magritte-text___pbpft_3-0-18 magritte-text_style-primary___AQ7MW_3-0-18 magritte-text_typography-label-1-regular___pi3R-_3-0-18")
            if v_salary:
                v_salary = v_salary.text
            else:
                v_salary = "Информация отсутствует"
            v_experience = v_salary_experience.find("div", class_="magritte-tag__label___YHV-o_3-0-21")
            if v_experience:
                v_experience = v_experience.text
            else:
                v_experience = "Информация отсутствует"
        else:
            v_salary = "Информация отсутствует"
            v_experience = "Информация отсутствует"

        v_company_main = vacancy.find("div", class_="info-section--YaC_npvTFcwpFd1I")
        v_company_name = v_company_main.find("a", class_="magritte-link___b4rEM_4-3-12 magritte-link_style_neutral___iqoW0_4-3-12")
        if v_company_name:
            v_company_name = v_company_name.text
        else:
            v_company_name = "Информация отсутствует"
        v_company_city = v_company_main.find("span", attrs={"data-qa" : "vacancy-serp__vacancy-address"})
        if v_company_city:
            v_company_city = v_company_city.text
        else:
            v_company_city = "Информация отсутствует"
        v_company_metro = v_company_main.find("span", class_="metro-station")
        if v_company_metro:
            v_company_metro = v_company_metro.text
        else:
            v_company_metro = "Информация отсутствует"
        vacancies.append(
            {"Ссылка": v_url, "Название должности": v_name.text, "Зарплата": v_salary, "Необходимый опыт": v_experience,
             "Название компании": v_company_name, "Город": v_company_city, "Станция метро": v_company_metro})

    return vacancies


def main():
    all_vacancies = []
    pages_to_fetch = 15

    for page in range(1, pages_to_fetch + 1):
        print(f"Сбор предложений со страницы {page}...")
        vacancies = fetch_vacancies(page)
        all_vacancies.extend(vacancies)
        time.sleep(5)  # Чтобы не нагружать сервер

    # Сохраняем в файл
    df = pd.DataFrame(all_vacancies)
    df.to_csv('vacancies_python.csv', index=False, encoding='utf-8')


print(f"Собрано предложений. Данные сохранены в файл vacancies_python.csv.")

if __name__ == '__main__':
    main()