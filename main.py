import cv2
import numpy as np
import pandas as pd
from tkinter import filedialog, Tk, Label, Button, messagebox

# Função para detectar os círculos na imagem
def detect_tubes(image_path, root):
    image = cv2.imread(image_path)
    if image is None:
        print("Erro ao carregar a imagem. Verifique o caminho e tente novamente.")
        return None, None

    print(f"Imagem carregada com sucesso: {image_path}")

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)

    circles = cv2.HoughCircles(
        blurred_image,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=15,
        param1=10,
        param2=8,
        minRadius=3,
        maxRadius=5
    )

    if circles is None:
        print("Nenhum círculo detectado.")
        return None, None

    circles = np.uint16(np.around(circles))
    detected_circles = [(x, y, radius) for x, y, radius in circles[0, :]]

    return detected_circles, image

# Função para salvar apenas a tabela
def save_table(detected_circles):
    table = {"Linha": [], "Tubo": []}
    
    # Agrupar os círculos em linhas
    detected_circles_sorted = sorted(detected_circles, key=lambda x: x[1])  # Ordena por Y (vertical)
    tolerance = 10  # Tolerância para agrupar tubos na mesma linha
    rows = []
    current_row = [detected_circles_sorted[0]]

    for i in range(1, len(detected_circles_sorted)):
        if abs(detected_circles_sorted[i][1] - current_row[-1][1]) <= tolerance:
            current_row.append(detected_circles_sorted[i])
        else:
            rows.append(current_row)
            current_row = [detected_circles_sorted[i]]
    rows.append(current_row)  # Adicionar a última linha

    # Numerando os tubos sequencialmente por linha
    row_number = 1
    for row in rows:
        for tube_number, _ in enumerate(row, start=1):
            table["Linha"].append(row_number)
            table["Tubo"].append(tube_number)
        row_number += 1

    # Caminho para salvar a tabela
    excel_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
    if excel_path:
        df = pd.DataFrame(table)
        df["Tubo"] = df["Tubo"].astype(int)  # Garantir que os números de tubo sejam inteiros
        df["Linha"] = df["Linha"].astype(int)  # Garantir que os números de linha sejam inteiros
        df.to_excel(excel_path, index=False)

        # Mensagem de sucesso
        messagebox.showinfo("Sucesso", f"Tabela salva em:\n{excel_path}")
    else:
        print("Salvamento da tabela cancelado.")

# Função para interação com a imagem
def interact_with_image(detected_circles, image):
    added_circles = detected_circles.copy()  # Círculos inicialmente detectados
    current_image = image.copy()

    # Função para remover um círculo
    def remove_circle(event, x, y, flags, param):
        nonlocal added_circles
        if event == cv2.EVENT_RBUTTONDOWN:  # Botão direito
            radius_tolerance = 10  # Tolerância para remover o círculo
            for i, (cx, cy, radius) in enumerate(added_circles):
                distance = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if distance < radius + radius_tolerance:
                    print(f"Removendo círculo: {added_circles[i]}")
                    added_circles.pop(i)
                    break  # Remover apenas o primeiro que encontrar

    # Função para adicionar um círculo
    def add_circle(event, x, y, flags, param):
        nonlocal added_circles
        if event == cv2.EVENT_LBUTTONDOWN:  # Botão esquerdo
            radius = 5  # Tamanho fixo para novos círculos
            added_circles.append((x, y, radius))
            print(f"Adicionando círculo: {(x, y, radius)}")

    # Função para exibir a imagem e aguardar a interação
    def display_image():
        nonlocal current_image
        while True:
            img_copy = current_image.copy()
            for circle in added_circles:
                cv2.circle(img_copy, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
                cv2.circle(img_copy, (circle[0], circle[1]), 1, (0, 0, 255), 3)

            cv2.imshow("Interação com Círculos", img_copy)  # Exibir a imagem com círculos

            # Aguardar o clique do mouse
            cv2.setMouseCallback("Interação com Círculos", lambda event, x, y, flags, param: add_circle(event, x, y, flags, param) if event == cv2.EVENT_LBUTTONDOWN else remove_circle(event, x, y, flags, param))

            # Aguardar até que o usuário pressione 'q' para sair
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):  # Pressione 'q' para sair
                break

        cv2.destroyAllWindows()

    # Exibir a imagem e permitir interação
    display_image()

    # Após a interação, salvar a tabela
    save_table(added_circles)

# Função para selecionar o arquivo de imagem
def select_image_file(root):
    file_path = filedialog.askopenfilename(title="Selecione o arquivo de imagem", filetypes=[("Imagens", "*.png *.jpg *.jpeg")])
    if file_path:
        detected_circles, image = detect_tubes(file_path, root)  # Detectar os tubos automaticamente
        if detected_circles:
            interact_with_image(detected_circles, image)  # Iniciar interação com a imagem

# Função para criar a interface gráfica
def create_gui():
    root = Tk()
    root.title("Gerador de Planilha Linha | Tubo")

    # Tamanho da janela
    root.geometry("400x200")

    # Label
    label = Label(root, text="Selecione a imagem para detectar os tubos", padx=10, pady=10)
    label.pack()

    # Botão para selecionar a imagem e iniciar a detecção
    button = Button(root, text="Selecionar Imagem", command=lambda: select_image_file(root), padx=10, pady=10)
    button.pack()

    root.mainloop()

# Iniciar a interface gráfica
create_gui()
