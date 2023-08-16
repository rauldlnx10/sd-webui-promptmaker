import random
import gradio as gr
import modules.scripts as scripts
from modules import script_callbacks
from modules import generation_parameters_copypaste as params_copypaste
import os
import sys

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
    "Expresion", 
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

for file in files:
    filename = os.path.join(directory, file)
    group = read_elements(filename)
    groups.append(group)
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
            sentence += subjects + " wearing a "
        for i in range(len(random_elements)):
            if i != quality_index and i != type_index:
                sentence += random_elements[i]
                if i < len(random_elements) - 1 and random_elements[i] != "Clothes":  
                    sentence += ", "
    return sentence

def randomize_elements():
    random_elements = []
    for group in groups: 
        random_element = random.choice(group) 
        random_elements.append(random_element) 
    return tuple(random_elements)

with gr.Blocks(layout="1-3") as interface:
    with gr.Row(variant="compact"):
        txt_subjects = gr.Textbox(label="Subject: (Ex: a caucasian woman)", lines=2)

    inputs_left = []   
    inputs_center = [] 
    inputs_right = []  

    with gr.Row(variant="compact"):
        with gr.Column(variant="compact"):
            for file, group_name in zip(files[:len(files)//3], group_names[:len(group_names)//3]):
                filename = os.path.join(directory, file)
                group = read_elements(filename)
                inputs_left.append(gr.Dropdown(choices=group, label=group_name.capitalize(), multiselect=True))
                
        with gr.Column(variant="compact"):
            for file, group_name in zip(files[len(files)//3:2*len(files)//3], group_names[len(group_names)//3:2*len(group_names)//3]):
                filename = os.path.join(directory, file)
                group = read_elements(filename)
                inputs_center.append(gr.Dropdown(choices=group, label=group_name.capitalize(), multiselect=True))

        with gr.Column(variant="compact"):
            for file, group_name in zip(files[2*len(files)//3:], group_names[2*len(group_names)//3:]):
                filename = os.path.join(directory, file)
                group = read_elements(filename)
                inputs_right.append(gr.Dropdown(choices=group, label=group_name.capitalize(), multiselect=True))

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
            btn_randomize.click(randomize_elements, outputs=inputs_left + inputs_center + inputs_right)

    with gr.Row(variant="compact"):
        btn_generate = gr.Button(value="Generate", variant="primary")
        btn_generate.click(generate_sentence, inputs=[txt_subjects] + inputs_left + inputs_center + inputs_right, outputs=[txt_result])

script = Script()
script_callbacks.on_ui_tabs(script.on_ui_tabs)
