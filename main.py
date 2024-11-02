# Link para señas de manos: https://es.hesperian.org/hhg/Disabled_Village_Children:Lenguaje_de_se%C3%B1as

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
from ttkthemes import ThemedTk
import os
from collections import defaultdict

# Historial de palabras buscadas
search_history = []

# Símbolos que no se utilizan en el lenguaje de señas
symbols_not_used = [',', '.', '_', '-', '{', '}', '[', ']', '(', ')', '!']

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
root.configure(bg='#F5E8D0')

# Estilo para el scrollbar
style = ttk.Style()

# Usar un tema moderno
style.theme_use('clam')  # Puedes probar otros temas como 'alt', 'default', 'classic'

# Personalizar el estilo del scrollbar
style.configure("Vertical.TScrollbar",
                background="#C0C0C0",
                troughcolor="#F5E8D0",
                bordercolor="#F5E8D0",
                arrowcolor="#505050",
                gripcount=0,
                relief='flat')

style.configure("Horizontal.TScrollbar",
                background="#C0C0C0",
                troughcolor="#F5E8D0",
                bordercolor="#F5E8D0",
                arrowcolor="#505050",
                gripcount=0,
                relief='flat')

style.map("Vertical.TScrollbar",
          background=[('active', '#A0A0A0'), ('disabled', '#F5E8D0')],
          arrowcolor=[('active', '#303030')])

style.map("Horizontal.TScrollbar",
          background=[('active', '#A0A0A0'), ('disabled', '#F5E8D0')],
          arrowcolor=[('active', '#303030')])

style.map("TButton",
          background=[('active', '#A97C50')],  # Color de fondo cuando está activo
          foreground=[('active', '#FFFFFF')])  # Color del texto cuando está activo

# Personalizar estilo de botones y entradas
style.configure("TButton", font=('Helvetica', 14))
style.configure("TButton", background='#D4B897', foreground='#8B4513')
style.configure("TEntry", fieldbackground='#F5E8D0', foreground='#8B4513')

# Fuente más grande para los textos
font_large = ('Helvetica', 12)

# Contenedor principal para los frames
container = tk.Frame(root)
container.pack(side="top", fill="both", expand=True)
container.configure(bg='#F5E8D0')

# Configurar el grid en el contenedor principal
container.grid_rowconfigure(0, weight=1)
container.grid_columnconfigure(0, weight=1)

# Diccionario para mantener referencias a los frames
frames = {}

def show_frame(frame_name):
    frame = frames[frame_name]
    frame.tkraise()

