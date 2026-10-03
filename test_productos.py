import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

@pytest.fixture(scope="module")
def driver():
    options = webdriver.ChromeOptions()
    options.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()

def test_01_autenticacion(driver):
    driver.get("https://productio.hande.ar/pages/login.php")
    
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "username")))
    
    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("password")
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    WebDriverWait(driver, 10).until(EC.url_contains("onboarding.php"))
    assert "onboarding.php" in driver.current_url
    
    time.sleep(1)
    driver.save_screenshot("captura_01_autenticacion.png")

def test_02_seleccion_planta(driver):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "fabricas-grid")))
    
    xpath_fabrica = "//div[contains(@class, 'fabrica-card') and .//div[contains(text(), 'Fábrica Norte')]]"
    fabrica_norte = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath_fabrica))
    )
    fabrica_norte.click()
    
    WebDriverWait(driver, 10).until(EC.url_contains("dashboard.php"))
    assert "dashboard.php" in driver.current_url
    
    time.sleep(1)
    driver.save_screenshot("captura_02_seleccion_planta.png")
    
    driver.get("https://productio.hande.ar/pages/productos.php")
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "btn-nuevo-producto")))

def test_03_validacion_campos_obligatorios_y_opcionales(driver):
    try:
        btn_nuevo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btn-nuevo-producto"))
        )
        driver.execute_script("arguments[0].click();", btn_nuevo)
        
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "producto-sku")))
        
        input_sku = driver.find_element(By.ID, "producto-sku")
        input_nombre = driver.find_element(By.ID, "producto-nombre")
        
        input_sku.clear()
        input_nombre.clear()
        
        es_sku_requerido = driver.execute_script("return arguments[0].required;", input_sku)
        es_nombre_requerido = driver.execute_script("return arguments[0].required;", input_nombre)
        
        assert es_sku_requerido is True
        assert es_nombre_requerido is True
        
        driver.find_element(By.ID, "producto-gramaje").send_keys("18.5")
        driver.find_element(By.ID, "producto-color").send_keys("Blanco")
        driver.find_element(By.ID, "producto-descripcion").send_keys("Prueba de campos opcionales")
        
        driver.find_element(By.ID, "form-producto").submit()
        
        formulario_abierto = driver.find_element(By.ID, "form-producto").is_displayed()
        assert formulario_abierto is True
        
        time.sleep(1)
        driver.save_screenshot("captura_03_validacion_campos.png")
        
    finally:
        try:
            btn_cerrar = driver.find_element(By.ID, "btn-overlay-close")
            driver.execute_script("arguments[0].click();", btn_cerrar)
        except Exception:
            pass

@pytest.mark.parametrize("sku, familia, nombre, validacion_esperada", [
    ("SKU-001", "SERVILLETAS", "Servilleta 33x33", "Exito"),
    ("SKU-002", "BOLSITAS", "Bolsa Kraft", "Exito"),
    ("SKU-003", "TROQUELADOS", "Caja Hamburguesa", "Exito"),
    ("SKU-001", "PAJITAS", "Pajita Bio", "Error Unicidad"),
])
def test_04_alta_producto_masiva(driver, sku, familia, nombre, validacion_esperada):
    try:
        btn_nuevo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btn-nuevo-producto"))
        )
        driver.execute_script("arguments[0].click();", btn_nuevo)
        
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "producto-sku")))
        
        input_sku = driver.find_element(By.ID, "producto-sku")
        input_sku.clear()
        input_sku.send_keys(sku)
        
        select_familia = Select(driver.find_element(By.ID, "producto-familia"))
        select_familia.select_by_value(familia)
        
        input_nombre = driver.find_element(By.ID, "producto-nombre")
        input_nombre.clear()
        input_nombre.send_keys(nombre)
        
        driver.find_element(By.ID, "producto-gramaje").clear()
        driver.find_element(By.ID, "producto-color").clear()
        driver.find_element(By.ID, "producto-descripcion").clear()
        
        driver.find_element(By.ID, "form-producto").submit()
        
        if validacion_esperada == "Error Unicidad":
            error_visible = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "notification-container"))
            ).is_displayed()
            assert error_visible is True
            
            time.sleep(1)
            driver.save_screenshot(f"captura_04_error_unicidad_{sku}.png")
        else:
            fila_tabla = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, f"//td[text()='{sku}']"))
            ).is_displayed()
            assert fila_tabla is True
            
            time.sleep(1)
            driver.save_screenshot(f"captura_04_alta_exito_{sku}.png")
            
    finally:
        try:
            btn_cerrar = driver.find_element(By.ID, "btn-overlay-close")
            driver.execute_script("arguments[0].click();", btn_cerrar)
        except Exception:
            pass

