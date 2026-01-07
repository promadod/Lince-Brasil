import os
from PIL import Image

# --- CONFIGURAÇÕES  ---

# 1. Onde estão as fotos originais 
PASTA_ORIGEM = r'C:\fotos_brutas'

# 2. Onde vamos salvar as novas 
PASTA_DESTINO = r'C:\fotos_brutas\NOVAS'

TAMANHO_FINAL = (256, 256)
# ---------------------

def padronizar_agora():
    print(f"📂 Lendo imagens de: {PASTA_ORIGEM}")
    
    # Cria a pasta de destino se não existir
    if not os.path.exists(PASTA_DESTINO):
        os.makedirs(PASTA_DESTINO)
        print(f"📁 Pasta de destino criada: {PASTA_DESTINO}")

    arquivos = os.listdir(PASTA_ORIGEM)
    
    sucesso = 0
    for arquivo in arquivos:
        if not arquivo.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            continue

        caminho_completo = os.path.join(PASTA_ORIGEM, arquivo)
        
        try:
            # Abre e converte
            img = Image.open(caminho_completo)
            img = img.convert("RGBA")

            # Redimensiona proporcionalmente
            img.thumbnail(TAMANHO_FINAL, Image.Resampling.LANCZOS)
            
            # Cria o quadrado transparente
            background = Image.new('RGBA', TAMANHO_FINAL, (255, 255, 255, 0))
            
            # Centraliza
            largura_img, altura_img = img.size
            pos_x = (TAMANHO_FINAL[0] - largura_img) // 2
            pos_y = (TAMANHO_FINAL[1] - altura_img) // 2
            
            background.paste(img, (pos_x, pos_y), img)
            
            # Salva na pasta NOVAS
            caminho_salvar = os.path.join(PASTA_DESTINO, arquivo) 
            background.save(caminho_salvar, "PNG")
            
            print(f"✅ Pronta: {arquivo}")
            sucesso += 1

        except Exception as e:
            print(f"❌ Erro em {arquivo}: {e}")

    print(f"\n🎉 CONCLUÍDO! {sucesso} fotos salvas em: {PASTA_DESTINO}")
    print("👉 Abra a pasta 'NOVAS' dentro de 'fotos_brutas' para pegar suas imagens.")

if __name__ == "__main__":
    padronizar_agora()