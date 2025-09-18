from PIL import Image, ImageDraw, ImageFont, ImageOps
from pilmoji import Pilmoji


def gerar_anuncio(
    texto,
    arquivo_saida="anuncio.png",
    largura=800,
    altura=1200,
    cor_fundo=(0, 0, 0),
    cor_texto=(255, 255, 255),
    margem=30,
    raio_borda=40,
):

    # Criar imagem base com tamanho fixo
    imagem = Image.new("RGB", (largura, altura), cor_fundo)
    draw = ImageDraw.Draw(imagem)

    # Fonte inicial grande (ajustável)
    fonte_tamanho = 80
    try:
        fonte = ImageFont.truetype("arialbd.ttf", fonte_tamanho)
    except:
        fonte = ImageFont.load_default()

    max_largura = largura - 2 * margem
    max_altura = altura - 2 * margem

    # Ajustar tamanho da fonte para caber na largura e altura
    while True:
        # Quebra de linhas
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

        # Calcular altura total do texto
        altura_texto = 0
        for linha in linhas:
            bbox = draw.textbbox((0, 0), linha, font=fonte)
            altura_texto += bbox[3] - bbox[1] + 10  # altura da linha + espaçamento

        if altura_texto <= max_altura:
            break
        else:
            # diminuir fonte e tentar de novo
            fonte_tamanho -= 2
            fonte = ImageFont.truetype("arialbd.ttf", fonte_tamanho)

    # Desenhar texto
    with Pilmoji(imagem) as pilmoji:
        y = margem
        for linha in linhas:
            pilmoji.text((margem, y), linha, font=fonte, fill=cor_texto)
            bbox = draw.textbbox((0, 0), linha, font=fonte)
            y += bbox[3] - bbox[1] + 10

    # Bordas arredondadas
    mask = Image.new("L", imagem.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([(0, 0), imagem.size], radius=raio_borda, fill=255)
    imagem.putalpha(mask)

    # Salvar PNG
    imagem.save(arquivo_saida, "PNG")
    print(f"✅ Anúncio salvo em {arquivo_saida} ({largura}x{altura}px)")


# Exemplo de uso
texto = """🚨🚨🚨🚚🚜🛬🏚
BOA TARDE SENHORES LIBERADO PARA PAGAMENTO EXCELENTE LOTE COM TRÊS UNIDADES RODOTREM DIFERENCIADO COM PREÇO ACESSÍVEL MELHOR CUSTO-BENEFÍCIO

✅ Duas unidades randon 
✅ Uma unidade noma
✅ Com pneus porém fracos 
✅ Venda de repasse estado que se encontra 
✅ Mas todos ainda estão trabalhando 
✅valor no lote 350.000.00
"""

gerar_anuncio(texto, "anuncio.png")
