from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

# --- 1. CONFIGURAÇÕES INICIAIS ---
URL_PROTHEUS = "https://totvs.grupotb.com.br:4000/webapp/" 
LOGIN = "" 
SENHA = ""
AMBIENTE = ""

# Ordem de execução nas filiais
LISTA_FILIAIS = ['002001', '002004', '002014']

# --- 2. FUNÇÃO AUXILIAR DE CAPTURA DE ERRO ---
def capturar_erro_com_print(driver, filial):
    if not os.path.exists("ERROS_FILIAIS"):
        os.makedirs("ERROS_FILIAIS")
    
    agora = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = f"ERROS_FILIAIS/Erro_Importacao_{filial}_{agora}.png"
    driver.save_screenshot(caminho)
    print(f"📸 Print de erro capturado e salvo em: {caminho}")
    return caminho

# --- 3. MOTOR SHADOW DOM ---
def busca_shadow_dom_universal(driver, js_condition, description="elemento"):
    script_js = f"function findElementRecursive(root) {{ if (!root) return null; if ({js_condition}) {{ return root; }} if (root.shadowRoot) {{ const found = findElementRecursive(root.shadowRoot); if (found) return found; }} const children = root.children || root.childNodes; for (let i = 0; i < children.length; i++) {{ const found = findElementRecursive(children[i]); if (found) return found; }} return null; }} return findElementRecursive(document.body);"
    try: return driver.execute_script(script_js)
    except: return None

def esperar_elemento_shadow(driver, condicao_js, descricao, timeout=15, obrigatorio=True):
    print(f"Buscando: {descricao}...")
    t_ini = time.time()
    while time.time() - t_ini < timeout:
        el = busca_shadow_dom_universal(driver, condicao_js, descricao)
        if el: return el
        time.sleep(1)
    if obrigatorio: raise Exception(f"Erro: {descricao} não encontrado.")
    return None

def clicar_shadow(driver, condicao_js, descricao, timeout=15, obrigatorio=True):
    el = esperar_elemento_shadow(driver, condicao_js, descricao, timeout, obrigatorio)
    if el:
        driver.execute_script("arguments[0].focus(); arguments[0].click();", el)
        print(f" ✅ {descricao} clicado.")
        time.sleep(2)
    return el

def preencher_shadow(driver, condicao_js, texto, descricao):
    el = esperar_elemento_shadow(driver, condicao_js, descricao)
    if el:
        el.click()
        driver.execute_script("arguments[0].value = '';", el)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", el)
        time.sleep(0.5)
        el.send_keys(texto)
        time.sleep(1)

# --- 4. SELEÇÃO FILIAL (TELA DE LOGIN) ---
def selecionar_filial_inicial(driver, ambiente, filial):
    print(f"\n--- Selecionando Filial Inicial: {filial} ---")
    WebDriverWait(driver, 30).until(EC.frame_to_be_available_and_switch_to_it(0))
    espera = WebDriverWait(driver, 30)
    campos = espera.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.po-lookup-input")))
    if len(campos) >= 3:
        for i, val in [(1, filial), (2, ambiente)]:
            campos[i].click()
            campos[i].send_keys(Keys.CONTROL + "a", Keys.BACKSPACE)
            time.sleep(0.5)
            campos[i].send_keys(val, Keys.TAB)
            time.sleep(1)
        espera.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "po-button[name='submmit'] button"))).click()
    driver.switch_to.default_content()

