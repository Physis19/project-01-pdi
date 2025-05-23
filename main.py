import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk
import os

class SimplePolarizationUpscaler:
    """
    Implementação simples de ampliação baseada em polarização.
    Usa conceitos básicos de polarização para melhorar a interpolação.
    """
    
    def polarization_filter(self, image, angle_deg):
        """
        Aplica um filtro de polarização simples baseado no ângulo.
        """
        h, w = image.shape
        angle_rad = np.radians(angle_deg)
        
        # Cria padrão de polarização baseado no ângulo
        x = np.arange(w)
        y = np.arange(h)
        X, Y = np.meshgrid(x, y)
        
        # Padrão senoidal simples simulando polarização
        pattern = np.sin(X * np.cos(angle_rad) + Y * np.sin(angle_rad)) ** 2
        
        # Normaliza entre 0.5 e 1 para evitar zeros
        pattern = 0.5 + 0.5 * pattern
        
        return image * pattern
    
    def get_polarization_info(self, image):
        """
        Extrai informação básica de polarização usando dois filtros.
        """
        # Aplica filtros em 0° e 90°
        pol_0 = self.polarization_filter(image, 0)
        pol_90 = self.polarization_filter(image, 90)
        
        # Calcula diferença (simula S1 dos parâmetros de Stokes)
        polarization_strength = np.abs(pol_0 - pol_90)
        
        # Normaliza
        if np.max(polarization_strength) > 0:
            polarization_strength = polarization_strength / np.max(polarization_strength)
        
        return polarization_strength
    
    def polarization_upscale(self, image, scale=2):
        """
        Amplia imagem usando informação de polarização.
        """
        # Converte para cinza se necessário
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Obtém mapa de polarização
        pol_map = self.get_polarization_info(gray.astype(np.float32))
        
        # Amplia imagem original
        h, w = gray.shape
        new_size = (w * scale, h * scale)
        upscaled = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)
        
        # Amplia mapa de polarização
        pol_map_large = cv2.resize(pol_map, new_size, interpolation=cv2.INTER_CUBIC)
        
        # Aplica realce baseado na polarização
        # Áreas com alta polarização (bordas/detalhes) são realçadas
        enhancement = 1 + pol_map_large * 0.3  # 30% de realce máximo
        enhanced = upscaled.astype(np.float32) * enhancement
        
        # Garante que valores ficam no range correto
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        return enhanced, pol_map_large
    
    def conventional_upscale(self, image, scale=2):
        """
        Ampliação convencional para comparação.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        h, w = gray.shape
        new_size = (w * scale, h * scale)
        return cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)

def load_image():
    """
    Carrega uma imagem usando dialog de arquivos.
    """
    # Cria janela temporária para o diálogo
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    
    # Tipos de arquivo suportados
    filetypes = [
        ("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
        ("JPEG", "*.jpg *.jpeg"),
        ("PNG", "*.png"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff *.tif"),
        ("Todos os arquivos", "*.*")
    ]
    
    # Abre diálogo de seleção
    filename = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=filetypes
    )
    
    root.destroy()
    
    if filename:
        try:
            # Carrega a imagem
            image = cv2.imread(filename)
            if image is None:
                raise ValueError("Não foi possível carregar a imagem")
            
            # Converte BGR para RGB para matplotlib
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            print(f"✓ Imagem carregada: {os.path.basename(filename)}")
            print(f"  Dimensões: {image.shape[1]}x{image.shape[0]}")
            
            return image_rgb, filename
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar imagem:\n{str(e)}")
            return None, None
    else:
        print("Nenhuma imagem selecionada.")
        return None, None

def process_user_image():
    """
    Processa uma imagem selecionada pelo usuário.
    """
    print("=== Processamento de Imagem Personalizada ===")
    
    # Carrega imagem
    image, filename = load_image()
    if image is None:
        return
    
    # Redimensiona se muito grande (para performance)
    max_size = 800
    h, w = image.shape[:2]
    if max(h, w) > max_size:
        scale_factor = max_size / max(h, w)
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        image = cv2.resize(image, (new_w, new_h))
        print(f"  Redimensionada para: {new_w}x{new_h} (para melhor performance)")
    
    # Solicita fator de escala
    root = tk.Tk()
    root.withdraw()
    
    scale_str = tk.simpledialog.askstring(
        "Fator de Escala",
        "Digite o fator de ampliação (ex: 2, 3, 4):",
        initialvalue="2"
    )
    root.destroy()
    
    try:
        scale = max(1, min(8, int(scale_str)))  # Limita entre 1 e 8
    except:
        scale = 2
        print("Usando fator de escala padrão: 2")
    
    print(f"Processando com fator de escala: {scale}x")
    
    # Inicializa o ampliador
    upscaler = SimplePolarizationUpscaler()
    
    # Aplica ambas as técnicas
    print("Aplicando ampliação por polarização...")
    pol_result, pol_map = upscaler.polarization_upscale(image, scale=scale)
    
    print("Aplicando ampliação convencional...")
    conv_result = upscaler.conventional_upscale(image, scale=scale)
    
    # Calcula métricas
    def calculate_sharpness(img):
        """Calcula nitidez usando variância do Laplaciano"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return laplacian.var()
    
    pol_sharpness = calculate_sharpness(pol_result)
    conv_sharpness = calculate_sharpness(conv_result)
    
    print(f"\nResultados:")
    print(f"Nitidez - Polarização: {pol_sharpness:.1f}")
    print(f"Nitidez - Convencional: {conv_sharpness:.1f}")
    if conv_sharpness > 0:
        improvement = ((pol_sharpness/conv_sharpness-1)*100)
        print(f"Melhoria: {improvement:.1f}%")
    
    # Visualiza resultados
    plt.figure(figsize=(15, 10))
    
    # Imagem original
    plt.subplot(2, 3, 1)
    if len(image.shape) == 3:
        plt.imshow(image)
    else:
        plt.imshow(image, cmap='gray')
    plt.title(f'Original\n{os.path.basename(filename)}\n{image.shape[1]}x{image.shape[0]}')
    plt.axis('off')
    
    # Mapa de polarização
    plt.subplot(2, 3, 2)
    plt.imshow(pol_map, cmap='viridis')
    plt.title('Mapa de Polarização\n(Força da Polarização)')
    plt.axis('off')
    plt.colorbar(shrink=0.7)
    
    # Ampliação convencional
    plt.subplot(2, 3, 3)
    if len(conv_result.shape) == 3:
        plt.imshow(conv_result)
    else:
        plt.imshow(conv_result, cmap='gray')
    plt.title(f'Convencional ({scale}x)\nNitidez: {conv_sharpness:.0f}')
    plt.axis('off')
    
    # Ampliação por polarização
    plt.subplot(2, 3, 4)
    if len(pol_result.shape) == 3:
        plt.imshow(pol_result)
    else:
        plt.imshow(pol_result, cmap='gray')
    plt.title(f'Polarização ({scale}x)\nNitidez: {pol_sharpness:.0f}')
    plt.axis('off')
    
    # Diferença
    if len(pol_result.shape) == 3 and len(conv_result.shape) == 3:
        diff = np.mean(np.abs(pol_result.astype(float) - conv_result.astype(float)), axis=2)
    else:
        diff = np.abs(pol_result.astype(float) - conv_result.astype(float))
    
    plt.subplot(2, 3, 5)
    plt.imshow(diff, cmap='hot')
    plt.title('Diferença\n(Vermelho = Maior diferença)')
    plt.axis('off')
    plt.colorbar(shrink=0.7)
    
    # Gráfico de comparação
    plt.subplot(2, 3, 6)
    methods = ['Convencional', 'Polarização']
    sharpness_values = [conv_sharpness, pol_sharpness]
    colors = ['blue', 'red']
    
    bars = plt.bar(methods, sharpness_values, color=colors, alpha=0.7)
    plt.title('Comparação de Nitidez')
    plt.ylabel('Nitidez (Variância Laplaciano)')
    
    # Adiciona valores nas barras
    for bar, value in zip(bars, sharpness_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(sharpness_values)*0.02,
                f'{value:.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()
    
    # Pergunta se quer salvar
    save_results = messagebox.askyesno(
        "Salvar Resultados", 
        "Deseja salvar as imagens processadas?"
    )
    
    if save_results:
        save_processed_images(image, pol_result, conv_result, filename, scale)

def save_processed_images(original, polarization_result, conventional_result, original_filename, scale):
    """
    Salva as imagens processadas.
    """
    try:
        # Diretório de saída
        base_dir = os.path.dirname(original_filename)
        base_name = os.path.splitext(os.path.basename(original_filename))[0]
        
        # Converte RGB para BGR para salvar com cv2
        if len(polarization_result.shape) == 3:
            pol_bgr = cv2.cvtColor(polarization_result, cv2.COLOR_RGB2BGR)
        else:
            pol_bgr = polarization_result
            
        if len(conventional_result.shape) == 3:
            conv_bgr = cv2.cvtColor(conventional_result, cv2.COLOR_RGB2BGR)
        else:
            conv_bgr = conventional_result
        
        # Nomes dos arquivos
        pol_filename = os.path.join(base_dir, f"{base_name}_polarization_{scale}x.png")
        conv_filename = os.path.join(base_dir, f"{base_name}_conventional_{scale}x.png")
        
        # Salva
        cv2.imwrite(pol_filename, pol_bgr)
        cv2.imwrite(conv_filename, conv_bgr)
        
        print(f"✓ Imagens salvas:")
        print(f"  Polarização: {pol_filename}")
        print(f"  Convencional: {conv_filename}")
        
        messagebox.showinfo(
            "Sucesso", 
            f"Imagens salvas com sucesso!\n\n"
            f"Polarização: {os.path.basename(pol_filename)}\n"
            f"Convencional: {os.path.basename(conv_filename)}"
        )
        
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        messagebox.showerror("Erro", f"Erro ao salvar imagens:\n{str(e)}")

def create_test_images():
    """
    Cria diferentes tipos de imagens de teste para demonstrar a técnica.
    """
    size = 120
    images = {}
    
    # 1. Imagem com linhas e padrões geométricos (original)
    img1 = np.zeros((size, size), dtype=np.uint8)
    for i in range(10, size, 20):
        cv2.line(img1, (i, 0), (i, size), 255, 2)
    for i in range(10, size, 25):
        cv2.line(img1, (0, i), (size, i), 180, 2)
    cv2.circle(img1, (30, 30), 10, 200, -1)
    cv2.circle(img1, (70, 70), 8, 150, -1)
    images['Linhas e Círculos'] = img1
    
    # 2. Textura de xadrez
    img2 = np.zeros((size, size), dtype=np.uint8)
    square_size = 8
    for i in range(0, size, square_size):
        for j in range(0, size, square_size):
            if (i // square_size + j // square_size) % 2 == 0:
                img2[i:i+square_size, j:j+square_size] = 255
    images['Xadrez'] = img2
    
    # 3. Bordas e cantos
    img3 = np.zeros((size, size), dtype=np.uint8)
    cv2.rectangle(img3, (20, 20), (100, 100), 255, 3)
    cv2.rectangle(img3, (40, 40), (80, 80), 128, 2)
    # Adiciona alguns cantos internos
    cv2.line(img3, (60, 20), (60, 40), 200, 2)
    cv2.line(img3, (40, 60), (60, 60), 200, 2)
    cv2.line(img3, (80, 60), (100, 60), 200, 2)
    cv2.line(img3, (80, 40), (80, 60), 200, 2)
    images['Bordas e Cantos'] = img3
    
    # 4. Padrão radial
    img4 = np.zeros((size, size), dtype=np.uint8)
    center = (size//2, size//2)
    for angle in range(0, 360, 15):
        x1 = int(center[0] + 40 * np.cos(np.radians(angle)))
        y1 = int(center[1] + 40 * np.sin(np.radians(angle)))
        cv2.line(img4, center, (x1, y1), 255, 2)
    cv2.circle(img4, center, 20, 128, 2)
    cv2.circle(img4, center, 5, 255, -1)
    images['Padrão Radial'] = img4
    
    # 5. Texto simulado
    img5 = np.zeros((size, size), dtype=np.uint8)
    # Simula linhas de texto
    for y in [25, 40, 55, 70, 85]:
        # Linha principal
        cv2.line(img5, (10, y), (110, y), 255, 1)
        # Alguns "caracteres" simulados
        for x in [15, 25, 35, 50, 60, 70, 85, 95]:
            if np.random.random() > 0.3:  # Adiciona variação
                cv2.line(img5, (x, y-3), (x, y+3), 200, 1)
    images['Texto Simulado'] = img5
    
    # 6. Padrão diagonal
    img6 = np.zeros((size, size), dtype=np.uint8)
    for i in range(-size, size, 10):
        cv2.line(img6, (0, i), (size, i + size), 255, 1)
        cv2.line(img6, (i, 0), (i + size, size), 180, 1)
    # Adiciona alguns elementos
    cv2.circle(img6, (30, 90), 12, 200, 2)
    cv2.rectangle(img6, (70, 20), (100, 50), 220, -1)
    images['Padrão Diagonal'] = img6
    
    # 7. Formas orgânicas (curvas)
    img7 = np.zeros((size, size), dtype=np.uint8)
    # Desenha algumas curvas usando pontos
    points1 = [(20, 60), (40, 30), (60, 40), (80, 20), (100, 50)]
    points2 = [(20, 80), (50, 100), (80, 90), (100, 70)]
    
    for i in range(len(points1)-1):
        cv2.line(img7, points1[i], points1[i+1], 255, 3)
    for i in range(len(points2)-1):
        cv2.line(img7, points2[i], points2[i+1], 200, 2)
    
    # Adiciona algumas elipses
    cv2.ellipse(img7, (40, 70), (15, 8), 45, 0, 360, 180, 2)
    cv2.ellipse(img7, (80, 40), (12, 20), -30, 0, 360, 150, 2)
    images['Curvas Orgânicas'] = img7
    
    # 8. Ruído estruturado
    img8 = np.zeros((size, size), dtype=np.uint8)
    # Base com gradiente
    for i in range(size):
        for j in range(size):
            img8[i, j] = int(100 + 50 * np.sin(i/10) * np.cos(j/8))
    
    # Adiciona elementos estruturais sobre o gradiente
    cv2.rectangle(img8, (30, 30), (90, 90), 255, 2)
    cv2.line(img8, (0, 60), (size, 60), 200, 1)
    cv2.line(img8, (60, 0), (60, size), 200, 1)
    images['Gradiente + Estrutura'] = img8
    
    return images

def demo_multiple_test_images():
    """
    Demonstração com múltiplas imagens de teste - uma por vez.
    """
    print("=== Demonstração com Múltiplas Imagens de Teste ===")
    print("Cada imagem será mostrada individualmente. Feche a janela para ver a próxima.")
    
    # Cria imagens de teste
    test_images = create_test_images()
    upscaler = SimplePolarizationUpscaler()
    
    # Processa e exibe cada imagem individualmente
    results = {}
    total_images = len(test_images)
    
    for idx, (name, img) in enumerate(test_images.items(), 1):
        print(f"\nProcessando {idx}/{total_images}: {name}...")
        
        # Processa a imagem
        pol_result, pol_map = upscaler.polarization_upscale(img, scale=2)
        conv_result = upscaler.conventional_upscale(img, scale=2)
        
        # Calcula métricas
        def calculate_sharpness(image):
            laplacian = cv2.Laplacian(image, cv2.CV_64F)
            return laplacian.var()
        
        pol_sharpness = calculate_sharpness(pol_result)
        conv_sharpness = calculate_sharpness(conv_result)
        improvement = ((pol_sharpness/conv_sharpness-1)*100) if conv_sharpness > 0 else 0
        
        # Armazena resultados para o resumo final
        results[name] = {
            'pol_sharpness': pol_sharpness,
            'conv_sharpness': conv_sharpness,
            'improvement': improvement
        }
        
        # Exibe a comparação individual
        plt.figure(figsize=(15, 10))
        plt.suptitle(f'Comparação {idx}/{total_images}: {name}', fontsize=16, fontweight='bold')
        
        # Imagem original
        plt.subplot(2, 4, 1)
        plt.imshow(img, cmap='gray')
        plt.title(f'Original\n{img.shape[1]}x{img.shape[0]}', fontsize=12)
        plt.axis('off')
        
        # Zoom da região central (original)
        center_y, center_x = img.shape[0]//2, img.shape[1]//2
        crop_size = min(40, img.shape[0]//3)
        zoom_orig = img[center_y-crop_size:center_y+crop_size, 
                        center_x-crop_size:center_x+crop_size]
        plt.subplot(2, 4, 2)
        plt.imshow(zoom_orig, cmap='gray')
        plt.title('Zoom Original', fontsize=12)
        plt.axis('off')
        
        # Mapa de polarização
        plt.subplot(2, 4, 3)
        im = plt.imshow(pol_map, cmap='viridis')
        plt.title('Mapa de Polarização\n(Força)', fontsize=12)
        plt.axis('off')
        plt.colorbar(im, shrink=0.8)
        
        # Diferença entre métodos
        diff = np.abs(pol_result.astype(float) - conv_result.astype(float))
        plt.subplot(2, 4, 4)
        plt.imshow(diff, cmap='hot')
        plt.title('Diferença\n(Vermelho = Maior)', fontsize=12)
        plt.axis('off')
        plt.colorbar(shrink=0.8)
        
        # Resultado convencional
        plt.subplot(2, 4, 5)
        plt.imshow(conv_result, cmap='gray')
        plt.title(f'Convencional (2x)\nNitidez: {conv_sharpness:.0f}', fontsize=12)
        plt.axis('off')
        
        # Zoom convencional
        zoom_conv = conv_result[center_y*2-crop_size:center_y*2+crop_size, 
                              center_x*2-crop_size:center_x*2+crop_size]
        plt.subplot(2, 4, 6)
        plt.imshow(zoom_conv, cmap='gray')
        plt.title('Zoom Convencional', fontsize=12)
        plt.axis('off')
        
        # Resultado com polarização
        plt.subplot(2, 4, 7)
        plt.imshow(pol_result, cmap='gray')
        improvement_text = f'{improvement:+.1f}%' if abs(improvement) > 0.1 else '0%'
        plt.title(f'Polarização (2x)\nNitidez: {pol_sharpness:.0f}\n({improvement_text})', fontsize=12)
        plt.axis('off')
        
        # Zoom polarização
        zoom_pol = pol_result[center_y*2-crop_size:center_y*2+crop_size, 
                             center_x*2-crop_size:center_x*2+crop_size]
        plt.subplot(2, 4, 8)
        plt.imshow(zoom_pol, cmap='gray')
        plt.title('Zoom Polarização', fontsize=12)
        plt.axis('off')
        
        plt.tight_layout()
        
        # Adiciona informações na parte inferior
        info_text = f"Tipo: {name} | Melhoria: {improvement_text} | "
        if improvement > 5:
            info_text += "✓ Polarização melhor"
        elif improvement < -5:
            info_text += "→ Convencional melhor"
        else:
            info_text += "≈ Resultados similares"
            
        plt.figtext(0.5, 0.02, info_text, ha='center', fontsize=11, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        print(f"Mostrando comparação para: {name}")
        print(f"  Nitidez Convencional: {conv_sharpness:.1f}")
        print(f"  Nitidez Polarização: {pol_sharpness:.1f}")
        print(f"  Melhoria: {improvement:+.1f}%")
        
        # Mostra a janela e aguarda o usuário fechar
        plt.show()
        
        print(f"✓ Imagem {idx}/{total_images} concluída.")
    
    # Resumo final de todos os resultados
    print("\n" + "="*60)
    print("                    RESUMO FINAL")
    print("="*60)
    print(f"{'Tipo de Imagem':<20} {'Conv.':<8} {'Polar.':<8} {'Melhoria':<10} {'Status':<15}")
    print("-" * 65)
    
    total_improvements = []
    best_types = []
    worst_types = []
    
    for name, data in results.items():
        improvement = data['improvement']
        improvement_text = f"{improvement:+.1f}%" if abs(improvement) > 0.1 else "0%"
        
        # Determina status
        if improvement > 5:
            status = "✓ Polarização"
            best_types.append((name, improvement))
        elif improvement < -5:
            status = "→ Convencional"
            worst_types.append((name, improvement))
        else:
            status = "≈ Similar"
        
        print(f"{name:<20} {data['conv_sharpness']:<8.0f} {data['pol_sharpness']:<8.0f} {improvement_text:<10} {status:<15}")
        
        if abs(improvement) > 0.1:
            total_improvements.append(improvement)
    
    # Estatísticas gerais
    if total_improvements:
        avg_improvement = np.mean(total_improvements)
        print(f"\nMelhoria média geral: {avg_improvement:+.1f}%")
    
    # Melhores casos
    if best_types:
        print(f"\n🏆 Polarização funciona MELHOR em:")
        for name, improvement in sorted(best_types, key=lambda x: x[1], reverse=True):
            print(f"   • {name}: {improvement:+.1f}%")
    
    # Piores casos
    if worst_types:
        print(f"\n⚠️  Convencional funciona MELHOR em:")
        for name, improvement in sorted(worst_types, key=lambda x: x[1]):
            print(f"   • {name}: {improvement:+.1f}%")
    
    # Conclusões
    print(f"\n💡 CONCLUSÕES:")
    print("   A técnica de polarização é mais eficaz em imagens com:")
    print("   • Bordas bem definidas e contrastes altos")
    print("   • Padrões direcionais e geométricos regulares")
    print("   • Estruturas lineares (linhas, retângulos)")
    print("   • Texturas organizadas (xadrez, grades)")
    print(f"\n   Funciona menos bem em:")
    print("   • Formas muito orgânicas e curvilíneas")
    print("   • Imagens com gradientes suaves")
    print("   • Padrões muito complexos ou aleatórios")
    
    print(f"\n{'='*60}")
    print("Demonstração completa! Todas as {0} imagens foram analisadas.".format(len(test_images)))

def demo_simple_polarization():
    """
    Demonstração simples da técnica com uma imagem específica.
    """
    print("=== Demonstração Simples (Imagem Individual) ===")
    
    # Usa a primeira imagem de teste como exemplo
    test_images = create_test_images()
    test_img = test_images['Linhas e Círculos']
    size = test_img.shape[0]
    
    upscaler = SimplePolarizationUpscaler()
    pol_result, pol_map = upscaler.polarization_upscale(test_img, scale=2)
    conv_result = upscaler.conventional_upscale(test_img, scale=2)
    
    # Visualização (mesmo código da versão original)
    def calculate_sharpness(img):
        laplacian = cv2.Laplacian(img, cv2.CV_64F)
        return laplacian.var()
    
    pol_sharpness = calculate_sharpness(pol_result)
    conv_sharpness = calculate_sharpness(conv_result)
    
    print(f"Nitidez - Polarização: {pol_sharpness:.1f}")
    print(f"Nitidez - Convencional: {conv_sharpness:.1f}")
    print(f"Melhoria: {((pol_sharpness/conv_sharpness-1)*100):.1f}%")
    
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 3, 1)
    plt.imshow(test_img, cmap='gray')
    plt.title(f'Original\n({size}x{size})')
    plt.axis('off')
    
    plt.subplot(2, 3, 2)
    plt.imshow(pol_map, cmap='viridis')
    plt.title('Mapa de Polarização')
    plt.axis('off')
    plt.colorbar(shrink=0.7)
    
    plt.subplot(2, 3, 3)
    plt.imshow(conv_result, cmap='gray')
    plt.title(f'Convencional\nNitidez: {conv_sharpness:.0f}')
    plt.axis('off')
    
    plt.subplot(2, 3, 4)
    plt.imshow(pol_result, cmap='gray')
    plt.title(f'Polarização\nNitidez: {pol_sharpness:.0f}')
    plt.axis('off')
    
    diff = np.abs(pol_result.astype(float) - conv_result.astype(float))
    plt.subplot(2, 3, 5)
    plt.imshow(diff, cmap='hot')
    plt.title('Diferença')
    plt.axis('off')
    plt.colorbar(shrink=0.7)
    
    plt.subplot(2, 3, 6)
    methods = ['Convencional', 'Polarização']
    sharpness_values = [conv_sharpness, pol_sharpness]
    colors = ['blue', 'red']
    
    bars = plt.bar(methods, sharpness_values, color=colors, alpha=0.7)
    plt.title('Comparação de Nitidez')
    plt.ylabel('Nitidez (Variância Laplaciano)')
    
    for bar, value in zip(bars, sharpness_values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{value:.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.show()

def choose_test_image():
    """
    Permite ao usuário escolher uma imagem de teste específica.
    """
    print("=== Demonstração com Imagem de Teste Específica ===")
    
    test_images = create_test_images()
    image_names = list(test_images.keys())
    
    print("\nImagens de teste disponíveis:")
    for i, name in enumerate(image_names, 1):
        print(f"{i}. {name}")
    
    while True:
        try:
            choice = input(f"\nEscolha uma imagem (1-{len(image_names)}): ").strip()
            choice_idx = int(choice) - 1
            
            if 0 <= choice_idx < len(image_names):
                selected_name = image_names[choice_idx]
                selected_img = test_images[selected_name]
                
                print(f"\nProcessando: {selected_name}")
                
                # Processa a imagem selecionada
                upscaler = SimplePolarizationUpscaler()
                pol_result, pol_map = upscaler.polarization_upscale(selected_img, scale=2)
                conv_result = upscaler.conventional_upscale(selected_img, scale=2)
                
                # Calcula métricas
                def calculate_sharpness(img):
                    laplacian = cv2.Laplacian(img, cv2.CV_64F)
                    return laplacian.var()
                
                pol_sharpness = calculate_sharpness(pol_result)
                conv_sharpness = calculate_sharpness(conv_result)
                improvement = ((pol_sharpness/conv_sharpness-1)*100) if conv_sharpness > 0 else 0
                
                print(f"Nitidez - Polarização: {pol_sharpness:.1f}")
                print(f"Nitidez - Convencional: {conv_sharpness:.1f}")
                print(f"Melhoria: {improvement:+.1f}%")
                
                # Visualiza resultado
                plt.figure(figsize=(12, 8))
                
                plt.subplot(2, 3, 1)
                plt.imshow(selected_img, cmap='gray')
                plt.title(f'Original: {selected_name}\n({selected_img.shape[1]}x{selected_img.shape[0]})')
                plt.axis('off')
                
                plt.subplot(2, 3, 2)
                plt.imshow(pol_map, cmap='viridis')
                plt.title('Mapa de Polarização')
                plt.axis('off')
                plt.colorbar(shrink=0.7)
                
                plt.subplot(2, 3, 3)
                plt.imshow(conv_result, cmap='gray')
                plt.title(f'Convencional\nNitidez: {conv_sharpness:.0f}')
                plt.axis('off')
                
                plt.subplot(2, 3, 4)
                plt.imshow(pol_result, cmap='gray')
                plt.title(f'Polarização\nNitidez: {pol_sharpness:.0f}')
                plt.axis('off')
                
                diff = np.abs(pol_result.astype(float) - conv_result.astype(float))
                plt.subplot(2, 3, 5)
                plt.imshow(diff, cmap='hot')
                plt.title('Diferença')
                plt.axis('off')
                plt.colorbar(shrink=0.7)
                
                plt.subplot(2, 3, 6)
                methods = ['Convencional', 'Polarização']
                sharpness_values = [conv_sharpness, pol_sharpness]
                colors = ['blue', 'red']
                
                bars = plt.bar(methods, sharpness_values, color=colors, alpha=0.7)
                plt.title('Comparação de Nitidez')
                plt.ylabel('Nitidez (Variância Laplaciano)')
                
                for bar, value in zip(bars, sharpness_values):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(sharpness_values)*0.02,
                            f'{value:.0f}', ha='center', va='bottom')
                
                plt.tight_layout()
                plt.show()
                break
                
            else:
                print("Opção inválida. Tente novamente.")
                
        except ValueError:
            print("Digite um número válido.")
        except KeyboardInterrupt:
            print("\nCancelado.")
            break

def main_menu():
    """
    Menu principal interativo.
    """
    print("\n" + "="*50)
    print("  POLARIZATION UPSCALER")
    print("  Ampliação de Imagens com Polarização")
    print("="*50)
    print("\nEscolha uma opção:")
    print("1. Processar sua própria imagem")
    print("2. Demonstração com imagem de teste específica")
    print("3. Comparação com todas as imagens de teste")
    print("4. Demonstração simples (imagem padrão)")
    print("5. Sair")
    
    while True:
        try:
            choice = input("\nDigite sua escolha (1-5): ").strip()
            
            if choice == '1':
                process_user_image()
                break
            elif choice == '2':
                choose_test_image()
                break
            elif choice == '3':
                demo_multiple_test_images()
                break
            elif choice == '4':
                demo_simple_polarization()
                break
            elif choice == '5':
                print("Saindo...")
                break
            else:
                print("Opção inválida. Digite 1, 2, 3, 4 ou 5.")
                
        except KeyboardInterrupt:
            print("\nSaindo...")
            break
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    # Verifica se tkinter está disponível
    try:
        import tkinter.simpledialog
        main_menu()
    except ImportError:
        print("Aviso: tkinter não disponível. Executando apenas demonstração.")
        demo_simple_polarization()