def test_05_rendimiento_alta(driver):
    try:
        btn_nuevo = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btn-nuevo-producto"))
        )
        driver.execute_script("arguments[0].click();", btn_nuevo)
        
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "producto-sku")))
        
        input_sku = driver.find_element(By.ID, "producto-sku")
        input_sku.clear()
        input_sku.send_keys("SKU-PERF-01")
        
        select_familia = Select(driver.find_element(By.ID, "producto-familia"))
        select_familia.select_by_value("VASOS")
        
        input_nombre = driver.find_element(By.ID, "producto-nombre")
        input_nombre.clear()
        input_nombre.send_keys("Prueba Rendimiento")
        
        driver.find_element(By.ID, "form-producto").submit()
        
        script_rendimiento = """
            let peticiones = window.performance.getEntriesByType('resource');
            let peticionApi = peticiones.filter(r => r.name.includes('api/productos'));
            return peticionApi.length > 0 ? peticionApi[peticionApi.length - 1].duration : 0;
        """
        tiempo_respuesta = driver.execute_script(script_rendimiento)
        
        assert tiempo_respuesta < 3000, f"Rendimiento degradado: {tiempo_respuesta} ms"
        
        time.sleep(1)
        driver.save_screenshot("captura_05_rendimiento_alta.png")
        
    finally:
        try:
            btn_cerrar = driver.find_element(By.ID, "btn-overlay-close")
            driver.execute_script("arguments[0].click();", btn_cerrar)
        except Exception:
            pass

def test_06_modificar_producto(driver):
    try:
        xpath_boton_editar = "//td[text()='SKU-002']/following-sibling::td//button[contains(text(), 'Editar')]"
        btn_editar = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath_boton_editar))
        )
        driver.execute_script("arguments[0].click();", btn_editar)
        
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "producto-nombre")))
        
        input_nombre = driver.find_element(By.ID, "producto-nombre")
        input_nombre.clear()
        input_nombre.send_keys("Bolsa Kraft Modificada")
        
        driver.find_element(By.ID, "form-producto").submit()
        
        elemento_modificado = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.XPATH, "//td[text()='Bolsa Kraft Modificada']"))
        )
        assert elemento_modificado.is_displayed() is True
        
        time.sleep(1)
        driver.save_screenshot("captura_06_modificacion_producto.png")
        
    finally:
        try:
            btn_cerrar = driver.find_element(By.ID, "btn-overlay-close")
            driver.execute_script("arguments[0].click();", btn_cerrar)
        except Exception:
            pass

def test_07_eliminar_producto(driver):
    xpath_boton_eliminar = "//td[text()='SKU-003']/following-sibling::td//button[contains(text(), 'Eliminar')]"
    btn_eliminar = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath_boton_eliminar))
    )
    driver.execute_script("arguments[0].click();", btn_eliminar)
    
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
    except Exception:
        pass
        
    invisibilidad = WebDriverWait(driver, 5).until(
        EC.invisibility_of_element_located((By.XPATH, "//td[text()='SKU-003']"))
    )
    assert invisibilidad is True
    
    time.sleep(1)
    driver.save_screenshot("captura_07_eliminacion_producto.png")