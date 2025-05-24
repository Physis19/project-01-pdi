import cv2
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog, messagebox
import tkinter as tk
import os

class SimplePolarizationUpscaler:
    def polarization_filter(self, image, angle_deg):
        h, w = image.shape
        angle_rad = np.radians(angle_deg)
        
        x = np.arange(w)
        y = np.arange(h)
        X, Y = np.meshgrid(x, y)
        
        pattern = np.sin(X * np.cos(angle_rad) + Y * np.sin(angle_rad)) ** 2
        
        pattern = 0.5 + 0.5 * pattern
        
        return image * pattern
    
    def get_polarization_info(self, image):
        pol_0 = self.polarization_filter(image, 0)
        pol_90 = self.polarization_filter(image, 90)
        
        polarization_strength = np.abs(pol_0 - pol_90)
        
        if np.max(polarization_strength) > 0:
            polarization_strength = polarization_strength / np.max(polarization_strength)
        
        return polarization_strength
    
    def polarization_upscale(self, image, scale=2):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        pol_map = self.get_polarization_info(gray.astype(np.float32))
        
        h, w = gray.shape
        new_size = (w * scale, h * scale)
        upscaled = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)
        
        pol_map_large = cv2.resize(pol_map, new_size, interpolation=cv2.INTER_CUBIC)
        
        enhancement = 1 + pol_map_large * 0.3
        enhanced = upscaled.astype(np.float32) * enhancement
        
        enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        return enhanced
    
    def conventional_upscale(self, image, scale=2):
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        h, w = gray.shape
        new_size = (w * scale, h * scale)
        return cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)

