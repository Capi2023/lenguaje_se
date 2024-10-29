# Link para señas de manos: https://es.hesperian.org/hhg/Disabled_Village_Children:Lenguaje_de_se%C3%B1as

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
from ttkthemes import ThemedTk
import os

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

        history_label = ttk.Label(history_frame, text="Historial de palabras:", background='#F5E8D0', font=('Helvetica', 16), foreground='#8B4513')
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
        self.history_text.configure(state='normal')
        self.history_text.insert('end', f"{index}. {text}\n")
        self.history_text.tag_add(f"item{index}", f"{index}.0", f"{index}.end")
        self.history_text.tag_bind(f"item{index}", "<Button-1>", lambda event, t=text: self.on_history_click(t))
        self.history_text.tag_configure(f"item{index}", foreground="#8B4513")
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

        words = text.split()  # Divide el texto en palabras

        # Definir tamaño máximo para las imágenes
        max_image_height = 90  # Ajusta este valor según tus necesidades
        max_image_width = 90   # Ajusta este valor según tus necesidades

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
                        continue  # Saltar espacios en blanco
                    elif letter in symbols_not_used:
                        # Mostrar advertencia en la interfaz gráfica
                        warning_message = f"El símbolo '{letter}' no se usa en el lenguaje de señas."
                        word_images.append((warning_message, 'warning'))
                        continue  # Continuar con las otras letras sin detener el flujo
                    elif letter == "?":  # Condición especial para el signo de interrogación
                        # Mapea "?" al archivo de imagen alternativo
                        question_image_path_gif = "images/question_mark.gif"
                        question_image_path_png = "images/question_mark.png"

                        if os.path.exists(question_image_path_gif):
                            word_images.append((question_image_path_gif, 'gif'))
                        elif os.path.exists(question_image_path_png):
                            word_images.append((question_image_path_png, 'png'))
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
            word_frame = tk.Frame(self.inner_frame, bg='#F5E8D0', bd=2, relief='solid', padx=10, pady=10, highlightbackground='#A97C50')
            word_frame.pack(fill='x', pady=10)  # Añadir separación entre grupos

            # Cambiar el color de las palabras o letras mostradas
            word_label = tk.Label(word_frame, text=word, bg='#F5E8D0', font=('Helvetica', 14, 'bold'), fg='#8B4513')
            word_label.pack(pady=(0, 5))  # Colocar la palabra arriba con un pequeño margen

            # Crear un sub-contenedor para las imágenes que se centrará
            images_frame = tk.Frame(word_frame, bg='#F5E8D0')
            images_frame.pack(anchor='center')  # Centrar el contenedor de las imágenes

            # Redimensionar imágenes y colocarlas en el sub-contenedor centrado
            for img_path, img_type in word_images:
                if img_type == 'gif':
                    # Manejar GIFs animados
                    label = AnimatedGIF(images_frame, img_path, bg='#F5E8D0')
                    label.pack(side='left', padx=5, pady=5)
                elif img_type == 'png':
                    # Cargar y redimensionar imágenes
                    img = Image.open(img_path).convert('RGBA')
                    img = resize_image(img, max_image_width, max_image_height)
                    img_tk = ImageTk.PhotoImage(img)
                    label = tk.Label(images_frame, image=img_tk, bg='#F5E8D0')
                    label.image = img_tk  # Evita que la imagen se elimine
                    label.pack(side='left', padx=5, pady=5)
                elif img_type == 'warning':
                    # Cambiar el color de advertencias
                    warning_label = tk.Label(images_frame, text=img_path, fg='red', bg='#F5E8D0', font=('Helvetica', 12, 'bold'))
                    warning_label.pack(side='left', padx=5, pady=5)

            # Ajustar el tamaño del inner_frame para el scroll
            self.inner_frame.update_idletasks()
            self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))

        # Ajustar el tamaño del inner_frame para el scroll
        self.inner_frame.update_idletasks()
        self.image_canvas.config(scrollregion=self.image_canvas.bbox("all"))

# Clases para las otras opciones (por ahora vacías)
class DiccionarioFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.configure(bg='#F5E8D0')

        # Título
        title_label = tk.Label(self, text="Diccionario de Señas", font=('Helvetica', 20, 'bold'), bg='#F5E8D0', fg='#8B4513')
        title_label.pack(pady=20)

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

        # Cargar y mostrar todas las imágenes
        self.load_dictionary()

    def on_mouse_wheel(self, event):
            # Desplaza el canvas verticalmente
            self.dict_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_scrollregion(self, event):
        self.dict_canvas.configure(scrollregion=self.dict_canvas.bbox("all"))

    def load_dictionary(self):
        # Obtener listas de archivos de imágenes y GIFs
        image_files = []
        gif_files = []

        # Directorios donde se almacenan las imágenes y GIFs
        image_dirs = [('Letras', 'images'), ('Palabras/Frases', 'words')]

        for category, dir_path in image_dirs:
            if os.path.exists(dir_path):
                for filename in os.listdir(dir_path):
                    if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg'):
                        image_files.append((filename, os.path.join(dir_path, filename), category))
                    elif filename.endswith('.gif'):
                        gif_files.append((filename, os.path.join(dir_path, filename), category))

        # Combinar las listas y ordenar alfabéticamente
        all_files = image_files + gif_files
        all_files.sort(key=lambda x: x[0])

        # Mostrar cada imagen con su etiqueta correspondiente
        for filename, filepath, category in all_files:
            # Obtener el nombre sin extensión
            name = os.path.splitext(filename)[0]

            # Crear un frame para cada elemento
            item_frame = tk.Frame(self.dict_frame, bg='#F5E8D0', padx=10, pady=10)
            item_frame.pack(fill='x', padx=10, pady=5)

            # Etiqueta con el nombre
            name_label = tk.Label(item_frame, text=f"{name} ({category})", font=('Helvetica', 14), bg='#F5E8D0', fg='#8B4513')
            name_label.pack(side='left', padx=10)

            # Mostrar la imagen o GIF
            if filename.endswith('.gif'):
                image_label = AnimatedGIF(item_frame, filepath, bg='#F5E8D0')
                image_label.pack(side='left', padx=10)
            else:
                # Cargar y redimensionar la imagen
                img = Image.open(filepath).convert('RGBA')
                max_image_height = 90
                max_image_width = 90
                img = resize_image(img, max_image_width, max_image_height)
                img_tk = ImageTk.PhotoImage(img)
                image_label = tk.Label(item_frame, image=img_tk, bg='#F5E8D0')
                image_label.image = img_tk  # Mantener referencia
                image_label.pack(side='left', padx=10)


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