# --- 5. FLUXO PRINCIPAL ---
def iniciar_automacao():
    op = Options()
    op.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe" 
    op.accept_insecure_certs = True 
    driver = webdriver.Firefox(options=op)
    driver.maximize_window()
    
    print("🚀 Abrindo Protheus... Aguardando carregamento inicial...")
    driver.get(URL_PROTHEUS)
    time.sleep(10)
    
    try:
        # Botoes Iniciais Opcionais (Avisos da tela de login)
        clicar_shadow(driver, "root.localName === 'wa-button' && root.getAttribute('caption') === 'Ok'", "OK Inicial", timeout=5, obrigatorio=False)
        clicar_shadow(driver, "root.localName === 'wa-button' && root.getAttribute('caption') === 'Fechar'", "Fechar Inicial", timeout=5, obrigatorio=False)

        # Login
        driver.switch_to.default_content()
        WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(0))
        for c, v in [("login", LOGIN), ("password", SENHA)]:
            el = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[name='{c}']")))
            el.click(); el.send_keys(v)
        driver.find_element(By.CSS_SELECTOR, "po-button.po-page-login-button button").click()
        driver.switch_to.default_content()

        # --- LOOP DE FILIAIS ---
        for index, filial_destino in enumerate(LISTA_FILIAIS):
            driver.switch_to.default_content()

            if index == 0:
                selecionar_filial_inicial(driver, AMBIENTE, filial_destino)
            else:
                # --- TROCA DE FILIAL INTERNA (002004 e 002014) ---
                print(f"\n--- Trocando para a Filial: {filial_destino} ---")
                clicar_shadow(driver, "root.id === 'COMP3055' || root.id === 'COMP3056'", "Botão Trocar Filial")
                time.sleep(2)

                # Preenche usando a tag wa-text-input para diferenciar do botão
                preencher_shadow(driver, "root.localName === 'wa-text-input' && root.id === 'COMP4512'", filial_destino, "Campo Filial")
                time.sleep(1)

                # Clica no Confirmar azul da tela de troca buscando pelo caption
                condicao_confirmar_troca = "root.localName === 'wa-button' && root.getAttribute('caption') === 'Confirmar' && root.offsetParent !== null"
                clicar_shadow(driver, condicao_confirmar_troca, "Botão Confirmar Mudança")
                
                print("⏳ Aguardando virada de filial no Protheus...")
                time.sleep(10)

            # --- PROCESSO BR SUPPLY ---
            print(f"Executando na Filial {filial_destino}...")
            time.sleep(5)
            clicar_shadow(driver, "root.getAttribute('title') && root.getAttribute('title').includes('Miscelanea')", "Menu Miscelanea")
            time.sleep(2)
            
            # Etapa 1: Importar
            clicar_shadow(driver, "root.localName === 'wa-menu-item' && root.getAttribute('caption').includes('Importa PC')", "Importa PC")
            print("   Aguardando processamento da importação..."); time.sleep(15)
            
            # --- SENTINELA: VERIFICAÇÃO DE ERRO DE VÍNCULO/PRODUTO ---
            condicao_erro = "root.innerText && (root.innerText.includes('vinculo') || root.innerText.includes('erro') || root.innerText.includes('referência') || root.innerText.includes('não cadastrado'))"
            erro_visto = esperar_elemento_shadow(driver, condicao_erro, "Verificação de Erros na Tela", timeout=5, obrigatorio=False)
            
            if erro_visto:
                print(f"❌ Erro detectado na Filial {filial_destino}!")
                capturar_erro_com_print(driver, filial_destino)
                
                # Limpa a tela fechando a janela de log/erro antes de ir para a próxima filial
                clicar_shadow(driver, "root.id === 'COMP6012' && root.offsetParent !== null", "Fechar Janela de Erro", timeout=5, obrigatorio=False)
                print(f"⏭️  Pulando geração da Filial {filial_destino} devido ao erro de vínculo.")
                continue # Salta direto para a próxima filial do loop 'for'

            # Etapa 2: Gerar (Só roda se a importação não apresentar erro)
            clicar_shadow(driver, "root.localName === 'wa-menu-item' && root.getAttribute('caption').includes('Gera PC')", "Gera PC")
            time.sleep(5)
            
            # Confirmação de Parâmetros (Aperta ENTER)
            el_conf = esperar_elemento_shadow(driver, "root.localName === 'wa-button' && root.id === 'COMP4522' && root.offsetParent !== null", "Confirmar Geração", timeout=10, obrigatorio=False)
            if el_conf: 
                print(" ⌨️  Enviando ENTER no Confirmar Geração...")
                el_conf.send_keys(Keys.ENTER)
                time.sleep(5)
            
            # Pergunta Sim/Não Final (Aperta ENTER)
            condicao_botao_sim = "root.localName === 'wa-button' && root.id === 'COMP4512' && root.offsetParent !== null"
            el_sim = esperar_elemento_shadow(driver, condicao_botao_sim, "Botão Sim Final", timeout=10, obrigatorio=False)
            if el_sim: 
                print(" ⌨️  Enviando ENTER no Sim...")
                el_sim.send_keys(Keys.ENTER)
                time.sleep(5)
            
            # Etapa 3: Fechar Janela de Log Pós-Processamento (Opcional com Timer de 5s)
            clicar_shadow(driver, "root.id === 'COMP6012' && root.offsetParent !== null", "Fechar Janela Log", timeout=5, obrigatorio=False)
            
            print(f"✅ Filial {filial_destino} concluída com sucesso!")

        print("\n🚀 AUTOMAÇÃO FINALIZADA EM TODAS AS FILIAIS!")
        
    except Exception as e: 
        print(f"\n❌ Script Interrompido por Falha Crítica: {e}")
    finally: 
        print("\nFim da execução."); time.sleep(5)
        driver.quit()

if __name__ == "__main__": 
    iniciar_automacao()