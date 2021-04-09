import requests, time, csv
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument('--incognito')
options.add_argument("--start-maximized")

# Debemos añadir la ubicación de chromedriver.exe, en este caso, la carpeta del proyecto
driver_path = './chromedriver'
# driver_path = 'C:\\Users\\imase\\UOC Scraping\\chromedriver.exe'
chrome_browser = webdriver.Chrome(driver_path, options=options)


# La siguiente función genera una lista con los enlaces de los últimos coches añadidos en 
# ofertas de milanuncios, elegimos el número de links objetivo.
def get_links(targetLinks, selectedDelay, browser):
    url_base = 'https://www.milanuncios.com/coches-de-segunda-mano/'
    print('Estamos en la pagina: {}'.format(url_base))
    browser_url = browser.get(url_base)
    links = []
    delay = selectedDelay
    target_links = targetLinks
    counter = 1
    
    try:
        # Acepta las cookies.
        WebDriverWait(browser, delay)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                               'button.sui-AtomButton sui-AtomButton--primary sui-AtomButton--solid sui-AtomButton--center'.replace(' ', '.'))))\
            .click()

        # Selecciona "mas filtros" en el menu y hace click.
        WebDriverWait(browser, delay)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                               'button.ma-ButtonBasic ma-ButtonBasic--secondary ma-FormListFilters-formToggleFiltersBtn ma-ButtonBasic--medium'.replace(' ', '.'))))\
            .click()

        # Selecciona 'Oferta y demanda' en el menu.
        WebDriverWait(browser, delay)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                               'div.sui-FormBuilder-field sui-FormBuilder-DefaultSelect sui-FormBuilder-demanda'.replace(' ', '.'))))\
            .click()

        # Selecciona 'Oferta' en el menu desplegable.
        WebDriverWait(browser, delay)\
            .until(EC.element_to_be_clickable((By.XPATH,
                                               "//*[@id='app']/div/div/div/div/div/div/main/header/form/div/fieldset/div/div/div/div/div/ul/li/span[text()='Oferta']")))\
            .click()
    
        # Selecciona ordenas por en el menu.
        WebDriverWait(browser, delay)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                               'div.sui-FormBuilder-field sui-FormBuilder-DefaultSelect sui-FormBuilder-orden'.replace(' ', '.'))))\
            .click()
    
        # Selecciona 'Ordenas por fecha' en el menu desplegable.
        WebDriverWait(browser, delay)\
            .until(EC.element_to_be_clickable((By.XPATH,
                                               "//*[@id='app']/div/div/div/div/div/div/main/header/form/div/fieldset/div/div/div/div/div/ul/li/span[text()='Ordenar por fecha']")))\
            .click()

        # Click en 'Ver xxx resultados'.
        WebDriverWait(browser, delay)\
            .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                               'button.ma-ButtonBasic ma-ButtonBasic--search ma-FormListFilters-formSubmitBtn ma-ButtonBasic--medium'.replace(' ', '.'))))\
            .click()
    except TimeoutException:
        print("No es posible cargar la página de busqueda por ofertas")


    # Utiliza la barra de desplazamiento por la  página hasta encontrar el botón siguiente.
    while (counter <= target_links):
        match = False
        error = True
        scroll = 400
    
        while (match==False):
            scroll = scroll+800
            browser.execute_script("window.scrollTo(0, {});".format(str(scroll)))
            try: 
                next_page = WebDriverWait(browser, 0)\
                                .until(EC.presence_of_element_located((By.XPATH,
                                                                       "//*[@id='app']/div/div/div/div/div/div/main/div/button/span[text()='>']")))
                match = True
            except TimeoutException:
                continue
            time.sleep(1)
    
        # guarda todos los enlaces de anuncios hasta el límite definido. 
        for i in browser.find_elements_by_xpath('//*[@id="app"]/div/div/div/div/div/div/main/div/article/div/div/div/h2/a'):
            if (counter<=targetLinks):
                counter+=1
                links.append(i.get_attribute('href'))
            else:
                print("El proceso de obtención de links finalizado")
                return links
        
        # En ocasiones aparece un elemento que puede provocar un error ElementClickInterceptedException, lo gesstionamos bajando la barra de desplazamiento:
        while error:
            try:
                next_page.click()
                error = False
            except (ElementClickInterceptedException, TimeoutException):
                scroll = scroll + 100
                browser.execute_script("window.scrollTo(0, {});".format(str(scroll)))
        
        time.sleep(1)
        
    
        
                