# Clase para el frame del Traductor
class TraductorFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#F5E8D0')

        # Configurar el grid en el frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Frame para la entrada y los botones
        input_frame = tk.Frame(self, bg='#F5E8D0')
        input_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Ajustar el grid del input_frame
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)

        # Campo de entrada
        entry_label = ttk.Label(input_frame, text="Escribe una palabra o frase:", background='#F5E8D0', font=('Helvetica', 16), foreground='#8B4513')
        entry_label.grid(row=0, column=0, columnspan=3, pady=5, sticky="w")
        self.entry = ttk.Entry(input_frame, width=100, font=('Helvetica', 16), style="TEntry")
        self.entry.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        # Frame para los botones de acción
        button_frame = tk.Frame(input_frame, bg='#F5E8D0')
        button_frame.grid(row=2, column=0, columnspan=3, pady=5)

        # Botón para procesar la entrada
        button = ttk.Button(button_frame, text="Mostrar", command=self.process_input, style="TButton", padding=(5, 5))
        button.pack(side=tk.LEFT, padx=5)

        # Botón para borrar el contenido del campo de entrada
        clear_button = ttk.Button(button_frame, text="Borrar", command=self.clear_entry, style="TButton", padding=(5, 5))
        clear_button.pack(side=tk.LEFT, padx=5)

        # Frame principal para el contenido
        content_frame = tk.Frame(self, bg='#F5E8D0')
        content_frame.grid(row=1, column=0, sticky="nsew")

        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=4)
        content_frame.rowconfigure(0, weight=1)

        # Historial de búsquedas
        history_frame = tk.Frame(content_frame, bg='#F5E8D0')
        history_frame.grid(row=0, column=0, sticky='nsew')

        history_label = ttk.Label(history_frame, text="Historial de palabras (haz clic en una palabra para volver a verla):", background='#F5E8D0', font=('Helvetica', 16), foreground='#8B4513')
        history_label.pack(pady=5)

        # Text widget para el historial
        self.history_text = tk.Text(history_frame, width=30, wrap='word', state='disabled', font=font_large)
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar para el historial
        history_scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        # Cambiar el fondo del historial de palabras
        self.history_text.configure(bg='#F1D9B0', fg='#8B4513', yscrollcommand=history_scrollbar.set)
        self.history_text.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Frame para el canvas de imágenes y scrollbars
        canvas_frame = tk.Frame(content_frame)
        canvas_frame.grid(row=0, column=1, sticky='nsew')

        # Canvas para las imágenes
        self.image_canvas = tk.Canvas(canvas_frame, bg='#F5E8D0')
        self.image_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar vertical para el canvas de imágenes
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.image_canvas.yview, style="Vertical.TScrollbar")
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Scrollbar horizontal para el canvas de imágenes
        h_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.image_canvas.xview, style="Horizontal.TScrollbar")
        h_scrollbar.grid(row=2, column=0, sticky='ew')

        self.image_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.image_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Frame interno donde se colocarán las imágenes
        self.inner_frame = tk.Frame(self.image_canvas, bg='#F5E8D0')
        self.inner_frame_window = self.image_canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

        # Ajustar el ancho del inner_frame al ancho del canvas
        self.inner_frame.bind('<Configure>', self.update_scrollregion)
        self.image_canvas.bind('<Configure>', self.resize_inner_frame)

    # Funciones internas del TraductorFrame
    def process_input(self):
        text = self.entry.get()
        if text:
            self.show_images(text)
            self.update_history(text)

    def clear_entry(self):
        self.entry.delete(0, tk.END)

    def on_mouse_wheel(self, event):
        # Desplazar el canvas de imágenes
        self.image_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        # Desplazar el historial de búsqueda
        self.history_text.yview_scroll(int(-1*(event.delta/120)), "units")

    def resize_inner_frame(self, event):
        # Ajustar el ancho del inner_frame al ancho del canvas si es mayor
        canvas_width = event.width
        self.image_canvas.itemconfig(self.inner_frame_window, width=canvas_width)

    def update_scrollregion(self, event=None):
        # Actualizar el scrollregion del canvas
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))

    def update_history(self, text):
        # Añadir la nueva búsqueda al historial
        search_history.append(text)
        index = len(search_history)  # Contador de búsqueda (el total de búsquedas realizadas)

        # Crear una etiqueta clicable para cada palabra en el historial
        # Crear una etiqueta clicable para cada palabra en el historial
        self.history_text.configure(state='normal')
        self.history_text.insert('end', f"{index}. {text}\n")
        start_index = f"{index}.0"
        end_index = f"{index}.end"
        tag_name = f"item{index}"
        self.history_text.tag_add(tag_name, start_index, end_index)
        self.history_text.tag_bind(tag_name, "<Button-1>", lambda event, t=text: self.on_history_click(t))
        self.history_text.tag_bind(tag_name, "<Enter>", lambda event: self.history_text.tag_configure(tag_name, underline=True, foreground="#0000FF") or self.history_text.config(cursor="hand2"))
        self.history_text.tag_bind(tag_name, "<Leave>", lambda event: self.history_text.tag_configure(tag_name, underline=False, foreground="#8B4513") or self.history_text.config(cursor=""))
        self.history_text.tag_configure(tag_name, foreground="#8B4513")
        self.history_text.configure(state='disabled')


        # Guardar el historial en el archivo
        if os.path.exists("historial_palabras.txt"):
            with open("historial_palabras.txt", "r+", encoding='utf-8') as file:
                content = file.read()
                file.seek(0, 0)
                file.write(text + "\n" + content)  # Insertar al principio del archivo
        else:
            with open("historial_palabras.txt", "w", encoding='utf-8') as file:
                file.write(text + "\n")

    def on_history_click(self, text):
        # Colocar la palabra/frase en la barra de búsqueda
        self.entry.delete(0, tk.END)  # Borrar cualquier texto actual
        self.entry.insert(0, text)    # Insertar la palabra/frase del historial

        self.show_images(text)

    def show_images(self, text):
        # Elimina cualquier imagen mostrada previamente
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Definir tamaño máximo para las imágenes
        max_image_height = 90  # Ajusta este valor según tus necesidades
        max_image_width = 90   # Ajusta este valor según tus necesidades

        # Dividir el texto en palabras
        words = text.split()
        i = 0
        while i < len(words):
            found_match = False
            # Intentar encontrar la frase más larga desde la posición actual
            for j in range(len(words), i, -1):
                phrase = ' '.join(words[i:j])
                phrase_with_underscores = phrase.replace(' ', '_')
                # Intentar encontrar la imagen de la frase
                image_dirs = ['phrases', 'words']
                found_image = False
                word_images = []

                for dir in image_dirs:
                    text_image_path_gif = f"{dir}/{phrase_with_underscores}.gif"
                    text_image_path_png = f"{dir}/{phrase_with_underscores}.png"
                    text_image_path_jpeg = f"{dir}/{phrase_with_underscores}.jpeg"

                    if os.path.exists(text_image_path_gif):
                        word_images.append((text_image_path_gif, 'gif'))
                        found_image = True
                        break
                    elif os.path.exists(text_image_path_png):
                        word_images.append((text_image_path_png, 'png'))
                        found_image = True
                        break
                    elif os.path.exists(text_image_path_jpeg):
                        word_images.append((text_image_path_jpeg, 'jpeg'))
                        found_image = True
                        break

                if found_image:
                    # Mostrar la imagen de la frase encontrada
                    word_frame = tk.Frame(self.inner_frame, bg='#F5E8D0', bd=2, relief='solid',
                                        padx=10, pady=10, highlightbackground='#A97C50')
                    word_frame.pack(fill='x', pady=10)

                    word_label = tk.Label(word_frame, text=phrase, bg='#F5E8D0',
                                        font=('Helvetica', 14, 'bold'), fg='#8B4513')
                    word_label.pack(pady=(0, 5))

                    images_frame = tk.Frame(word_frame, bg='#F5E8D0')
                    images_frame.pack(anchor='center')

                    for img_path, img_type in word_images:
                        if img_type == 'gif':
                            label = AnimatedGIF(images_frame, img_path, bg='#F5E8D0')
                            label.pack(side='left', padx=5, pady=5)
                        elif img_type in ['png', 'jpeg']:
                            img = Image.open(img_path).convert('RGBA')
                            img = resize_image(img, max_image_width, max_image_height)
                            img_tk = ImageTk.PhotoImage(img)
                            label = tk.Label(images_frame, image=img_tk, bg='#F5E8D0')
                            label.image = img_tk  # Evita que la imagen se elimine
                            label.pack(side='left', padx=5, pady=5)

                    # Actualizar el scroll
                    self.inner_frame.update_idletasks()
                    self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))
                    i = j  # Avanzar el índice a la posición después de la frase encontrada
                    found_match = True
                    break  # Salir del bucle interno ya que se encontró la frase

            if not found_match:
                # Procesar words[i] como palabra individual
                word = words[i]
                word_images = []
                # Lista de directorios donde buscar imágenes de palabras
                word_dirs = ['words', 'numbers']

                found_word_image = False
                for dir in word_dirs:
                    word_image_path_gif = f"{dir}/{word}.gif"
                    word_image_path_png = f"{dir}/{word}.png"
                    word_image_path_jpeg = f"{dir}/{word}.jpeg"

                    if os.path.exists(word_image_path_gif):
                        word_images.append((word_image_path_gif, 'gif'))
                        found_word_image = True
                        break
                    elif os.path.exists(word_image_path_png):
                        word_images.append((word_image_path_png, 'png'))
                        found_word_image = True
                        break
                    elif os.path.exists(word_image_path_jpeg):
                        word_images.append((word_image_path_jpeg, 'jpeg'))
                        found_word_image = True
                        break

                if not found_word_image:
                    # Si no se encuentra la palabra, procesar por letras
                    for letter in word:
                        if letter == " ":
                            continue
                        elif letter in symbols_not_used:
                            warning_message = f"El símbolo '{letter}' no se usa en el lenguaje de señas."
                            word_images.append((warning_message, 'warning'))
                            continue
                        elif letter == "?":
                            question_image_path_gif = "images/question_mark.gif"
                            question_image_path_png = "images/question_mark.png"
                            if os.path.exists(question_image_path_gif):
                                word_images.append((question_image_path_gif, 'gif'))
                            elif os.path.exists(question_image_path_png):
                                word_images.append((question_image_path_png, 'png'))
                        else:
                            letter_variants = [letter.lower(), letter.upper()]
                            letter_found = False
                            for l in letter_variants:
                                letter_image_path_gif = f"images/{l}.gif"
                                letter_image_path_png = f"images/{l}.png"
                                letter_image_path_jpeg = f"images/{l}.jpeg"

                                if os.path.exists(letter_image_path_gif):
                                    word_images.append((letter_image_path_gif, 'gif'))
                                    letter_found = True
                                    break
                                elif os.path.exists(letter_image_path_png):
                                    word_images.append((letter_image_path_png, 'png'))
                                    letter_found = True
                                    break
                                elif os.path.exists(letter_image_path_jpeg):
                                    word_images.append((letter_image_path_jpeg, 'jpeg'))
                                    letter_found = True
                                    break

                            if not letter_found:
                                continue

                # Mostrar imágenes de la palabra o letras
                word_frame = tk.Frame(self.inner_frame, bg='#F5E8D0', bd=2, relief='solid',
                                    padx=10, pady=10, highlightbackground='#A97C50')
                word_frame.pack(fill='x', pady=10)

                word_label = tk.Label(word_frame, text=word, bg='#F5E8D0',
                                    font=('Helvetica', 14, 'bold'), fg='#8B4513')
                word_label.pack(pady=(0, 5))

                images_frame = tk.Frame(word_frame, bg='#F5E8D0')
                images_frame.pack(anchor='center')

                for img_path, img_type in word_images:
                    if img_type == 'gif':
                        label = AnimatedGIF(images_frame, img_path, bg='#F5E8D0')
                        label.pack(side='left', padx=5, pady=5)
                    elif img_type in ['png', 'jpeg']:
                        img = Image.open(img_path).convert('RGBA')
                        img = resize_image(img, max_image_width, max_image_height)
                        img_tk = ImageTk.PhotoImage(img)
                        label = tk.Label(images_frame, image=img_tk, bg='#F5E8D0')
                        label.image = img_tk
                        label.pack(side='left', padx=5, pady=5)
                    elif img_type == 'warning':
                        warning_label = tk.Label(images_frame, text=img_path, fg='red', bg='#F5E8D0',
                                                font=('Helvetica', 12, 'bold'))
                        warning_label.pack(side='left', padx=5, pady=5)

                # Actualizar el scroll
                self.inner_frame.update_idletasks()
                self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))
                i += 1  # Avanzar al siguiente índice

        # Actualizar el scroll final
        self.inner_frame.update_idletasks()
        self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))



