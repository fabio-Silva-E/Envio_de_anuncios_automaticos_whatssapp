import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import uuid
import hashlib
import hmac
# IMPORTA OS DOIS SCRIPTS
import automatizaçãoWatts_1 as simples
import automatizaçãoWatts as legenda

SEGREDO = "081118c02c46cb775bf621d6ad8f8f0d916753abc50326aaa354e97b80d8e2c7"
import os

# 🔥 PRIMEIRO DE TUDO
def get_machine_id():
    mac = uuid.getnode()
    return hashlib.sha256(str(mac).encode()).hexdigest()




def validar_licenca(licenca):
    try:
        machine_id = get_machine_id()

        licenca_correta = hmac.new(
            SEGREDO.encode(),
            machine_id.encode(),
            hashlib.sha256
        ).hexdigest()

        return licenca == licenca_correta
    except:
        return False
def salvar_licenca(licenca):
    with open("licenca.key", "w") as f:
        f.write(f"{get_machine_id()}|{licenca}")

def pedir_licenca():
    machine_id = get_machine_id()

    # cria janela
    janela_licenca = tk.Toplevel()
    janela_licenca.title("Ativação necessária")
    janela_licenca.geometry("400x200")
    janela_licenca.resizable(False, False)

    tk.Label(
        janela_licenca,
        text="Envie este ID para liberação:",
        font=("Arial", 11)
    ).pack(pady=10)

    # campo com ID (selecionável)
    entry_id = tk.Entry(janela_licenca, justify="center", font=("Arial", 10))
    entry_id.insert(0, machine_id)
    entry_id.config(state="readonly")
    entry_id.pack(pady=5, padx=10, fill="x")

    # função copiar
    def copiar():
        janela_licenca.clipboard_clear()
        janela_licenca.clipboard_append(machine_id)
        janela_licenca.update()
        messagebox.showinfo("Copiado", "ID copiado para a área de transferência!")

    tk.Button(
        janela_licenca,
        text="📋 Copiar ID",
        command=copiar,
        bg="blue",
        fg="white"
    ).pack(pady=5)

    # campo para digitar licença
    tk.Label(janela_licenca, text="Digite sua chave:").pack(pady=5)

    entry_licenca = tk.Entry(janela_licenca)
    entry_licenca.pack(pady=5, padx=10, fill="x")

    resultado = {"ok": False}

    def validar():
        licenca = entry_licenca.get().strip()

        if not licenca:
            messagebox.showerror("Erro", "Digite a licença")
            return

        if validar_licenca(licenca):
            salvar_licenca(licenca)
            messagebox.showinfo("Sucesso", "✅ Ativado com sucesso!")
            resultado["ok"] = True
            janela_licenca.destroy()
        else:
            messagebox.showerror("Erro", "❌ Licença inválida")

    tk.Button(
        janela_licenca,
        text="✅ Ativar",
        command=validar,
        bg="green",
        fg="white"
    ).pack(pady=10)

    janela_licenca.grab_set()
    janela_licenca.wait_window()

    return resultado["ok"]

def carregar_licenca():
    if os.path.exists("licenca.key"):
        with open("licenca.key", "r") as f:
            conteudo = f.read().strip()
            try:
                machine_id, licenca = conteudo.split("|")
                if machine_id == get_machine_id():
                    return licenca
            except:
                return None
    return None

def verificar_ou_pedir_licenca():
    licenca = carregar_licenca()

    if licenca and validar_licenca(licenca):
        return True

    return pedir_licenca()


# 🚨 BLOQUEIO CORRETO
if not verificar_ou_pedir_licenca():
    exit()

def log(msg):
    def escrever():
        log_texto.insert(tk.END, msg + "\n")
        log_texto.see(tk.END)

    janela.after(0, escrever)

def iniciar_envio():
    modo = modo_envio.get()
    simples.set_log_callback(log)
    legenda.set_log_callback(log)
    def executar():
        try:
            if modo == "modo 1":
                log("🚀 Iniciando envio simples...")
                simples.iniciar()

            elif modo == "modo 2 ":
                log("🚀 Iniciando envio com legenda...")
                legenda.iniciar()

            log("✅ Finalizado!")

        except Exception as e:
            log(f"❌ Erro: {e}")

    threading.Thread(target=executar, daemon=True).start()


# ------------------------
# INTERFACE
# ------------------------
janela = tk.Tk()
janela.title("Envio WhatsApp")
janela.geometry("420x450")

tk.Label(
    janela,
    text="Selecione o modo de envio:",
    font=("Arial", 12, "bold")
).pack(pady=10)

modo_envio = tk.StringVar(value="modo 1")

dropdown = ttk.Combobox(
    janela,
    textvariable=modo_envio,
    values=["modo 1", "modo 2 (foto + legenda)"],
    state="readonly"
)
dropdown.pack(pady=10)

tk.Button(
    janela,
    text="🚀 Iniciar Envio",
    command=iniciar_envio,
    bg="green",
    fg="white",
    font=("Arial", 12, "bold"),
    width=20
).pack(pady=20)

tk.Button(
    janela,
    text="❌ Fechar",
    command=janela.destroy
).pack()

# LOG
frame = tk.Frame(janela)
frame.pack(fill="both", expand=True, padx=10, pady=10)

log_texto = tk.Text(frame, bg="black", fg="white")
log_texto.pack(side="left", fill="both", expand=True)

scroll = tk.Scrollbar(frame, command=log_texto.yview)
scroll.pack(side="right", fill="y")

log_texto.config(yscrollcommand=scroll.set)

janela.mainloop()