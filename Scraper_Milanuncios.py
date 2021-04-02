import requests, time, csv
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument('--incognito')

driver_path = './chromedriver'
# driver_path = 'C:\\Users\\imase\\UOC Scraping\\chromedriver.exe'

browser = webdriver.Chrome(driver_path, options=options)

url_base = 'https://www.milanuncios.com/coches-de-segunda-mano/'
print('Estamos en la pagina: '+url_base)
browser_url = browser.get(url_base)

# closes the cookies box
WebDriverWait(browser, 5)\
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                         'button.sui-AtomButton sui-AtomButton--primary sui-AtomButton--solid sui-AtomButton--center'.replace(' ', '.'))))\
    .click()

# selects 'Más filtros' drop down menu
WebDriverWait(browser, 5)\
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                         'button.ma-ButtonBasic ma-ButtonBasic--secondary ma-FormListFilters-formToggleFiltersBtn ma-ButtonBasic--medium'.replace(' ', '.'))))\
    .click()

# selects 'Oferta y demanda' drop down menu
WebDriverWait(browser, 5)\
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                         'div.sui-FormBuilder-field sui-FormBuilder-DefaultSelect sui-FormBuilder-demanda'.replace(' ', '.'))))\
    .click()

#browser.find_element_by_xpath("//*[@id='app']/div/div/div/div/div/div/main/header/form/div/fieldset/div/div/div/div/div/ul/li/span[text()='Oferta']").click()

# selects 'Oferta' in the drop down menu
WebDriverWait(browser, 5)\
    .until(EC.element_to_be_clickable((By.XPATH,
                                         "//*[@id='app']/div/div/div/div/div/div/main/header/form/div/fieldset/div/div/div/div/div/ul/li/span[text()='Oferta']")))\
    .click()

# click on 'Ver xxx resultados'
WebDriverWait(browser, 5)\
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                         'button.ma-ButtonBasic ma-ButtonBasic--search ma-FormListFilters-formSubmitBtn ma-ButtonBasic--medium'.replace(' ', '.'))))\
    .click()

links = []

target_links = 5

while (len(links) < target_links):
    scroll = 400
    for i in range(1,15):
        scroll = scroll+1000
        browser.execute_script("window.scrollTo(0, "+str(scroll)+");")
        time.sleep(1)
    
    # gets link to each ad
    for i in browser.find_elements_by_xpath('//*[@id="app"]/div/div/div/div/div/div/main/div/article/div/div/div/h2/a'):
        links.append(i.get_attribute('href'))
    
    #browser.find_element_by_xpath("//*[@id='app']/div/div/div/div/div/div/main/div/button/span[text()='>']").click()
    
    WebDriverWait(browser, 5)\
        .until(EC.element_to_be_clickable((By.XPATH,
                                         "//*[@id='app']/div/div/div/div/div/div/main/div/button/span[text()='>']")))\
        .click()
    time.sleep(1)

save_data = []
output = 'data.csv'
data_file = open(output, 'w')
writer = csv.writer(data_file)
writer.writerow(['url', 'titulo', 'referencia', 'descripcion', 'ubicacion', 'vendedor', 'precio', 'particular', 'stats_visto', 'stats_contactado', 'stats_compartido', 'stats_favorito', 'stats_renovados'])

for link in links:
    url = str(link)
    print('Estamos en el item: '+url)
    browser_link = browser.get(url)
    element_present0 = EC.presence_of_element_located((By.XPATH,'/html/body/div[1]/div[1]/div[5]/div/div[2]/div[2]/div[1]'))
    WebDriverWait(browser, 6).until(element_present0)
    titulo = browser.find_element_by_xpath('//h1').text
    referencia = browser.find_element_by_xpath('//div[@class="pillDiv pillRef"]').text
    descripcion = browser.find_element_by_xpath('//p[@class="pagAnuCuerpoAnu"]').text
    ubicacion = browser.find_element_by_xpath('//div[@class="pagAnuCatLoc"]').text
    vendedor = browser.find_element_by_xpath('//h2[@class="ma-UserOverview-name"]').text        
    precio = browser.find_element_by_xpath('//div[@class="pagAnuPrecioTexto"]').text
    particular = browser.find_element_by_xpath('//div[@class="pagAnuSubtitle"]/div[2]').text
    stats_visto = browser.find_element_by_xpath('//div[@class="pagAnuStats"]/div[3]/div[1]/div[1]').text
    stats_contactado = browser.find_element_by_xpath('//div[@class="pagAnuStats"]/div[3]/div[2]/div[1]').text
    stats_compartido = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[5]/div/div[2]/div[2]/div[4]/div[1]/div[1]').text
    stats_favorito = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[5]/div/div[2]/div[2]/div[4]/div[2]/div[1]').text
    stats_renovados = browser.find_element_by_xpath('/html/body/div[1]/div[1]/div[5]/div/div[2]/div[2]/div[5]/div/div[1]').text
    save_data.append([url, titulo, referencia, descripcion, ubicacion, vendedor, precio, particular, stats_visto, stats_contactado, stats_compartido, stats_favorito, stats_renovados])
    writer.writerow([url, titulo, referencia, descripcion, ubicacion, vendedor, precio, particular, stats_visto, stats_contactado, stats_compartido, stats_favorito, stats_renovados])