# Clases para las otras opciones (por ahora vacías)
class DiccionarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#F5E8D0')

        # Título
        title_label = tk.Label(self, text="Diccionario de Señas", font=('Helvetica', 20, 'bold'),
                               bg='#F5E8D0', fg='#8B4513')
        title_label.pack(pady=20)

        # Frame para la búsqueda
        search_frame = tk.Frame(self, bg='#F5E8D0')
        search_frame.pack(pady=10)

        # Etiqueta y campo de entrada para la búsqueda
        search_label = ttk.Label(search_frame, text="Buscar:", background='#F5E8D0',
                                 font=('Helvetica', 14), foreground='#8B4513')
        search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(search_frame, width=30, font=('Helvetica', 14), style="TEntry")
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Botón de búsqueda
        search_button = ttk.Button(search_frame, text="Buscar", command=self.perform_search,
                                   style="TButton", padding=(5, 5))
        search_button.pack(side=tk.LEFT, padx=5)

        # Índice alfabético
        alphabet_frame = tk.Frame(self, bg='#F5E8D0')
        alphabet_frame.pack(pady=5)

        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

        for letter in alphabet:
            letter_button = tk.Button(alphabet_frame, text=letter, font=('Helvetica', 12),
                                      bg='#D4B897', fg='#8B4513', relief='flat',
                                      command=lambda l=letter: self.scroll_to_letter(l))
            letter_button.pack(side='left', padx=2)

        # Frame para el canvas y scrollbar
        canvas_frame = tk.Frame(self, bg='#F5E8D0')
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas para el diccionario
        self.dict_canvas = tk.Canvas(canvas_frame, bg='#F5E8D0')
        self.dict_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.dict_canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Scrollbar vertical para el canvas del diccionario
        dict_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.dict_canvas.yview)
        dict_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.dict_canvas.configure(yscrollcommand=dict_scrollbar.set)

        # Frame interno donde se colocarán las imágenes y etiquetas
        self.dict_frame = tk.Frame(self.dict_canvas, bg='#F5E8D0')
        self.dict_canvas.create_window((0, 0), window=self.dict_frame, anchor='nw')

        # Ajustar el tamaño del frame interno
        self.dict_frame.bind("<Configure>", self.update_scrollregion)

        # Inicializar el diccionario para las etiquetas de letras
        self.letter_labels = {}

        # Cargar y mostrar todas las imágenes
        self.load_dictionary()


    def on_mouse_wheel(self, event):
            # Desplaza el canvas verticalmente
            self.dict_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_scrollregion(self, event):
        self.dict_canvas.configure(scrollregion=self.dict_canvas.bbox("all"))
   
        
    def load_dictionary(self, search_term=''):
        # Limpiar los widgets existentes
        for widget in self.dict_frame.winfo_children():
            widget.destroy()

        # Convertir el término de búsqueda a minúsculas para una búsqueda insensible a mayúsculas
        search_term = search_term.lower()

        # Diccionario para almacenar las entradas organizadas
        items_dict = defaultdict(lambda: defaultdict(list))

        # Directorios donde se almacenan las imágenes y GIFs
        image_dirs = [('Letras', 'images'), ('Números', 'numbers'), ('Palabras', 'words'), ('Frases', 'phrases')]

        for category, dir_path in image_dirs:
            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    if filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        filepath = os.path.join(dir_path, filename)
                        name = os.path.splitext(filename)[0]
                        # Aplicar filtro de búsqueda
                        if search_term and search_term not in name.lower():
                            continue
                        # Obtener la letra inicial
                        first_letter = name[0].upper()
                        items_dict[category][first_letter].append((name, filepath))

        # Mostrar las entradas organizadas
        self.letter_labels = {}  # Para navegación alfabética
        for category in sorted(items_dict.keys()):
            # Etiqueta de categoría
            category_label = tk.Label(self.dict_frame, text=category, font=('Helvetica', 16, 'bold'),
                                    bg='#F5E8D0', fg='#8B4513')
            category_label.pack(pady=(10, 5))

            for letter in sorted(items_dict[category].keys()):
                # Etiqueta de letra
                letter_label = tk.Label(self.dict_frame, text=letter, font=('Helvetica', 14, 'bold'),
                                        bg='#F5E8D0', fg='#8B4513')
                letter_label.pack(pady=(5, 5))
                self.letter_labels[letter] = letter_label  # Guardar referencia para navegación

                # Mostrar los ítems bajo cada letra
                for name, filepath in sorted(items_dict[category][letter], key=lambda x: x[0]):
                    # Crear un frame para cada ítem
                    item_frame = tk.Frame(self.dict_frame, bg='#F5E8D0', padx=10, pady=5)
                    item_frame.pack(fill='x', padx=20, pady=2)

                    # Etiqueta con el nombre
                    name_label = tk.Label(item_frame, text=name, font=('Helvetica', 12),
                                        bg='#F5E8D0', fg='#8B4513')
                    name_label.pack(side='left', padx=10)

                    # Mostrar la imagen o GIF
                    if filepath.endswith('.gif'):
                        image_label = AnimatedGIF(item_frame, filepath, bg='#F5E8D0')
                        image_label.pack(side='left', padx=10)
                    else:
                        img = Image.open(filepath).convert('RGBA')
                        max_image_height = 90
                        max_image_width = 90
                        img = resize_image(img, max_image_width, max_image_height)
                        img_tk = ImageTk.PhotoImage(img)
                        image_label = tk.Label(item_frame, image=img_tk, bg='#F5E8D0')
                        image_label.image = img_tk  # Mantener referencia
                        image_label.pack(side='left', padx=10)

        # Verificar si no se encontraron resultados
        if not items_dict:
            no_results_label = tk.Label(self.dict_frame, text="No se encontraron resultados.", font=('Helvetica', 14),
                                        bg='#F5E8D0', fg='red')
            no_results_label.pack(pady=20)

        # Actualizar la región de scroll
        self.dict_frame.update_idletasks()
        self.dict_canvas.config(scrollregion=self.dict_canvas.bbox("all"))


    def perform_search(self):
        search_term = self.search_entry.get()
        self.load_dictionary(search_term=search_term)
    
    def scroll_to_letter(self, letter):
        if letter in self.letter_labels:
            target_widget = self.letter_labels[letter]
            self.dict_canvas.update_idletasks()
            # Obtener la posición del widget dentro del canvas
            bbox = self.dict_canvas.bbox(target_widget)
            if bbox:
                y = bbox[1]
                # Calcular la fracción para desplazarse
                content_height = self.dict_frame.winfo_height()
                fraction = y / content_height
                self.dict_canvas.yview_moveto(fraction)




class Opcion3Frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#F5E8D0')
        label = tk.Label(self, text="Opción 3 - En desarrollo", font=('Helvetica', 16), bg='#F5E8D0')
        label.pack(pady=20)

# Inicializar los frames y añadirlos al contenedor
for F in (TraductorFrame, DiccionarioFrame, Opcion3Frame):
    frame_name = F.__name__
    frame = F(parent=container, controller=root)
    frames[frame_name] = frame
    frame.grid(row=0, column=0, sticky="nsew")

# Mostrar el frame inicial (por ejemplo, TraductorFrame)
show_frame("TraductorFrame")

# Crear el menú
menubar = tk.Menu(root)

# Menú principal
menu_principal = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Menú", menu=menu_principal)

# Añadir opciones al menú
menu_principal.add_command(label="Traductor", command=lambda: show_frame("TraductorFrame"))
menu_principal.add_command(label="Diccionario", command=lambda: show_frame("DiccionarioFrame"))
menu_principal.add_command(label="Opción 3", command=lambda: show_frame("Opcion3Frame"))
menu_principal.add_separator()
menu_principal.add_command(label="Salir", command=root.quit)

# Configurar el menú en la ventana
root.config(menu=menubar)

# Ejecutar la aplicación
root.mainloop()
