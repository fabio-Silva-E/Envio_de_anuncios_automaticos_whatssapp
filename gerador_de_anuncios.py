import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
from PIL import Image, ImageDraw, ImageFont
from pilmoji import Pilmoji


# Função para gerar o anúncio
def gerar_anuncio_interface():
    texto = campo_texto.get("1.0", tk.END).strip()
    nome_arquivo = entrada_nome.get().strip()

    if not texto:
        messagebox.showwarning("Aviso", "O campo do anúncio está vazio!")
        return

    if not nome_arquivo:
        messagebox.showwarning("Aviso", "Digite o nome do arquivo!")
        return

    # Criar pasta 'anuncios' se não existir
    pasta_destino = "anuncios"
    os.makedirs(pasta_destino, exist_ok=True)

    arquivo_saida = os.path.join(pasta_destino, f"{nome_arquivo}.png")

    # 📱 Formato 9:16 (Stories / Status / Reels / TikTok)
    largura = 1080
    altura = 1920
    cor_fundo = (0, 0, 0)
    cor_texto = (255, 255, 255)
    margem = 60
    raio_borda = 50

    # Criar imagem base
    imagem = Image.new("RGB", (largura, altura), cor_fundo)
    draw = ImageDraw.Draw(imagem)

    # Fonte inicial
    fonte_tamanho = 80
    fonte_minima = 60
    try:
        fonte = ImageFont.truetype("arialbd.ttf", fonte_tamanho)
    except:
        fonte = ImageFont.load_default()

    # Ajustar largura do texto
    max_largura = largura - 2 * margem
    max_altura = altura - 2 * margem

    while True:
        linhas = []
        for linha_original in texto.split("\n"):
            palavras = linha_original.split(" ")
            linha_temp = ""
            for palavra in palavras:
                teste_linha = (linha_temp + " " + palavra).strip()
                largura_texto = draw.textlength(teste_linha, font=fonte)
                if largura_texto <= max_largura:
                    linha_temp = teste_linha
                else:
                    linhas.append(linha_temp)
                    linha_temp = palavra
            linhas.append(linha_temp)

        # Calcula altura total do texto
        altura_texto = 0
        for linha in linhas:
            bbox = draw.textbbox((0, 0), linha, font=fonte)
            altura_texto += bbox[3] - bbox[1] + 15

        if altura_texto <= max_altura and fonte_tamanho >= fonte_minima:
            break
        elif fonte_tamanho > fonte_minima:
            fonte_tamanho -= 2
            fonte = ImageFont.truetype("arialbd.ttf", fonte_tamanho)
        else:
            # aumenta altura até caber
            altura += 300
            max_altura = altura - 2 * margem
            imagem = Image.new("RGB", (largura, altura), cor_fundo)
            draw = ImageDraw.Draw(imagem)

    # Centralizar verticalmente
    y = (altura - altura_texto) // 2

    # Desenhar texto
    with Pilmoji(imagem) as pilmoji:
        for linha in linhas:
            pilmoji.text((margem, y), linha, font=fonte, fill=cor_texto)
            bbox = draw.textbbox((0, 0), linha, font=fonte)
            y += bbox[3] - bbox[1] + 15

    # Bordas arredondadas
    mask = Image.new("L", imagem.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), imagem.size], radius=raio_borda, fill=255)
    imagem.putalpha(mask)

    # Salvar PNG
    imagem.save(arquivo_saida, "PNG")
    messagebox.showinfo("Sucesso", f"✅ Anúncio salvo em {arquivo_saida}")


# ------------------ Interface Tkinter ------------------
janela = tk.Tk()
janela.title("Gerador de Anúncios PNG")
janela.geometry("600x600")

tk.Label(janela, text="Cole o anúncio abaixo:").pack(pady=5)
campo_texto = scrolledtext.ScrolledText(janela, width=70, height=20)
campo_texto.pack(pady=5)

tk.Label(janela, text="Nome do arquivo (sem extensão):").pack(pady=5)
entrada_nome = tk.Entry(janela, width=50)
entrada_nome.pack(pady=5)

tk.Button(
    janela,
    text="Gerar Anúncio PNG",
    command=gerar_anuncio_interface,
    bg="green",
    fg="white",
).pack(pady=20)

tk.Button(
    janela,
    text="⬅ Voltar",
    font=("Arial", 12),
    command=janela.destroy,
).pack(pady=20)

janela.mainloop()