def load_image():
    root = tk.Tk()
    root.withdraw()
    
    filetypes = [
        ("Imagens", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
        ("JPEG", "*.jpg *.jpeg"),
        ("PNG", "*.png"),
        ("BMP", "*.bmp"),
        ("TIFF", "*.tiff *.tif"),
        ("Todos os arquivos", "*.*")
    ]
    
    filename = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=filetypes
    )
    
    root.destroy()
    
    if filename:
        try:
            image = cv2.imread(filename)
            if image is None:
                raise ValueError("Não foi possível carregar a imagem")
            
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
    print("=== Processamento de Imagem Personalizada ===")
   
    image, filename = load_image()
    if image is None:
        return
    
    max_size = 800
    h, w = image.shape[:2]
    if max(h, w) > max_size:
        scale_factor = max_size / max(h, w)
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        image = cv2.resize(image, (new_w, new_h))
        print(f"  Redimensionada para: {new_w}x{new_h} (para melhor performance)")
    
    root = tk.Tk()
    root.withdraw()
    
    scale_str = tk.simpledialog.askstring(
        "Fator de Escala",
        "Digite o fator de ampliação (ex: 2, 3, 4):",
        initialvalue="2"
    )
    root.destroy()
    
    try:
        scale = max(1, min(8, int(scale_str)))
    except:
        scale = 2
        print("Usando fator de escala padrão: 2")
    
    print(f"Processando com fator de escala: {scale}x")
    
    upscaler = SimplePolarizationUpscaler()
    pol_result = upscaler.polarization_upscale(image, scale=scale)
    conv_result = upscaler.conventional_upscale(image, scale=scale)
    
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    if len(image.shape) == 3:
        plt.imshow(image)
    else:
        plt.imshow(image, cmap='gray')
    plt.title(f'Original\n{os.path.basename(filename)}\n{image.shape[1]}x{image.shape[0]}')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.imshow(conv_result, cmap='gray')
    plt.title(f'Convencional ({scale}x)')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.imshow(pol_result, cmap='gray')
    plt.title(f'Polarização ({scale}x)')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def create_test_images():
    size = 120
    images = {}
    
    img1 = np.zeros((size, size), dtype=np.uint8)
    for i in range(10, size, 20):
        cv2.line(img1, (i, 0), (i, size), 255, 2)
    for i in range(10, size, 25):
        cv2.line(img1, (0, i), (size, i), 180, 2)
    cv2.circle(img1, (30, 30), 10, 200, -1)
    cv2.circle(img1, (70, 70), 8, 150, -1)
    images['Linhas e Círculos'] = img1
    
    img2 = np.zeros((size, size), dtype=np.uint8)
    square_size = 8
    for i in range(0, size, square_size):
        for j in range(0, size, square_size):
            if (i // square_size + j // square_size) % 2 == 0:
                img2[i:i+square_size, j:j+square_size] = 255
    images['Xadrez'] = img2
    
    img3 = np.zeros((size, size), dtype=np.uint8)
    cv2.rectangle(img3, (20, 20), (100, 100), 255, 3)
    cv2.rectangle(img3, (40, 40), (80, 80), 128, 2)
    cv2.line(img3, (60, 20), (60, 40), 200, 2)
    cv2.line(img3, (40, 60), (60, 60), 200, 2)
    cv2.line(img3, (80, 60), (100, 60), 200, 2)
    cv2.line(img3, (80, 40), (80, 60), 200, 2)
    images['Bordas e Cantos'] = img3
    
    img4 = np.zeros((size, size), dtype=np.uint8)
    center = (size//2, size//2)
    for angle in range(0, 360, 15):
        x1 = int(center[0] + 40 * np.cos(np.radians(angle)))
        y1 = int(center[1] + 40 * np.sin(np.radians(angle)))
        cv2.line(img4, center, (x1, y1), 255, 2)
    cv2.circle(img4, center, 20, 128, 2)
    cv2.circle(img4, center, 5, 255, -1)
    images['Padrão Radial'] = img4
    
    img5 = np.zeros((size, size), dtype=np.uint8)
    for y in [25, 40, 55, 70, 85]:
        cv2.line(img5, (10, y), (110, y), 255, 1)
        for x in [15, 25, 35, 50, 60, 70, 85, 95]:
            if np.random.random() > 0.3:
                cv2.line(img5, (x, y-3), (x, y+3), 200, 1)
    images['Texto Simulado'] = img5
    
    img6 = np.zeros((size, size), dtype=np.uint8)
    for i in range(-size, size, 10):
        cv2.line(img6, (0, i), (size, i + size), 255, 1)
        cv2.line(img6, (i, 0), (i + size, size), 180, 1)
    cv2.circle(img6, (30, 90), 12, 200, 2)
    cv2.rectangle(img6, (70, 20), (100, 50), 220, -1)
    images['Padrão Diagonal'] = img6

    img7 = np.tile(np.linspace(50, 200, size, dtype=np.uint8), (size, 1))
    images['Gradiente Suave'] = img7

    img8 = np.random.randint(0, 255, (size, size), dtype=np.uint8)
    images['Ruído Aleatório'] = img8

    img9 = np.zeros((size, size), dtype=np.uint8)
    cv2.circle(img9, (60, 60), 30, 200, -1)
    img9 = cv2.GaussianBlur(img9, (15, 15), 5)
    images['Formas Desfocadas'] = img9

    
    return images

def demo_all_test_images():
    print("=== Demonstração com Todas as Imagens de Teste ===")
    print("INSTRUÇÕES:")
    print("- Após cada imagem aparecer, volte ao terminal")
    print("- Pressione ENTER para próxima imagem")
    print("- Digite 'q' + ENTER para sair")
    print("- Ou simplesmente feche a janela da imagem")
    
    test_images = create_test_images()
    upscaler = SimplePolarizationUpscaler()
    
    total_images = len(test_images)
    current = 1
    
    try:
        for name, img in test_images.items():
            print(f"\nProcessando ({current}/{total_images}): {name}...")
            
            pol_result = upscaler.polarization_upscale(img, scale=2)
            conv_result = upscaler.conventional_upscale(img, scale=2)
            
            fig = plt.figure(figsize=(12, 4))
            
            plt.subplot(1, 3, 1)
            plt.imshow(img, cmap='gray')
            plt.title(f'{name}\nOriginal ({img.shape[1]}x{img.shape[0]})')
            plt.axis('off')
            
            plt.subplot(1, 3, 2)
            plt.imshow(conv_result, cmap='gray')
            plt.title('Convencional (2x)')
            plt.axis('off')
            
            plt.subplot(1, 3, 3)
            plt.imshow(pol_result, cmap='gray')
            plt.title('Polarização (2x)')
            plt.axis('off')
            
            plt.suptitle(f'Imagem {current}/{total_images}: {name}', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            plt.show(block=False)
            plt.draw()
            
            if current < total_images:
                print(f"\n✓ Imagem {current}/{total_images} exibida: {name}")
                print("→ Volte ao terminal e pressione ENTER para continuar...")
                
                try:
                    user_input = input(f"[ENTER] Próxima | [q + ENTER] Sair: ").strip().lower()
                    if user_input == 'q':
                        print("Demonstração interrompida pelo usuário.")
                        plt.close('all')
                        return
                except KeyboardInterrupt:
                    print("\nDemonstração interrompida pelo usuário.")
                    plt.close('all')
                    return
            else:
                print(f"\n✓ Imagem final {current}/{total_images} exibida: {name}")
                input("Pressione ENTER para finalizar...")
            
            plt.close(fig)
            current += 1
        
        print(f"\nDemonstração concluída! Processadas {total_images} imagens de teste.")
        
    except Exception as e:
        print(f"Erro durante a demonstração: {e}")
        plt.close('all')
    finally:
        plt.close('all')

def demo_simple_polarization():
    print("=== Demonstração Simples ===")
    
    test_images = create_test_images()
    test_img = test_images['Linhas e Círculos']
    
    upscaler = SimplePolarizationUpscaler()
    pol_result = upscaler.polarization_upscale(test_img, scale=2)
    conv_result = upscaler.conventional_upscale(test_img, scale=2)
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    plt.imshow(test_img, cmap='gray')
    plt.title(f'Original\n({test_img.shape[1]}x{test_img.shape[0]})')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.imshow(conv_result, cmap='gray')
    plt.title('Convencional (2x)')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.imshow(pol_result, cmap='gray')
    plt.title('Polarização (2x)')
    plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def choose_test_image():
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
                
                upscaler = SimplePolarizationUpscaler()
                pol_result = upscaler.polarization_upscale(selected_img, scale=2)
                conv_result = upscaler.conventional_upscale(selected_img, scale=2)
                
                plt.figure(figsize=(12, 4))
                
                plt.subplot(1, 3, 1)
                plt.imshow(selected_img, cmap='gray')
                plt.title(f'Original: {selected_name}\n({selected_img.shape[1]}x{selected_img.shape[0]})')
                plt.axis('off')
                
                plt.subplot(1, 3, 2)
                plt.imshow(conv_result, cmap='gray')
                plt.title('Convencional (2x)')
                plt.axis('off')
                
                plt.subplot(1, 3, 3)
                plt.imshow(pol_result, cmap='gray')
                plt.title('Polarização (2x)')
                plt.axis('off')
                
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
    print("\n" + "="*50)
    print("  POLARIZATION UPSCALER")
    print("  Ampliação de Imagens com Polarização")
    print("="*50)
    print("\nEscolha uma opção:")
    print("1. Processar sua própria imagem")
    print("2. Demonstração com imagem de teste específica")
    print("3. Demonstração com todas as imagens de teste")
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
                demo_all_test_images()
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
    try:
        import tkinter.simpledialog
        main_menu()
    except ImportError:
        print("Aviso: tkinter não disponível. Executando apenas demonstração.")
        demo_simple_polarization()