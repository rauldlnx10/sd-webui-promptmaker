import random
import gradio as gr
import modules.scripts as scripts
from modules import ui
from modules import shared
from modules import script_callbacks
import os
import datetime
import sys
import pyperclip

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

def read_elements(filename):
    with open(filename, "r") as f:
        elements = f.read().strip()
        elements = elements.split(";")
    return elements

current_path = os.path.dirname(__file__)
parent_path = os.path.dirname(current_path)
directory = os.path.join(parent_path, "groups")
files = os.listdir(directory)
order = [
    "Quality", 
    "Type", 
    "Input text", 
    "Clothes", 
    "Places", 
    "Position", 
    "Hair", 
    "Hair Color",
    "Expression", 
    "Face", 
    "Lips", 
    "Eye Color", 
    "Make Up", 
    "Looking At", 
    "Lighting", 
    "Angles", 
    "Camera", 
    "Others"
]

files.sort(key=lambda x: order.index(x.split(".")[0]))

groups = []
group_names = []
history = []

for file in files:
    filename = os.path.join(directory, file)
    group = read_elements(filename)
    groups.append(group)
    group_name = file.split(".")[0]
    group_names.append(group_name)

def generate_sentence(subjects, *args):
    sentence = ""

    random_elements = []
    for i in range(len(args)):
        selected_items = args[i] 
        group = groups[i]

        if selected_items:
            items = selected_items.split(';')
            random_element = random.choice(items)
            random_elements.append(random_element)

    if random_elements:
        quality_index = order.index("Quality")
        quality_element = random_elements[quality_index]
        sentence += quality_element + ", "
        type_index = order.index("Type")
        type_element = random_elements[type_index]
        sentence += type_element + " "
        if subjects:
            sentence += subjects + ", "
        for i in range(len(random_elements)):
            if i != quality_index and i != type_index:
                sentence += random_elements[i]
                if i < len(random_elements) - 1 and random_elements[i] != "Clothes":  
                    sentence += ", "
    history_result = sentence 
    history.append(f" {history_result}")
    return f"## " + f"{sentence}"

def randomize_elements(group):
    while True:  # Comienza un bucle infinito
        random_elements = []
        try:
            for group in groups:
                random_element = random.choice(group)
                random_elements.append(random_element)
            return tuple(random_elements)  # Si todos los grupos tienen al menos un elemento, devuelve los elementos seleccionados
        except IndexError:  # Si algún grupo está vacío, IndexError será lanzado
            continue  # Si algún grupo está vacío, vuelve al principio del bucle y lo 
    return tuple(random_elements)

def copy_prompt_to_clipboard(text):
    text = text.lstrip('## ')
    gr.Info("Prompt copied to clipboard")
    pyperclip.copy(text)

def show_history():
    history_text = "\n".join(history)
    return f"{history_text}\n"

def save_history_to_file():
    desktop_path = os.path.expanduser("~/Desktop")  # Obtiene la ruta al escritorio del usuario
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # Agrega una marca de tiempo única
    filename = os.path.join(desktop_path, f"prompt_history_{timestamp}.txt")

    with open(filename, "w") as file:
        for item in history:
            file.write(item + "\n")

    gr.Info(f"History saved to {filename}")

def clear_history():
    history_text = ""
    return f""

with gr.Blocks(layout="1-3") as interface:
    with gr.Tab("Prompting"):
        with gr.Row(variant="panel"):
            txt_subjects = gr.Textbox(label="Input Text", show_label=True, lines=1, variant="panel")

        inputs_left = []   
        inputs_center = [] 
        inputs_right = []  

        with gr.Accordion("Options:", scale=0.7):
            with gr.Row():
                btn_randomize = gr.Button(value="Randomize", variant="secondary")
            with gr.Row(variant="panel"):
                with gr.Column():
                    for file, group_name in zip(files[:len(files)//3], group_names[:len(group_names)//3]):
                        filename = os.path.join(directory, file)
                        group = read_elements(filename)
                        inputs_left.append(gr.Dropdown(choices=group, label=group_name.capitalize()))
                        
                with gr.Column():
                    for file, group_name in zip(files[len(files)//3:2*len(files)//3], group_names[len(group_names)//3:2*len(group_names)//3]):
                        filename = os.path.join(directory, file)
                        group = read_elements(filename)
                        inputs_center.append(gr.Dropdown(choices=group, label=group_name.capitalize()))

                with gr.Column():
                    for file, group_name in zip(files[2*len(files)//3:], group_names[2*len(group_names)//3:]):
                        filename = os.path.join(directory, file)
                        group = read_elements(filename)
                        inputs_right.append(gr.Dropdown(choices=group, label=group_name.capitalize()))
        
            with gr.Column(variant="compact"):
                with gr.Row():
                    btn_generate = gr.Button(value="📄 Generate", variant="primary", scale=0.2)
                    copy_prompt = gr.Button("Copy", scale=0)
                    txt_result = gr.Markdown(label="Generated Prompt:")

    
    with gr.Tab("History"):
        with gr.Row():
            clear_history_button = gr.Button("🗑️ Clear History", variant="stop", scale=0)
            save_history_button = gr.Button("Save History to File", scale=0)
        with gr.Row():
            history_display = gr.Markdown("")

        txt_result.change(show_history, None, history_display)  # Actualizar el componente de historial
        btn_randomize.click(randomize_elements, outputs=inputs_left + inputs_center + inputs_right)
        btn_generate.click(generate_sentence, inputs=[txt_subjects] + inputs_left + inputs_center + inputs_right, outputs=[txt_result])
        copy_prompt.click(copy_prompt_to_clipboard, inputs=txt_result, outputs=None)
        clear_history_button.click(clear_history, None, history_display)
        save_history_button.click(save_history_to_file)

script = Script()
script_callbacks.on_ui_tabs(script.on_ui_tabs)
