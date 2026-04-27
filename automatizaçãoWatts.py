import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import traceback
from datetime import datetime
import threading  # Para rodar o envio sem travar a interface
import pyperclip

# ------------------------
# Configurações do envio
# ------------------------
TEMPO_ENVIO_IMAGENS = 10
TEMPO_ESPERA = 10
TEMPO_REENVIO = 10
MAX_TENTATIVAS = 3
ARQUIVO_LOG = "envios.log"
ARQUIVO_ERROS = "erros.log"

REPETICOES = 1
INTERVALO = 6
log_interface = print  # padrão (fallback)
PASTA_BASE = os.path.join(os.getcwd(), "imgs_2")
PASTAS = [
    os.path.join(PASTA_BASE, p)
    for p in os.listdir(PASTA_BASE)
    if os.path.isdir(os.path.join(PASTA_BASE, p))
]
def set_log_callback(func):
    global log_interface
    log_interface = func
    
if not PASTAS:
    log_interface("⚠️ Nenhuma pasta encontrada dentro de 'imgs'.")
    print("⚠️ Nenhuma pasta encontrada dentro de 'imgs'.")
    exit(1)


# ------------------------
# Leitura dos grupos a partir de um único arquivo
# ------------------------
def ler_grupos_de_arquivo(nome_arquivo="grupos.txt"):
    caminho = os.path.join(os.getcwd(), nome_arquivo)
    if not os.path.exists(caminho):
        log_interface(f"⚠️ Arquivo '{nome_arquivo}' não encontrado. Crie-o na mesma pasta do script.")
        print(
            f"⚠️ Arquivo '{nome_arquivo}' não encontrado. Crie-o na mesma pasta do script."
        )
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        grupos = [linha.strip() for linha in f.readlines() if linha.strip()]
    log_interface(f"✅ {len(grupos)} grupos carregados do arquivo '{nome_arquivo}'.")

    print(f"✅ {len(grupos)} grupos carregados do arquivo '{nome_arquivo}'.")
    return grupos


grupos = ler_grupos_de_arquivo()

if not grupos:
    print("⚠️ Nenhum grupo encontrado. Verifique o conteúdo de 'grupos.txt'.")
    exit(1)

# ------------------------
# Configuração do Chrome com perfil
# ------------------------
user_data_dir = os.path.join(os.getcwd(), "selenium_profile")
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument("--profile-directory=Default")
options.add_argument("--remote-debugging-port=9222")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")
log_interface("📌 Escaneie o QR Code do WhatsApp (se necessário)...")
print("📌 Escaneie o QR Code do WhatsApp (se necessário)...")
time.sleep(TEMPO_ESPERA)


# ------------------------
# Função principal - enviando pasta para grupo
# ------------------------
def enviar_pasta_para_grupo(grupo, pasta):
    tentativas = 0
    enviado = False

    imagens = [
        os.path.abspath(os.path.join(pasta, arquivo))
        for arquivo in os.listdir(pasta)
        if arquivo.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ]

    arquivo_texto = None
    for arquivo in os.listdir(pasta):
        if arquivo.lower().endswith(".txt"):
            arquivo_texto = os.path.abspath(os.path.join(pasta, arquivo))
            break

    if not imagens:
        msg = f"⚠️ Nenhuma imagem encontrada em {pasta}"
        log_interface(msg)
        with open(ARQUIVO_ERROS, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {msg}\n")
        return

    while tentativas < MAX_TENTATIVAS and not enviado:
        try:
            tentativas += 1
            log_interface(f"📤 Enviando '{os.path.basename(pasta)}' para: {grupo} (Tentativa {tentativas})")

            # 🔍 Buscar grupo
            search_box = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.presence_of_element_located((By.XPATH, '//input[@data-tab="3"]'))
            )
            search_box.clear()
            search_box.click()
            time.sleep(0.3)
            
            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)
            
            pyperclip.copy(grupo)
            search_box.send_keys(Keys.CONTROL, "v")
            
            time.sleep(2)

            try:
                grupo_elemento = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//span[contains(@title, "{grupo}")]')
                    )
                )
                
                grupo_elemento.click()
            except:
                log_interface(f"⚠️ Grupo '{grupo}' não encontrado")
                return

            # ⏳ Espera chat abrir
            WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.presence_of_element_located((By.XPATH, '//header//span[@dir="auto"]'))
            )
            # 📝 LEGENDA (100% estável)
            if arquivo_texto:
                try:
                    with open(arquivo_texto, "r", encoding="utf-8") as f:
                        texto_msg = f.read().strip()
            
                    if texto_msg:
                        # ⏳ espera o preview REAL aparecer (IMPORTANTE)
                        WebDriverWait(driver, TEMPO_ESPERA).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
                            )
                        )
            
                        time.sleep(2)  # deixa WhatsApp terminar animação
            
                        # pega TODOS os campos de texto
                        caixas = driver.find_elements(By.XPATH, "//div[@role='textbox' and @contenteditable='true']")
            
                        if not caixas:
                            raise Exception("Nenhuma caixa de texto encontrada")
            
                        legenda_box = caixas[-1]  # sempre o último é a legenda
            
                        # 🔥 FORÇA FOCO (resolve 99% dos bugs)
                        driver.execute_script("arguments[0].focus();", legenda_box)
                        driver.execute_script("arguments[0].click();", legenda_box)
            
                        time.sleep(0.5)
            
                        # limpa qualquer coisa
                        legenda_box.send_keys(Keys.CONTROL + "a")
                        legenda_box.send_keys(Keys.DELETE)
            
                        # copia e cola
                        pyperclip.copy(texto_msg)
                        legenda_box.send_keys(Keys.CONTROL, "v")
            
                        time.sleep(2)
            
                except Exception as e:
                    print(f"⚠️ Erro legenda: {e}")
            # 📎 Abrir anexo
            attach_btn = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-icon='plus-rounded']"))
            )
            attach_btn.click()
            time.sleep(1)

            # 📂 Clicar em fotos
            botao_fotos = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Fotos')]"))
            )
            driver.execute_script("arguments[0].click();", botao_fotos)
            time.sleep(1)

            # 📂 Pegar input correto
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            file_input = file_inputs[-1]

            file_input.send_keys("\n".join(imagens))

            # ⏳ Espera abrir preview
            time.sleep(3)

            # 📤 Enviar
            send_btn = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@aria-label,'Enviar')]"))
            )

            driver.execute_script("arguments[0].click();", send_btn)

            log_interface(f"✅ Enviado para {grupo}")
            time.sleep(TEMPO_ENVIO_IMAGENS)
            # Log
            with open(ARQUIVO_LOG, "a", encoding="utf-8") as log:
                log.write(
                    f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] ✅ Grupo: {grupo} | Pasta: {os.path.basename(pasta)} | Imagens: {len(imagens)}\n"
                )

            enviado = True

        except Exception as e:
            erro_msg = f"❌ Erro ao enviar pasta '{os.path.basename(pasta)}' para {grupo}: {e}"
            print(erro_msg)
            log_interface(erro_msg)
            
            with open(ARQUIVO_ERROS, "a", encoding="utf-8") as log:
                log.write(erro_msg + "\n")
            if tentativas < MAX_TENTATIVAS:
                time.sleep(TEMPO_REENVIO)
        finally:
            # 🔥 LIMPA O CAMPO DE BUSCA SEMPRE (SUCESSO OU ERRO)
            try:
                search_box = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@data-tab="3"]'))
                )

                search_box.click()
                time.sleep(0.3)

                # limpa corretamente
                search_box.send_keys(Keys.CONTROL + "a")
                search_box.send_keys(Keys.DELETE)

                time.sleep(0.5)

            except:
                pass
