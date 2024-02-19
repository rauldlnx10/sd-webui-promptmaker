import gradio as gr
import os
import datetime
import random
import json

current_path = os.path.dirname(__file__)
parent_path = os.path.dirname(current_path)
directory = os.path.join(parent_path, "groups")
files = os.listdir(directory)

def read_elements(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def load_groups(directory):
    json_files = [file for file in os.listdir(directory) if file.lower().endswith('.json')]
    return {file: read_elements(os.path.join(directory, file)) for file in json_files}

def select_group(selected_file):
    groups_file = os.path.join(directory, selected_file)
    with open(groups_file, 'r') as f:
        return json.load(f)
    return  update_dropdown_choices(groups_data)

def update_dropdown_choices(groups_data):
    return [gr.Dropdown(choices=group, label=key.capitalize()) for key, group in groups_data.items()]


def generate_sentence(subjects, groups_data, order, *args):
    sentence = ""
    random_elements = [random.choice(arg.split(';')) for arg in args if arg]

    if random_elements and "Quality" in order:
        quality_index = order.index("Quality")
        quality_element = random_elements[quality_index]
        sentence += quality_element + ", "

        if "Type" in order:
            type_index = order.index("Type")
            type_element = random_elements[type_index]
            sentence += type_element + " "

            if subjects:
                sentence += subjects + " wearing a "

            for element in random_elements:
                if element != quality_element and element != type_element:
                    sentence += element + ", "

    sentence = sentence.strip(", ")
    return sentence

def randomize_elements():
    while True:
        random_elements = []
        try:
            for group_key in order:
                group = groups_data[group_key]
                random_element = random.choice(group)
                while random_element == "":
                    random_element = random.choice(group)
                random_elements.append(random_element)
            return tuple(random_elements)
        except IndexError:
            continue
    return tuple(random_elements)

def save_history_to_file(history):
    desktop_path = os.path.expanduser("~/Desktop")
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = os.path.join(desktop_path, f"prompt_history_{timestamp}.txt")

    with open(filename, 'w') as file:
        file.writelines(f"{item}\n" for item in history)
        
    return f"Saved to {filename}"


def show_history():
    history_text = "\n".join(history)
    return f"""
        <div style="border: 1px solid #ccc; padding: 10px; max-height: 700px; overflow-y: auto; font-size: 14px;">
            <ul style="list-style-type: none; padding-left: 0;">
                {"".join(f"<li style='border-bottom: 0px solid #ccc; padding-bottom: 5px;'>{item}</li>" for item in history)}
            </ul>
        </div>
        """

def save_history_to_file():
    desktop_path = os.path.expanduser("~/Desktop")  # Obtiene la ruta al escritorio del usuario
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # Agrega una marca de tiempo única
    filename = os.path.join(desktop_path, f"prompt_history_{timestamp}.txt")
    with open(filename, "w") as file:
        for item in history:
            file.write(item + "\n")
    return gr.Info(f"Saved to {filename}") 

def clear_history():
    global history
    history = [] 
    return ""

def handle_generation(subjects, *dropdown_values):
    sentence = generate_sentence(subjects, groups_data, order, *dropdown_values)
    history.append(sentence)
    return sentence, history  # Return both sentence and updated history

groups = load_groups(directory)

def create_prompting_ui(directory, groups, prompt):
    global groups_data
    groups_data = load_groups(directory)  # Load groups initially
    order = list(groups_data.keys())
    history = []
    files = list(groups.keys())

    with gr.Blocks() as prompting_ui:
        with gr.Tab("Prompting"):
            selected_file = gr.Radio(choices=files, value="Normal.json", label="Select JSON File")
            txt_subjects = gr.Textbox(label="Input a Subject", show_label=True, lines=1)
            prompt = prompt  
            inputs = update_dropdown_choices(groups_data)

            with gr.Accordion("Manual Settings:", open=False):
                for group_name in order:
                    inputs.append(gr.Dropdown(choices=groups_data[group_name], label=group_name.capitalize()))

            btn_randomize = gr.Button(value="Randomize", variant="secondary")
            btn_generate = gr.Button(value="Generate", variant="primary")


            selected_file.change(
                fn=select_group,
                inputs=selected_file,
                outputs=inputs   # Assign to your 'inputs' variable representing the dropdowns
            )

            btn_randomize.click(
                fn=randomize_elements, 
                inputs=[txt_subjects] + inputs,
                outputs=[prompt]
            )

            btn_generate.click(
                fn=handle_generation, 
                inputs=[txt_subjects] + inputs,
                outputs=[prompt]
            )
            
    return prompting_ui


