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

PASTA_BASE = os.path.join(os.getcwd(), "imgs")
PASTAS = [
    os.path.join(PASTA_BASE, p)
    for p in os.listdir(PASTA_BASE)
    if os.path.isdir(os.path.join(PASTA_BASE, p))
]

if not PASTAS:
    print("⚠️ Nenhuma pasta encontrada dentro de 'imgs'.")
    exit(1)

# ------------------------
# Leitura dos grupos a partir de um único arquivo
# ------------------------


def ler_grupos_de_arquivo(nome_arquivo="grupos.txt"):
    caminho = os.path.join(os.getcwd(), nome_arquivo)
    if not os.path.exists(caminho):
        print(
            f"⚠️ Arquivo '{nome_arquivo}' não encontrado. Crie-o na mesma pasta do script."
        )
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        grupos = [linha.strip() for linha in f.readlines() if linha.strip()]
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
print("📌 Escaneie o QR Code do WhatsApp (se necessário)...")
time.sleep(TEMPO_ESPERA)


# ------------------------
# Função para enviar uma pasta para um grupo
# ------------------------
def enviar_pasta_para_grupo(grupo, pasta):
    tentativas = 0
    enviado = False
    imagens = [
        os.path.abspath(os.path.join(pasta, arquivo))
        for arquivo in os.listdir(pasta)
        if arquivo.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ]

    if not imagens:
        msg = f"⚠️ Nenhuma imagem encontrada em {pasta}"
        print(msg)
        with open(ARQUIVO_ERROS, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {msg}\n")
        return

    while tentativas < MAX_TENTATIVAS and not enviado:
        try:
            tentativas += 1
            print(
                f"📤 Enviando pasta '{os.path.basename(pasta)}' para: {grupo} (Tentativa {tentativas})"
            )

            # Buscar grupo
            search_box = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                )
            )
            search_box.clear()
            time.sleep(0.5)
            search_box.send_keys(grupo)
            time.sleep(2)
            try:
                # Clicar no grupo encontrado
                grupo_result = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f'//span[starts-with(@title, "{grupo}")]')
                    )
                )
                grupo_result.click()
            except:
                print(f"⚠️ Grupo '{grupo}' não encontrado, pulando para o próximo...")
                search_box = WebDriverWait(driver, TEMPO_ESPERA).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                    )
                )
                search_box.clear()
                time.sleep(1)
                return

            # Verifica se o grupo abriu corretamente
            WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//header//span[@dir="auto"]')
                )
            )

            # Campo de mensagem
            WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                )
            )

            # Botão anexar
            attach_btn = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, 'span[data-icon="plus-rounded"]')
                )
            )
            attach_btn.click()

            # Input de arquivo
            file_input = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//input[@type="file" and contains(@accept,"image")]')
                )
            )
            file_input.send_keys("\n".join(imagens))
            time.sleep(3)

            # Botão enviar
            send_btn = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//div[@aria-label="Enviar" and @role="button"]')
                )
            )
            send_btn.click()
            print(f"✅ Pasta '{os.path.basename(pasta)}' enviada para {grupo}")

            # Aguarda mais tempo para garantir que todas as imagens subam
            print(f"⏳ Aguardando {TEMPO_ENVIO_IMAGENS}s para concluir upload...")
            time.sleep(TEMPO_ENVIO_IMAGENS)

            # Envia ponto separador
            msg_box = WebDriverWait(driver, TEMPO_ESPERA).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                )
            )
            msg_box.send_keys(".")
            msg_box.send_keys(Keys.ENTER)

            # Log
            with open(ARQUIVO_LOG, "a", encoding="utf-8") as log:
                log.write(
                    f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] ✅ Grupo: {grupo} | Pasta: {os.path.basename(pasta)} | Imagens: {len(imagens)}\n"
                )

            enviado = True

        except Exception as e:
            erro_msg = (
                f"❌ Erro ao enviar pasta '{os.path.basename(pasta)}' para {grupo}: {e}"
            )
            print(erro_msg)
            with open(ARQUIVO_ERROS, "a", encoding="utf-8") as log:
                log.write(
                    f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] {erro_msg}\n"
                )
                log.write(traceback.format_exc())
                log.write("\n" + "-" * 80 + "\n")

            if tentativas < MAX_TENTATIVAS:
                print(f"⏳ Tentando novamente em {TEMPO_REENVIO}s...")
                time.sleep(TEMPO_REENVIO)
            else:
                print(
                    f"⚠️ Falha definitiva ao enviar pasta '{os.path.basename(pasta)}' para: {grupo}"
                )


def enviar_para_todos_grupos():
    if not grupos:
        messagebox.showwarning(
            "Aviso", "Nenhum grupo encontrado no arquivo 'grupos.txt'."
        )
        return

    for r in range(1, REPETICOES + 1):
        print(f"\n🔄 Repetição {r}/{REPETICOES}")
        for idx_pasta, pasta in enumerate(PASTAS):
            print(
                f"\n📂 Enviando pasta {os.path.basename(pasta)} ({idx_pasta+1}/{len(PASTAS)})"
            )
            for grupo in grupos:
                enviar_pasta_para_grupo(grupo, pasta)
        if r < REPETICOES:
            print(f"⏳ Aguardando {INTERVALO}s antes da próxima repetição...")
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
            for idx_pasta, pasta in enumerate(PASTAS):
                print(
                    f"\n📂 Enviando pasta {os.path.basename(pasta)} ({idx_pasta+1}/{len(PASTAS)})"
                )
                for grupo in grupos_selecionados:
                    enviar_pasta_para_grupo(grupo, pasta)
            if r < REPETICOES:
                print(f"⏳ Aguardando {INTERVALO}s antes da próxima repetição...")
                time.sleep(INTERVALO)
        messagebox.showinfo("Concluído", "Envio finalizado!")

    threading.Thread(target=enviar_thread, daemon=True).start()


# ------------------------
# ------------------------
# Interface Tkinter (simplificada)
# ------------------------
janela = tk.Tk()
janela.title("Envio Automático WhatsApp")
janela.geometry("400x250")

tk.Label(
    janela,
    text="📋 Grupos carregados a partir de 'grupos.txt'\nClique abaixo para iniciar o envio:",
    font=("Arial", 11),
    justify="center",
).pack(pady=20)

tk.Button(
    janela,
    text="🚀 Iniciar Envio",
    command=lambda: threading.Thread(
        target=lambda: enviar_para_todos_grupos(), daemon=True
    ).start(),
    bg="green",
    fg="white",
    font=("Arial", 12, "bold"),
    width=20,
).pack(pady=20)

tk.Button(
    janela,
    text="⬅ Fechar",
    font=("Arial", 11),
    command=janela.destroy,
).pack(pady=5)

janela.mainloop()
