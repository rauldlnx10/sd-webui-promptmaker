import random
import gradio as gr
import modules.scripts as scripts
from modules import script_callbacks
from modules import generation_parameters_copypaste as params_copypaste
import os
import sys

def read_elements(filename):
    # Abrir el archivo en modo lectura
    with open(filename, "r") as f:
        # Leer el contenido del archivo y eliminar el salto de línea final
        elements = f.read().strip()
        # Separar los elementos por punto y coma y guardarlos en una lista
        elements = elements.split(";")
    # Devolver la lista de elementos
    return elements

# Obtener la ruta de la carpeta actual
current_path = os.path.dirname(__file__)

# Obtener la ruta de la carpeta anterior
parent_path = os.path.dirname(current_path)

# Unir la ruta de la carpeta anterior con la carpeta "groups"
directory = os.path.join(parent_path, "groups")

# Obtener la lista de archivos de texto en el directorio
files = os.listdir(directory)

# Definir una lista con el orden deseado de los grupos
order = ["Quality", "Type", "Input text", "Clothes", "Places", "Position", "Hair", "Hair Color","Expresion", "Face", "Lips", "Eye Color", "Make Up", "Looking At", "Lighting", "Angles", "Camera", "Others"]

# Ordenar la lista de archivos de texto según el orden de la lista anterior
files.sort(key=lambda x: order.index(x.split(".")[0]))

# Definir una lista vacía para guardar los grupos de elementos
groups = []

# Definir una lista vacía para guardar los nombres de los grupos
group_names = []

# Recorrer cada archivo de texto y leer sus elementos con la función read_elements
for file in files:
    # Obtener el nombre completo del archivo con su ruta
    filename = os.path.join(directory, file)
    # Leer los elementos del archivo y guardarlos en la lista groups
    group = read_elements(filename)
    groups.append(group)
    # Obtener el nombre del grupo a partir del nombre del archivo y guardarlo en la lista group_names
    group_name = file.split(".")[0]
    group_names.append(group_name)

class Script(scripts.Script):
    def __init__(self) -> None:
        super().__init__()

    def title(self):
        return "Prompt Maker"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        return ()
    
    def on_ui_tabs(self):
        return [(interface, "Prompt Maker", "prompt_gen")]

def generate_sentence(subjects, *args):
    sentence = ""

    random_elements = []
    for i in range(len(args)):
        selected_items = args[i]  # Cada argumento es una lista de elementos seleccionados

        group = groups[i]  # Obtener el grupo correspondiente

        if selected_items:
            items = selected_items.split(';')
            random_element = random.choice(items)  # Seleccionar un elemento aleatorio de los seleccionados
            random_elements.append(random_element)  # Agregar el elemento a la lista

    if random_elements:
        # Buscar el índice del grupo Quality en la lista order
        quality_index = order.index("Quality")
        # Buscar el elemento que corresponde al grupo Quality en la lista random_elements
        quality_element = random_elements[quality_index]
        # Poner el elemento Quality al principio de la frase
        sentence += quality_element + ", "
        # Buscar el índice del grupo Type en la lista order
        type_index = order.index("Type")
        # Buscar el elemento que corresponde al grupo Type en la lista random_elements
        type_element = random_elements[type_index]
        # Poner el elemento Type después del Quality
        sentence += type_element + " "
        if subjects:
            sentence += subjects + " wearing a "  # Agregar el input text sin coma y separado por un espacio
        for i in range(len(random_elements)):  # Recorrer los elementos restantes
            if i != quality_index and i != type_index:  # Si el elemento no es el del grupo Quality ni el del grupo Type
                sentence += random_elements[i]  # Agregar el elemento
                if i < len(random_elements) - 1 and random_elements[i] != "Clothes":  # Si el elemento no es el último y no es el grupo clothes
                    sentence += ", "  # Agregar una coma y un espacio
    return sentence


def randomize_elements():
    random_elements = []
    for group in groups:  # Recorrer cada grupo de elementos
        random_element = random.choice(group)  # Seleccionar un elemento aleatorio del grupo
        random_elements.append(random_element)  # Agregar el elemento a la lista
    return tuple(random_elements)  # Devolver una tupla con los elementos aleatorios



with gr.Blocks(layout="1-3") as interface:
    with gr.Row(variant="compact"):
        txt_subjects = gr.Textbox(label="Subject: (Ex: a caucasian woman)", lines=2)
    with gr.Row(variant="compact"):
        inputs = []
        for file, group_name in zip(files, group_names):
            # Obtener el nombre completo del archivo con su ruta
            filename = os.path.join(directory, file)
            # Leer los elementos del archivo y guardarlos en la lista group
            group = read_elements(filename)
            # Crear un Dropdown con las opciones del archivo actual
            inputs.append(gr.Dropdown(choices=group, label=group_name.capitalize(), multiselect=False))

    with gr.Row(variant="compact"):
        txt_result = gr.Textbox(label="Generated Prompt:", lines=3)
        
    with gr.Row(variant="compact"):
        with gr.Column(variant="compact"):
            button_txt2img = params_copypaste.create_buttons(["txt2img"])
            params_copypaste.bind_buttons(button_txt2img, None, txt_result)
        with gr.Column(variant="compact"):
            button_img2img = params_copypaste.create_buttons(["img2img"])
            params_copypaste.bind_buttons(button_img2img, None, txt_result)            
        with gr.Column(variant="compact"):
            btn_randomize = gr.Button(value="Randomize", variant="secondary")
            btn_randomize.click(randomize_elements, outputs=inputs)
    with gr.Row(variant="compact"):
        btn_generate = gr.Button(value="Generate", variant="primary")
        btn_generate.click(generate_sentence, inputs=[txt_subjects] + inputs, outputs=[txt_result])            




# Crear un objeto de la clase Script
script = Script()

script_callbacks.on_ui_tabs(script.on_ui_tabs)
