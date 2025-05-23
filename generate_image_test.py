import cv2
import numpy as np
import matplotlib.pyplot as plt

class ImageTestCases:
    """
    Gera diferentes tipos de imagens para testar a técnica de polarização.
    """
    
    def create_good_cases(self):
        """
        Cria imagens onde a polarização funciona BEM.
        """
        size = 80
        good_cases = {}
        
        # 1. BORDAS NÍTIDAS - Funciona MUITO BEM
        img1 = np.zeros((size, size), dtype=np.uint8)
        cv2.rectangle(img1, (20, 20), (60, 60), 255, -1)
        cv2.rectangle(img1, (10, 10), (30, 30), 128, -1)
        good_cases['bordas_nitidas'] = {
            'image': img1,
            'description': 'Bordas Nítidas\n(Retângulos)',
            'why_good': 'Transições abruptas criam alta polarização'
        }
        
        # 2. LINHAS DIRECIONAIS - Funciona MUITO BEM
        img2 = np.zeros((size, size), dtype=np.uint8)
        for i in range(5, size, 8):
            cv2.line(img2, (i, 0), (i, size), 255, 2)
        for i in range(5, size, 12):
            cv2.line(img2, (0, i), (size, i), 180, 1)
        good_cases['linhas_direcionais'] = {
            'image': img2,
            'description': 'Linhas Direcionais\n(Grade)',
            'why_good': 'Padrões lineares maximizam diferença 0°/90°'
        }
        
        # 3. TEXTURAS GEOMÉTRICAS - Funciona BEM
        img3 = np.zeros((size, size), dtype=np.uint8)
        for i in range(0, size, 10):
            for j in range(0, size, 10):
                if (i//10 + j//10) % 2 == 0:
                    cv2.rectangle(img3, (i, j), (i+8, j+8), 255, -1)
        good_cases['textura_geometrica'] = {
            'image': img3,
            'description': 'Textura Geométrica\n(Xadrez)',
            'why_good': 'Alternância regular cria padrões estruturados'
        }
        
        # 4. ARQUITETÔNICA - Funciona BEM
        img4 = np.ones((size, size), dtype=np.uint8) * 50
        # Janelas
        for i in range(15, size-15, 20):
            for j in range(10, size-10, 15):
                cv2.rectangle(img4, (i, j), (i+8, j+12), 200, -1)
                cv2.rectangle(img4, (i+2, j+2), (i+6, j+10), 100, -1)
        # Linhas estruturais
        cv2.line(img4, (0, size//2), (size, size//2), 150, 2)
        good_cases['arquitetonica'] = {
            'image': img4,
            'description': 'Arquitetônica\n(Prédio)',
            'why_good': 'Estruturas regulares e bordas definidas'
        }
        
        return good_cases
    
    def create_bad_cases(self):
        """
        Cria imagens onde a polarização funciona MAL.
        """
        size = 80
        bad_cases = {}
        
        # 1. GRADIENTE SUAVE - Funciona MAL
        img1 = np.zeros((size, size), dtype=np.uint8)
        for i in range(size):
            for j in range(size):
                img1[i, j] = int(255 * (i + j) / (2 * size))
        bad_cases['gradiente_suave'] = {
            'image': img1,
            'description': 'Gradiente Suave\n(Transição gradual)',
            'why_bad': 'Sem bordas abruptas, pouca diferença direcional'
        }
        
        # 2. RUÍDO ALEATÓRIO - Funciona MAL
        img2 = np.random.randint(0, 256, (size, size), dtype=np.uint8)
        # Suaviza um pouco para não ser ruído puro
        img2 = cv2.GaussianBlur(img2, (3, 3), 1)
        bad_cases['ruido_aleatorio'] = {
            'image': img2,
            'description': 'Ruído Aleatório\n(Sem estrutura)',
            'why_bad': 'Sem padrões direcionais consistentes'
        }
        
        # 3. CIRCULAR/RADIAL - Funciona MAL
        img3 = np.zeros((size, size), dtype=np.uint8)
        center = (size//2, size//2)
        for radius in range(10, size//2, 8):
            cv2.circle(img3, center, radius, 255 - radius*3, 2)
        bad_cases['circular_radial'] = {
            'image': img3,
            'description': 'Padrão Circular\n(Concêntrico)',
            'why_bad': 'Simetria radial não favorece direções específicas'
        }
        
        # 4. TEXTURA ORGÂNICA - Funciona MAL
        img4 = np.zeros((size, size), dtype=np.uint8)
        # Simula textura orgânica com blobs irregulares
        np.random.seed(42)  # Para reprodutibilidade
        for _ in range(15):
            x = np.random.randint(5, size-5)
            y = np.random.randint(5, size-5)
            radius = np.random.randint(3, 8)
            intensity = np.random.randint(100, 255)
            cv2.circle(img4, (x, y), radius, intensity, -1)
        img4 = cv2.GaussianBlur(img4, (5, 5), 2)
        bad_cases['textura_organica'] = {
            'image': img4,
            'description': 'Textura Orgânica\n(Irregular)',
            'why_bad': 'Formas irregulares sem direções preferenciais'
        }
        
        return bad_cases

def comprehensive_test():
    """
    Testa a técnica em casos bons e ruins, mostrando as diferenças.
    """
    from polarization_image_enhancement import SimplePolarizationUpscaler
    
    # Cria gerador de casos de teste
    test_cases = ImageTestCases()
    good_cases = test_cases.create_good_cases()
    bad_cases = test_cases.create_bad_cases()
    
    # Inicializa upscaler
    upscaler = SimplePolarizationUpscaler()
    
    print("=== TESTE ABRANGENTE: CASOS BONS vs RUINS ===\n")
    
    # Função para calcular métricas
    def calculate_metrics(original, enhanced, conventional):
        # Nitidez
        def sharpness(img):
            laplacian = cv2.Laplacian(img, cv2.CV_64F)
            return laplacian.var()
        
        enh_sharp = sharpness(enhanced)
        conv_sharp = sharpness(conventional)
        improvement = ((enh_sharp / conv_sharp - 1) * 100) if conv_sharp > 0 else 0
        
        return {
            'enhanced_sharpness': enh_sharp,
            'conventional_sharpness': conv_sharp,
            'improvement_percent': improvement
        }
    
    # Testa casos BONS
    print("🟢 CASOS ONDE POLARIZAÇÃO FUNCIONA BEM:")
    print("-" * 50)
    
    good_results = {}
    for name, case in good_cases.items():
        img = case['image']
        enhanced, pol_map = upscaler.polarization_upscale(img, scale=2)
        conventional = upscaler.conventional_upscale(img, scale=2)
        
        metrics = calculate_metrics(img, enhanced, conventional)
        good_results[name] = {
            'original': img,
            'enhanced': enhanced,
            'conventional': conventional,
            'pol_map': pol_map,
            'metrics': metrics,
            'description': case['description'],
            'why_good': case['why_good']
        }
        
        print(f"{case['description']}: {metrics['improvement_percent']:+.1f}% melhoria")
        print(f"  → {case['why_good']}")
    
    print("\n🔴 CASOS ONDE POLARIZAÇÃO FUNCIONA MAL:")
    print("-" * 50)
    
    bad_results = {}
    for name, case in bad_cases.items():
        img = case['image']
        enhanced, pol_map = upscaler.polarization_upscale(img, scale=2)
        conventional = upscaler.conventional_upscale(img, scale=2)
        
        metrics = calculate_metrics(img, enhanced, conventional)
        bad_results[name] = {
            'original': img,
            'enhanced': enhanced,
            'conventional': conventional,
            'pol_map': pol_map,
            'metrics': metrics,
            'description': case['description'],
            'why_bad': case['why_bad']
        }
        
        print(f"{case['description']}: {metrics['improvement_percent']:+.1f}% melhoria")
        print(f"  → {case['why_bad']}")
    
    # VISUALIZAÇÃO COMPARATIVA
    fig, axes = plt.subplots(4, 8, figsize=(20, 12))
    fig.suptitle('Comparação: Casos Bons vs Ruins para Polarização', fontsize=16, fontweight='bold')
    
    # Casos BONS (primeiras 2 linhas)
    good_items = list(good_results.items())
    for i, (name, result) in enumerate(good_items):
        row = i // 2
        
        # Original
        axes[row, i*2].imshow(result['original'], cmap='gray')
        axes[row, i*2].set_title(f"Original\n{result['description']}", fontsize=10)
        axes[row, i*2].axis('off')
        
        # Polarização
        axes[row, i*2+1].imshow(result['enhanced'], cmap='gray')
        improvement = result['metrics']['improvement_percent']
        color = 'green' if improvement > 0 else 'red'
        axes[row, i*2+1].set_title(f"Polarização\n{improvement:+.1f}%", 
                                  fontsize=10, color=color, fontweight='bold')
        axes[row, i*2+1].axis('off')
    
    # Casos RUINS (últimas 2 linhas)
    bad_items = list(bad_results.items())
    for i, (name, result) in enumerate(bad_items):
        row = i // 2 + 2
        
        # Original
        axes[row, i*2].imshow(result['original'], cmap='gray')
        axes[row, i*2].set_title(f"Original\n{result['description']}", fontsize=10)
        axes[row, i*2].axis('off')
        
        # Polarização
        axes[row, i*2+1].imshow(result['enhanced'], cmap='gray')
        improvement = result['metrics']['improvement_percent']
        color = 'green' if improvement > 0 else 'red'
        axes[row, i*2+1].set_title(f"Polarização\n{improvement:+.1f}%", 
                                  fontsize=10, color=color, fontweight='bold')
        axes[row, i*2+1].axis('off')
    
    plt.tight_layout()
    plt.show()
    
    # GRÁFICO RESUMO
    plt.figure(figsize=(12, 6))
    
    # Coleta todas as melhorias
    all_names = []
    all_improvements = []
    colors = []
    
    for name, result in good_results.items():
        all_names.append(result['description'].replace('\n', ' '))
        all_improvements.append(result['metrics']['improvement_percent'])
        colors.append('green' if result['metrics']['improvement_percent'] > 0 else 'red')
    
    for name, result in bad_results.items():
        all_names.append(result['description'].replace('\n', ' '))
        all_improvements.append(result['metrics']['improvement_percent'])
        colors.append('green' if result['metrics']['improvement_percent'] > 0 else 'red')
    
    # Gráfico de barras
    bars = plt.bar(range(len(all_names)), all_improvements, color=colors, alpha=0.7)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.xlabel('Tipo de Imagem')
    plt.ylabel('Melhoria na Nitidez (%)')
    plt.title('Performance da Técnica de Polarização por Tipo de Imagem')
    plt.xticks(range(len(all_names)), all_names, rotation=45, ha='right')
    
    # Adiciona valores nas barras
    for bar, value in zip(bars, all_improvements):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + (1 if height >= 0 else -3),
                f'{value:.1f}%', ha='center', va='bottom' if height >= 0 else 'top',
                fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # CONCLUSÕES
    print("\n" + "="*60)
    print("CONCLUSÕES PARA SUA APRESENTAÇÃO:")
    print("="*60)
    
    good_avg = np.mean([r['metrics']['improvement_percent'] for r in good_results.values()])
    bad_avg = np.mean([r['metrics']['improvement_percent'] for r in bad_results.values()])
    
    print(f"\n📊 RESULTADOS QUANTITATIVOS:")
    print(f"   • Casos favoráveis: {good_avg:+.1f}% melhoria média")
    print(f"   • Casos desfavoráveis: {bad_avg:+.1f}% melhoria média")
    
    print(f"\n✅ A TÉCNICA FUNCIONA BEM EM:")
    print("   • Imagens com bordas nítidas e bem definidas")
    print("   • Padrões geométricos regulares")
    print("   • Estruturas arquitetônicas")
    print("   • Texturas com direções preferenciais")
    
    print(f"\n❌ A TÉCNICA FUNCIONA MAL EM:")
    print("   • Gradientes suaves sem bordas abruptas")
    print("   • Ruído aleatório sem estrutura")
    print("   • Padrões circulares/radiais")
    print("   • Texturas orgânicas irregulares")
    
    print(f"\n💡 EXPLICAÇÃO TÉCNICA:")
    print("   A polarização detecta diferenças direcionais (0° vs 90°)")
    print("   Funciona bem quando há estruturas que favorecem uma direção")
    print("   Falha quando a imagem é isotrópica (igual em todas direções)")

# Teste rápido com imagens reais (se disponível)
def test_with_real_images():
    """
    Exemplo de como testar com imagens reais.
    """
    print("\n=== DICAS PARA IMAGENS REAIS ===")
    print("\n🟢 PROCURE POR:")
    print("• Fotos de prédios, arquitetura")
    print("• Imagens de grades, cercas, estruturas")
    print("• Fotografias de tecidos com padrões")
    print("• Imagens de circuitos eletrônicos")
    print("• Fotos de janelas, portões")
    
    print("\n🔴 EVITE:")
    print("• Paisagens naturais (céu, nuvens)")
    print("• Retratos de pessoas")
    print("• Imagens muito suaves ou borradas")
    print("• Fotos com muito ruído")
    print("• Imagens de água, fogo, fumaça")
    
    print("\n📝 PARA TESTAR IMAGEM REAL:")
    print("""
    # Carregue sua imagem
    img = cv2.imread('sua_imagem.jpg', cv2.IMREAD_GRAYSCALE)
    
    # Redimensione se muito grande
    if img.shape[0] > 200:
        scale = 200 / img.shape[0]
        new_width = int(img.shape[1] * scale)
        img = cv2.resize(img, (new_width, 200))
    
    # Teste a técnica
    upscaler = SimplePolarizationUpscaler()
    enhanced, pol_map = upscaler.polarization_upscale(img)
    conventional = upscaler.conventional_upscale(img)
    
    # Compare os resultados...
    """)

if __name__ == "__main__":
    comprehensive_test()
    test_with_real_images()