# ------------------------
# Envio completo
# ------------------------
def enviar_para_todos_grupos():
    if not grupos:
        messagebox.showwarning(
            "Aviso", "Nenhum grupo encontrado no arquivo 'grupos.txt'."
        )
        return

    for r in range(1, REPETICOES + 1):
        print(f"\n🔄 Repetição {r}/{REPETICOES}")
        log_interface(f"\n🔄 Repetição {r}/{REPETICOES}")
        for idx_pasta, pasta in enumerate(PASTAS):
            print(
                f"\n📂 Enviando pasta {os.path.basename(pasta)} ({idx_pasta+1}/{len(PASTAS)})"
            )
            log_interface(f"\n📂 Enviando pasta {os.path.basename(pasta)} ({idx_pasta+1}/{len(PASTAS)})")
            for grupo in grupos:
                enviar_pasta_para_grupo(grupo, pasta)
        if r < REPETICOES:
            print(f"⏳ Aguardando {INTERVALO}s antes da próxima repetição...")
            log_interface(f"⏳ Aguardando {INTERVALO}s antes da próxima repetição...")
            time.sleep(INTERVALO)

    messagebox.showinfo("Concluído", "✅ Envio finalizado com sucesso!")


# ------------------------
# Função chamada pelo botão - envio em ciclo
# ------------------------
# ------------------------
# Variável global para armazenar grupos escolhidos
# ------------------------
grupos_selecionados = []


# ------------------------
# Função chamada pelo botão - envio em ciclo
# ------------------------
def iniciar_envio_interface():
    global grupos_selecionados
    if not grupos_selecionados:
        messagebox.showwarning("Aviso", "Selecione pelo menos uma opção de envio!")
        return

    def enviar_thread():
        for r in range(1, REPETICOES + 1):
            print(f"\n🔄 Repetição {r}/{REPETICOES}")
            log_interface(f"\n🔄 Repetição {r}/{REPETICOES}")
            for idx_pasta, pasta in enumerate(PASTAS):
                print(
                    f"\n📂 Enviando pasta {os.path.basename(pasta)} ({idx_pasta+1}/{len(PASTAS)})"
                )
                log_interface(f"\n📂 Enviando pasta {os.path.basename(pasta)} ({idx_pasta+1}/{len(PASTAS)})")
                for grupo in grupos_selecionados:
                    enviar_pasta_para_grupo(grupo, pasta)
            if r < REPETICOES:
                print(f"⏳ Aguardando {INTERVALO}s antes da próxima repetição...")
                log_interface(f"⏳ Aguardando {INTERVALO}s antes da próxima repetição...")
                time.sleep(INTERVALO)
        messagebox.showinfo("Concluído", "Envio finalizado!")

    threading.Thread(target=enviar_thread, daemon=True).start()


def iniciar():
    enviar_para_todos_grupos()