import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
from ttkthemes import ThemedTk
import os

# Historial de palabras buscadas
search_history = []

# Clase para manejar GIFs animados
class AnimatedGIF(tk.Label):
    def __init__(self, master, path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.sequence = []
        self.delay = 100  # Tiempo entre cuadros en milisegundos

        # Cargar el GIF y obtener los cuadros
        self.load_frames(path)

        self.idx = 0
        if len(self.sequence) > 1:
            self.after(self.delay, self.next_frame)

    def load_frames(self, path):
        img = Image.open(path)
        try:
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert('RGBA')
                self.sequence.append(ImageTk.PhotoImage(frame))
            self.configure(image=self.sequence[0])
        except EOFError:
            pass

    def next_frame(self):
        self.idx = (self.idx + 1) % len(self.sequence)
        self.configure(image=self.sequence[self.idx])
        self.after(self.delay, self.next_frame)

# Función para redimensionar las imágenes o GIFs si no caben en la pantalla
def resize_image(img, max_width, max_height):
    # Obtener tamaño original de la imagen
    original_width, original_height = img.size

    # Calcular factor de escala para ajustar la imagen a los límites máximos
    scale_factor = min(max_width / original_width, max_height / original_height)

    # Redimensionar la imagen manteniendo la proporción
    new_size = (int(original_width * scale_factor), int(original_height * scale_factor))
    return img.resize(new_size, Image.LANCZOS)

# Función para mostrar las imágenes de cada letra o palabra
def show_images(text):
    # Elimina cualquier imagen mostrada previamente
    for widget in inner_frame.winfo_children():
        widget.destroy()

    words = text.split()  # Divide el texto en palabras

    # Obtener el ancho disponible en el frame
    inner_frame.update_idletasks()
    frame_width = inner_frame.winfo_width()

    # Definir tamaño máximo para las imágenes (ajustado para ser un poco más pequeño)
    max_image_height = 150  # Ajusta este valor según tus necesidades (originalmente 200)
    max_image_width = 150   # Ajusta este valor según tus necesidades (originalmente 200)

    # Lista para almacenar todas las imágenes
    images_list = []

    for word in words:
        # Intentar buscar la imagen/GIF correspondiente a la palabra completa
        word_image_path_gif = f"words/{word}.gif"
        word_image_path_png = f"words/{word}.png"

        if os.path.exists(word_image_path_gif):
            # Si existe un GIF para la palabra completa
            images_list.append((word_image_path_gif, 'gif'))
        elif os.path.exists(word_image_path_png):
            # Si existe una imagen PNG para la palabra completa
            images_list.append((word_image_path_png, 'png'))
        else:
            # Si no hay imagen de la palabra, añadir las imágenes de las letras
            for letter in word:
                if letter == " ":
                    continue  # Saltar espacios
                else:
                    # Buscar tanto mayúsculas como minúsculas y ambos formatos
                    letter_variants = [letter.lower(), letter.upper()]
                    letter_found = False
                    for l in letter_variants:
                        letter_image_path_gif = f"images/{l}.gif"
                        letter_image_path_png = f"images/{l}.png"

                        if os.path.exists(letter_image_path_gif):
                            images_list.append((letter_image_path_gif, 'gif'))
                            letter_found = True
                            break
                        elif os.path.exists(letter_image_path_png):
                            images_list.append((letter_image_path_png, 'png'))
                            letter_found = True
                            break
                    if not letter_found:
                        print(f"No se encontró imagen para: {letter}")

    # Calcular el número de imágenes por fila
    num_images = len(images_list)
    if num_images == 0:
        return

    # Estimar ancho de imagen
    estimated_image_width = max_image_width + 10  # Añadimos margen

    images_per_row = max(1, frame_width // estimated_image_width)
    if images_per_row > num_images:
        images_per_row = num_images

    # Ajustar las columnas para que se distribuyan uniformemente
    for i in range(images_per_row):
        inner_frame.grid_columnconfigure(i, weight=1)

    # Redimensionar imágenes y colocarlas en el grid
    row = 0
    col = 0
    for img_path, img_type in images_list:
        if img_type == 'gif':
            # Manejar GIFs animados
            label = AnimatedGIF(inner_frame, img_path, bg='#f0f0f0')
            label.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        else:
            # Cargar y redimensionar imágenes
            img = Image.open(img_path)
            img = resize_image(img, max_image_width, max_image_height)
            img_tk = ImageTk.PhotoImage(img)
            label = tk.Label(inner_frame, image=img_tk, bg='#f0f0f0')
            label.image = img_tk  # Evita que la imagen se elimine
            label.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

        col += 1
        if col >= images_per_row:
            col = 0
            row += 1

    # Ajustar el tamaño del inner_frame para el scroll
    inner_frame.update_idletasks()
    image_canvas.config(scrollregion=image_canvas.bbox("all"))

# Función para actualizar el historial de palabras buscadas
def update_history(text):
    search_history.append(text)
    index = len(search_history)
    history_entry = f"{index}. {text}\n"
    history_text.configure(state='normal')
    history_text.insert(tk.END, history_entry)
    history_text.configure(state='disabled')
    with open("historial_palabras.txt", "a", encoding='utf-8') as file:
        file.write(text + "\n")

# Función para procesar la entrada del usuario
def process_input():
    text = entry.get()
    if text:
        show_images(text)
        update_history(text)

# Función para borrar el contenido del campo de entrada
def clear_entry():
    entry.delete(0, tk.END)

# Crear ventana con tema moderno usando ThemedTk
root = ThemedTk(theme="arc")
root.title("Lenguaje de Señas")

# Configuración para maximizar la ventana al inicio sin ocultar decoraciones
try:
    root.state('zoomed')  # Funciona en Windows
except:
    # Para Linux y macOS podemos ajustar la geometría manualmente
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{screen_width}x{screen_height}")

# Estilos generales
root.configure(bg='#f0f0f0')

# Estilo para el scrollbar
style = ttk.Style()

# Usar un tema moderno
style.theme_use('clam')  # Puedes probar otros temas como 'alt', 'default', 'classic'

# Personalizar el estilo del scrollbar
style.configure("Vertical.TScrollbar",
                background="#C0C0C0",
                troughcolor="#f0f0f0",
                bordercolor="#f0f0f0",
                arrowcolor="#505050",
                gripcount=0,
                relief='flat')

style.map("Vertical.TScrollbar",
          background=[('active', '#A0A0A0'), ('disabled', '#f0f0f0')],
          arrowcolor=[('active', '#303030')])

# Fuente más grande para los textos
font_large = ('Helvetica', 12)

# Frame para la entrada y los botones
input_frame = tk.Frame(root, bg='#f0f0f0')
input_frame.pack(pady=10)

# Campo de entrada
entry_label = ttk.Label(input_frame, text="Escribe una palabra o frase:", background='#f0f0f0', font=font_large)
entry_label.pack(pady=5)
entry = ttk.Entry(input_frame, width=80, font=font_large)  # Entrada más larga y con fuente más grande
entry.pack(padx=10, pady=5)

# Frame para los botones de acción
button_frame = tk.Frame(input_frame, bg='#f0f0f0')
button_frame.pack(pady=5)

# Botón para procesar la entrada
button = ttk.Button(button_frame, text="Mostrar", command=process_input)
button.pack(side=tk.LEFT, padx=5)

# Botón para borrar el contenido del campo de entrada
clear_button = ttk.Button(button_frame, text="Borrar", command=clear_entry)
clear_button.pack(side=tk.LEFT, padx=5)

# Frame principal para el contenido
content_frame = tk.Frame(root)
content_frame.pack(fill=tk.BOTH, expand=True)

content_frame.columnconfigure(0, weight=1)
content_frame.columnconfigure(1, weight=4)
content_frame.rowconfigure(0, weight=1)

# Historial de búsquedas
history_frame = tk.Frame(content_frame, bg='#f0f0f0')
history_frame.grid(row=0, column=0, sticky='nsew')

history_label = ttk.Label(history_frame, text="Historial de palabras:", background='#f0f0f0', font=font_large)
history_label.pack(pady=5)

# Text widget para el historial
history_text = tk.Text(history_frame, width=30, wrap='word', state='disabled', font=font_large)
history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar para el historial
history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=history_text.yview)
history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
history_text.configure(yscrollcommand=history_scrollbar.set)

# Frame para el canvas de imágenes y scrollbar
canvas_frame = tk.Frame(content_frame)
canvas_frame.grid(row=0, column=1, sticky='nsew')

# Canvas para las imágenes
image_canvas = tk.Canvas(canvas_frame, bg='#f0f0f0', highlightthickness=0)
image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Scrollbar vertical para el canvas de imágenes
scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=image_canvas.yview, style="Vertical.TScrollbar")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
image_canvas.configure(yscrollcommand=scrollbar.set)

# Frame interno donde se colocarán las imágenes
inner_frame = tk.Frame(image_canvas, bg='#f0f0f0')
inner_frame_window = image_canvas.create_window((0, 0), window=inner_frame, anchor='nw')

# Ajustar el ancho del inner_frame al ancho del canvas
def resize_inner_frame(event):
    canvas_width = event.width
    image_canvas.itemconfig(inner_frame_window, width=canvas_width)
inner_frame.bind('<Configure>', lambda event: image_canvas.configure(scrollregion=image_canvas.bbox("all")))
image_canvas.bind('<Configure>', resize_inner_frame)

# Ejecutar la aplicación
root.mainloop()
