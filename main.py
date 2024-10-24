# Cambios a la aplicacion:
# Colores que no sean gris como colores claros, talvez cafe
# Mas grande la barra de busqueda
# Historial de palabras mas chico y mas angosto

# Link para señas de manos: https://es.hesperian.org/hhg/Disabled_Village_Children:Lenguaje_de_se%C3%B1as

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
                # No componemos sobre fondo blanco, mantenemos la transparencia
                self.sequence.append(ImageTk.PhotoImage(frame))
            self.configure(image=self.sequence[0])
        except EOFError:
            pass

    def next_frame(self):
        self.idx = (self.idx + 1) % len(self.sequence)
        self.configure(image=self.sequence[self.idx])
        self.after(self.delay, self.next_frame)

# Función para redimensionar las imágenes o GIFs manteniendo la proporción
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

    # Definir tamaño máximo para las imágenes
    max_image_height = 50  # Ajusta este valor según tus necesidades
    max_image_width = 50   # Ajusta este valor según tus necesidades

    for word in words:
        word_images = []  # Imágenes para la palabra actual
        # Intentar buscar la imagen/GIF correspondiente a la palabra completa
        word_image_path_gif = f"words/{word}.gif"
        word_image_path_png = f"words/{word}.png"

        if os.path.exists(word_image_path_gif):
            word_images.append((word_image_path_gif, 'gif'))
        elif os.path.exists(word_image_path_png):
            word_images.append((word_image_path_png, 'png'))
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
                            word_images.append((letter_image_path_gif, 'gif'))
                            letter_found = True
                            break
                        elif os.path.exists(letter_image_path_png):
                            word_images.append((letter_image_path_png, 'png'))
                            letter_found = True
                            break

                    # Si no se encontró una imagen para el carácter, ignorar y continuar
                    if not letter_found:
                        continue

        # Crear un contenedor con borde para separar visualmente cada palabra
        word_frame = tk.Frame(inner_frame, bg='#f0f0f0', bd=2, relief='solid', padx=10, pady=10)
        word_frame.pack(fill='x', pady=10)  # Añadir separación entre grupos

        # Colocar la palabra en la parte superior del contenedor
        word_label = tk.Label(word_frame, text=word, bg='#f0f0f0', font=('Helvetica', 14, 'bold'))
        word_label.pack(pady=(0, 5))  # Colocar la palabra arriba con un pequeño margen

        # Crear un sub-contenedor para las imágenes que se centrará
        images_frame = tk.Frame(word_frame, bg='#f0f0f0')
        images_frame.pack(anchor='center')  # Centrar el contenedor de las imágenes

        # Redimensionar imágenes y colocarlas en el sub-contenedor centrado
        for img_path, img_type in word_images:
            if img_type == 'gif':
                # Manejar GIFs animados
                label = AnimatedGIF(images_frame, img_path, bg='#f0f0f0')
                label.pack(side='left', padx=5, pady=5)
            else:
                # Cargar y redimensionar imágenes
                img = Image.open(img_path).convert('RGBA')
                img = resize_image(img, max_image_width, max_image_height)
                img_tk = ImageTk.PhotoImage(img)
                label = tk.Label(images_frame, image=img_tk, bg='#f0f0f0')
                label.image = img_tk  # Evita que la imagen se elimine
                label.pack(side='left', padx=5, pady=5)

    # Ajustar el tamaño del inner_frame para el scroll
    inner_frame.update_idletasks()
    image_canvas.config(scrollregion=image_canvas.bbox("all"))


# Función para actualizar el historial de palabras buscadas
def update_history(text):
    search_history.append(text)
    index = len(search_history)
    
    # Crear una etiqueta clicable para cada palabra en el historial
    history_label = tk.Label(history_text, text=f"{index}. {text}", fg="blue", cursor="hand2", font=('Helvetica', 12))
    history_label.pack(anchor='w', padx=5, pady=2)

    # Asociar evento de clic a la etiqueta
    history_label.bind("<Button-1>", lambda event, t=text: on_history_click(t))

    # Guardar el historial en el archivo
    if os.path.exists("historial_palabras.txt"):
        with open("historial_palabras.txt", "r+", encoding='utf-8') as file:
            content = file.read()
            file.seek(0, 0)
            file.write(text + "\n" + content)  # Insertar al principio del archivo
    else:
        with open("historial_palabras.txt", "w", encoding='utf-8') as file:
            file.write(text + "\n")

def on_history_click(text):
    # Colocar la palabra/frase en la barra de búsqueda
    entry.delete(0, tk.END)  # Borrar cualquier texto actual
    entry.insert(0, text)    # Insertar la palabra/frase del historial

    # Mostrar las imágenes nuevamente
    show_images(text)

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