# La siguiente función extrae la información de todos los enlaces y genera un .csv con los datos
# informando de los datos que faltan en cada enlace y si el enlace ha sido eliminado.
def get_data(links, selectedDelay, csvFile, browser):
    delay = selectedDelay
    count = 1
    
    with open(csvFile, 'w', newline='', encoding='utf-8') as data_file:
        writer = csv.writer(data_file)
        writer.writerow(['url', 'titulo', 'referencia', 'marca', 'modelo', 'ano_vehic', 'km', 'combustible', 'puertas', 'cv',
                         'transmision', 'ubicacion', 'vendedor', 'precio', 'particular', 'stats_visto',
                         'stats_contactado', 'stats_compartido', 'stats_favorito', 'stats_renovados', 'descripcion'])

        for link in links:
            url = str(link)
            print('Añadiendo página({}): {}'.format(count, url))
            count+=1
            browser_link = browser.get(url)
            
            # Si quisieramos hacer que la barra de desplazamiento se moviera hasta el final en cada enlace, simulando un comportamiento mas humano, podríamos este código:
            #lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            #match=False
            
            #while(match==False):
                #lastCount = lenOfPage
                #time.sleep(3)
                #lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                #if lastCount==lenOfPage:
                    #match=True
            
            try:
                # Título del anuncio:
                titulo = WebDriverWait(browser, delay)\
                            .until(EC.presence_of_element_located((By.XPATH,
                                                                   '//h1[@class="ad-detail-title"]')))\
                            .text
                marca = titulo.split(" - ")[0]
                modelo = titulo.split(" - ")[1]

                # Nº de referencia del anuncio:
                referencia = WebDriverWait(browser, delay)\
                                .until(EC.presence_of_element_located((By.XPATH,
                                                                       '//div[@class="pillDiv pillRef"]')))\
                                .text.split()[1]
    
                # Características del vehículo:
                # Año:
                try:
                    ano_vehic = WebDriverWait(browser, delay)\
                                    .until(EC.presence_of_element_located((By.XPATH,
                                                                           '//div[@class="ano tag-mobile"]')))\
                                    .text.split()[1]
                except TimeoutException:
                    ano_vehic = "NULL"
                    print("El año del vehículo no está disponible")
    
                # Kilometraje:
                try:
                    km = WebDriverWait(browser, delay)\
                            .until(EC.presence_of_element_located((By.XPATH,
                                                                   '//div[@class="kms tag-mobile"]')))\
                            .text.split()[0]
                except TimeoutException:
                    km = "NULL"
                    print("Los kilómetros del vehículo no está disponible")

                # Tipo de combustible, gasolina/diesel:
                try:
                    combustible = WebDriverWait(browser, 0)\
                                    .until(EC.presence_of_element_located((By.XPATH,
                                                                           '//div[@class="die tag-mobile"]')))\
                                    .text
                except TimeoutException:
                    try:
                        combustible = WebDriverWait(browser, delay)\
                                        .until(EC.presence_of_element_located((By.XPATH,
                                                                               '//div[@class="gas tag-mobile"]')))\
                                        .text
                    except TimeoutException:
                        combustible = "NULL"
                        print("El tipo de combustible del vehículo no está disponible")
    
                # Nº de puertas del vehículo:
                try:
                    puertas = WebDriverWait(browser, delay)\
                                .until(EC.presence_of_element_located((By.XPATH,
                                                                       '//div[@class="ejes tag-mobile"]')))\
                                .text.split()[0]
                except TimeoutException:
                    puertas = "NULL"
                    print("El Nº de puertas del vehículo no está disponible")
    
                # Potencia del vehículo:
                try:
                    cv = WebDriverWait(browser, delay)\
                            .until(EC.presence_of_element_located((By.XPATH,
                                                                   '//div[@class="cc tag-mobile"]')))\
                            .text.split()[0]
                except TimeoutException:
                    cv = "NULL"
                    print("La potencia del vehículo no está disponible")
    
                # Tipo de cambio del vehículo, automático/manual:
                try:
                    transmision = WebDriverWait(browser, 0)\
                                    .until(EC.presence_of_element_located((By.XPATH,
                                                                           '//div[@class="cmanual tag-mobile"]')))\
                                    .text
                except TimeoutException:
                    try:
                        transmision = WebDriverWait(browser, delay)\
                                        .until(EC.presence_of_element_located((By.XPATH,
                                                                               '//div[@class="cauto tag-mobile"]')))\
                                        .text
                    except TimeoutException:
                        transmision = "NULL"
                        print("El tipo de transmisión del vehículo no está disponible")
    
                # Ubicación del vehículo:
                try:
                    ubicacion = WebDriverWait(browser, delay)\
                                    .until(EC.presence_of_element_located((By.XPATH,
                                                                           '//div[@class="pagAnuCatLoc"]')))\
                                    .text
                    ubicacion = re.search(r'\((.*?)\)',ubicacion).group(1)
                except TimeoutException:
                        ubicacion = "NULL"
                        print("La ubicación del vehículo no está disponible")

                # Nombre del vendedor:
                try:
                    vendedor = WebDriverWait(browser, delay)\
                                .until(EC.presence_of_element_located((By.XPATH,
                                                                       '//h2[@class="ma-UserOverview-name"]')))\
                                .text
                except TimeoutException:
                        vendedor = "NULL"
                        print("El nombre del vendedor no está disponible")

                # Precio del vehículo:
                try:
                    precio = WebDriverWait(browser, delay)\
                                .until(EC.presence_of_element_located((By.XPATH,
                                                                       '//div[@class="pagAnuPrecioTexto"]')))\
                                .text.split()[0]
                except TimeoutException:
                        precio = "NULL"
                        print("El precio del vehículo no está disponible")

                # Tipo de anunciante, particular/profesional:
                try:
                    particular = WebDriverWait(browser, delay)\
                                    .until(EC.presence_of_element_located((By.XPATH,
                                                                           '//div[@class="pagAnuSubtitle"]/div[2]')))\
                                    .text
                except TimeoutException:
                        particular = "NULL"
                        print("El tipo de vendedor no está disponible")

                # Estadísticas del canuncio:
                # Nº de veces listado:
                try:
                    stats_visto = WebDriverWait(browser, delay)\
                                    .until(EC.presence_of_element_located((By.XPATH,
                                                                           '//div[@class="pagAnuStats"]/div[3]/div[1]/div[1]')))\
                                    .text
                except TimeoutException:
                        stats_visto = "NULL"
                        print("La estadística Nº veces listado no está disponible")

                # Nº de veces contactado:
                try:
                    stats_contactado = WebDriverWait(browser, delay)\
                                        .until(EC.presence_of_element_located((By.XPATH,
                                                                               '//div[@class="pagAnuStats"]/div[3]/div[2]/div[1]')))\
                                        .text
                except TimeoutException:
                        stats_contactado = "NULL"
                        print("La estadística Nº veces contactado no está disponible")

                # Nº de veces compartido:
                try:
                    stats_compartido = WebDriverWait(browser, delay)\
                                        .until(EC.presence_of_element_located((By.XPATH,
                                                                               '//div[@class="pagAnuStats"]/div[4]/div[1]/div[1]')))\
                                        .text
                except TimeoutException:
                    stats_compartido = "NULL"
                    print("La estadística Nº veces compartido no está disponible")

                # Nº de veces añadido a favoritos:
                try:
                    stats_favorito = WebDriverWait(browser, delay)\
                                        .until(EC.presence_of_element_located((By.XPATH,
                                                                               '//div[@class="pagAnuStats"]/div[4]/div[2]/div[1]')))\
                                        .text
                except TimeoutException:
                    stats_favorito = "NULL"
                    print("La estadística Nº veces añadido a favoritos no está disponible")

                # Nº veces renovado:
                try:
                    stats_renovados = WebDriverWait(browser, delay)\
                                        .until(EC.presence_of_element_located((By.XPATH,
                                                                               '//div[@class="pagAnuStats"]/div[5]/div[1]/div[1]')))\
                                        .text
                except TimeoutException:
                    stats_renovados = "NULL"
                    print("La estadística Nº veces renovado no está disponible")
    
                # Descripción del anuncio:
                # Reemplazamos las comas por '#', a la hora de leer los datos haremos la
                # misma conversión,para facilitar la gestión del csv.
                try:
                    descripcion = WebDriverWait(browser, delay)\
                                    .until(EC.presence_of_element_located((By.XPATH,
                                                                           '//p[@class="pagAnuCuerpoAnu"]')))\
                                    .text.replace(',', '#')
                except TimeoutException:
                    descripcion = "NULL"
                    print("No hay descripción del vehículo")

                '''Podríamos guardar los datos en una lista por si fuera necesario:
                save_data.append([url, titulo, referencia, ano_vehic, km, combustible, puertas, cv,
                                 transmision, ubicacion, vendedor, precio, particular, stats_visto,
                                 stats_contactado, stats_compartido, stats_favorito, stats_renovados, descripcion])'''
                # Guardamos la información por lineas:
                writer.writerow([url, titulo, referencia, marca, modelo, ano_vehic, km, combustible, puertas, cv,
                                 transmision, ubicacion, vendedor, precio, particular, stats_visto,
                                 stats_contactado, stats_compartido, stats_favorito, stats_renovados, descripcion])

            except TimeoutException:
                print("LA PÁGINA ({})".format(url))
                print("TARDA DEMASIADO EN CARGAR O NO EXISTE")
                
    data_file.close()
    print("El proceso de obtención de datos ha finalizado")


# Esta función comprueba los links que ya han sido procesados previamente en un archivo de texto,
# en nuestro caso links.txt, si ya hemos scrapeado esos links los omite y añade los nuevos a la lista.
def check_links(newLinks, file):
    old_links = []
    new_links = []
    
    try:
        with open(file, 'r') as output1:
            line = output1.readline()
            while line:
                old_links.append(line.rstrip('\n'))
                line = output1.readline()
        output1.close()
    except FileNotFoundError:
        print("La lista de links no existe, creando...")
        f = open(file,"w")
        f.close()
    
    with open(file, 'a', newline='', encoding='utf-8') as output2:
        for i in newLinks:
            if i in old_links:
                print(i)
                print("El enlace ya existe, se omitirá")
                pass
            else:
                new_links.append(i)
                output2.write(str(i) + '\n')

    output2.close()
    
    return new_links
    
    print("El proceso de comprobación ha finalizado")
                
    
links = get_links(500, 5, chrome_browser)
links = check_links(links, "links.txt")
get_data(links, 5, "coches_milanuncios_09_04_2021.csv", chrome_browser)
print("El proceso ha finalizado")
