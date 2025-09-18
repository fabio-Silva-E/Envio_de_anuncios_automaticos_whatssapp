from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime

# 📌 Configurações
TEMPO_ESPERA = 30  # tempo para login do WhatsApp
TEMPO_REENVIO = 10  # tempo para tentar novamente caso falhe
MAX_TENTATIVAS = 3  # número de tentativas por grupo
ARQUIVO_LOG = "envios.log"

REPETICOES = 1  # número de vezes que o ciclo completo será repetido
INTERVALO = 6  # intervalo em segundos entre cada repetição

# 📌 Carrega os grupos do arquivo
with open("grupos.txt", "r", encoding="utf-8") as f:
    GRUPOS = [linha.strip() for linha in f.readlines() if linha.strip()]

# 📌 Pega todas as pastas dentro de "imgs"
PASTA_BASE = os.path.join(os.getcwd(), "imgs")
PASTAS = [
    os.path.join(PASTA_BASE, p)
    for p in os.listdir(PASTA_BASE)
    if os.path.isdir(os.path.join(PASTA_BASE, p))
]

if not PASTAS:
    print("⚠️ Nenhuma pasta encontrada dentro de 'imgs'.")
    exit(1)

# Configuração do Chrome com perfil salvo
user_data_dir = os.path.join(os.getcwd(), "selenium_profile")
options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument("--profile-directory=Default")
options.add_argument("--remote-debugging-port=9222")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")

print("📌 Escaneie o QR Code do WhatsApp (se necessário)...")
time.sleep(TEMPO_ESPERA)


def enviar_pasta(grupo, pasta):
    """Envia todas as imagens de UMA pasta como UMA mensagem única + mensagem em branco depois"""
    tentativas = 0
    enviado = False
    imagens = [
        os.path.abspath(os.path.join(pasta, arquivo))
        for arquivo in os.listdir(pasta)
        if arquivo.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ]

    if not imagens:
        print(f"⚠️ Nenhuma imagem encontrada em {pasta}")
        return

    while tentativas < MAX_TENTATIVAS and not enviado:
        try:
            tentativas += 1
            print(
                f"📤 Enviando pasta '{os.path.basename(pasta)}' para: {grupo} (Tentativa {tentativas})"
            )

            # Buscar grupo
            search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                )
            )
            search_box.clear()
            search_box.send_keys(grupo)
            time.sleep(2)
            search_box.send_keys(Keys.ENTER)

            # Aguarda o campo de mensagem abrir
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                )
            )

            # Clica no botão de anexar
            attach_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@title="Anexar"]'))
            )
            attach_btn.click()

            # Localiza o input escondido (para fotos e vídeos)
            file_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//input[@type="file" and contains(@accept,"image")]')
                )
            )

            # Envia TODAS as imagens dessa pasta em UM envio
            file_input.send_keys("\n".join(imagens))
            print(
                f"⏳ Aguardando 3 segundos para envio do lote de imagens da pasta '{os.path.basename(pasta)}'..."
            )
            time.sleep(3)  # espera carregar pré-visualizações

            # Botão enviar
            send_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@aria-label="Enviar" and @role="button"]')
                )
            )
            send_btn.click()
            print(f"✅ Pasta '{os.path.basename(pasta)}' enviada para {grupo}")

            # Mensagem separadora após 3 segundos
            time.sleep(3)
            try:
                msg_box = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    )
                )
                msg_box.send_keys(".")
                msg_box.send_keys(Keys.ENTER)
                print("✉️ Mensagem separadora enviada")
            except Exception as e:
                print(f"⚠️ Não foi possível enviar mensagem separadora: {e}")

            # Log
            with open(ARQUIVO_LOG, "a", encoding="utf-8") as log:
                log.write(
                    f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] "
                    f"Grupo: {grupo} | Pasta: {os.path.basename(pasta)} | Imagens: {', '.join(imagens)}\n"
                )

            enviado = True
            time.sleep(2)

        except Exception as e:
            print(
                f"❌ Erro ao enviar pasta {os.path.basename(pasta)} para {grupo}: {e}"
            )
            # screenshot_nome = (
            #  f"erro_{grupo}_{os.path.basename(pasta)}_{tentativas}.png".replace(
            #     " ", "_"
            # )
            # )
            # try:
            #    driver.save_screenshot(screenshot_nome)
            # except:
            #   pass

            if tentativas < MAX_TENTATIVAS:
                print(f"⏳ Tentando novamente em {TEMPO_REENVIO}s...")
                time.sleep(TEMPO_REENVIO)
            else:
                print(
                    f"⚠️ Falha definitiva ao enviar {os.path.basename(pasta)} para: {grupo}"
                )


# 📌 Loop de repetições
for r in range(1, REPETICOES + 1):
    print(f"\n🔄 Repetição {r}/{REPETICOES}")
    for grupo in GRUPOS:
        for pasta in PASTAS:
            enviar_pasta(grupo, pasta)

    if r < REPETICOES:
        print(f"⏳ Aguardando {INTERVALO}s antes da próxima repetição...")
        time.sleep(INTERVALO)

print("✅ Processo finalizado.")
