import os

import tkinter
import customtkinter

from utils.translator import convert_language_to_code, deepl_translate
from utils.utils import clear_queue

class LangNetUIMessage:
    def __init__(self):
        self.text = None
        self.translation = None

class LangNetUI: 
    def __init__(self):
        self.load_pressed = False

        self.model_queue = None
        self.load_event = None
        self.language_queue = None
        self.translation_queue = None
        self.clear_event = None
        self.text_queue = None
        
        self.model_combobox = None
        self.language_combobox = None
        self.deepl_api_key_textbox = None
        self.deepl_language_combobox = None

        self.subtitles = ['']
        self.messages = dict()

    def run(self, model_queue, load_event, language_queue, translation_queue, clear_event, text_queue):
        self.model_queue = model_queue
        self.load_event = load_event
        self.language_queue = language_queue
        self.translation_queue = translation_queue
        self.clear_event = clear_event
        self.text_queue = text_queue

        customtkinter.set_appearance_mode("light") # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("dark-blue") # Themes: blue (default), dark-blue, green

        app = customtkinter.CTk()
        app.geometry("900x600")
        app.title("LangNet 1.0")
        app.resizable(False, False)

        # Create a frame for the left panel
        settings_frame = customtkinter.CTkFrame(app, width=200)
        settings_frame.place(relx=0.0, rely=0.0, relwidth=0.2, relheight=1.0)

        model_combobox_label = customtkinter.CTkLabel(settings_frame, text="Model (Restart Required)", justify=tkinter.LEFT)
        model_combobox_label.place(relx=0.05, rely=0.025, anchor=tkinter.W)

        self.model_combobox = customtkinter.CTkOptionMenu(settings_frame, width=165, state="readonly")
        self.model_combobox.place(relx=0.5, rely=0.07, anchor=tkinter.CENTER)
        self.model_combobox.configure(values=["tiny (~1GB VRAM)", "base (~1GB VRAM)", "small (~2GB VRAM)", "medium (~5GB VRAM)", "large (~10GB VRAM)"])
        self.model_combobox.set("small (~2GB VRAM)")

        # Load button
        load_button = customtkinter.CTkButton(settings_frame, text="Load", width=165)
        load_button.place(relx=0.5, rely=0.125, anchor=tkinter.CENTER)
        load_button.configure(command=self.load_model)

        # Language combobox label
        language_combobox_label = customtkinter.CTkLabel(settings_frame, text="Language (Restart Required)", justify=tkinter.LEFT)
        language_combobox_label.place(relx=0.05, rely=0.2, anchor=tkinter.W)

        # Language combobox
        self.language_combobox = customtkinter.CTkOptionMenu(settings_frame, width=165, state="readonly")
        self.language_combobox.place(relx=0.5, rely=0.245, anchor=tkinter.CENTER)
        self.language_combobox.configure(values=["Auto", "English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Chinese", "Japanese", "Korean"])
        self.language_combobox.set("English")
        self.language_combobox.configure(command=self.language_combobox_callback)
        self.language_queue.put("English")

        # Translation combobox label
        translation_combobox_label = customtkinter.CTkLabel(settings_frame, text="Translation (Restart Required)", justify=tkinter.LEFT)
        translation_combobox_label.place(relx=0.05, rely=0.32, anchor=tkinter.W)

        # Translation combobox
        translation_combobox = customtkinter.CTkOptionMenu(settings_frame, width=165, state="readonly")
        translation_combobox.place(relx=0.5, rely=0.365, anchor=tkinter.CENTER)
        translation_combobox.configure(values=["None", "Whisper (English)", "DeepL"])
        translation_combobox.set("DeepL")
        translation_combobox.configure(command=self.translation_combobox_callback)
        self.translation_queue.put("DeepL")

        # DeepL API key label
        deepl_api_key_label = customtkinter.CTkLabel(settings_frame, text="DeepL API Key", justify=tkinter.LEFT)
        deepl_api_key_label.place(relx=0.05, rely=0.44, anchor=tkinter.W)

        # DeepL API key textbox
        self.deepl_api_key_textbox = customtkinter.CTkEntry(settings_frame, width=165)
        self.deepl_api_key_textbox.place(relx=0.5, rely=0.485, anchor=tkinter.CENTER)

        self.load_api_key()

        # DeepL languge combobox label
        deepl_language_combobox_label = customtkinter.CTkLabel(settings_frame, text="DeepL Language", justify=tkinter.LEFT)
        deepl_language_combobox_label.place(relx=0.05, rely=0.535, anchor=tkinter.W)

        # DeepL language combobox
        self.deepl_language_combobox = customtkinter.CTkOptionMenu(settings_frame, width=165, state="readonly")
        self.deepl_language_combobox.place(relx=0.5, rely=0.58, anchor=tkinter.CENTER)
        self.deepl_language_combobox.configure(values=["English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Chinese", "Japanese", "Korean"])
        self.deepl_language_combobox.set("Japanese")

        # Clear button
        clear_button = customtkinter.CTkButton(settings_frame, text="Clear", width=165)
        clear_button.place(relx=0.5, rely=0.96, anchor=tkinter.CENTER)
        clear_button.configure(command=self.clear_textbox)

        # Create a frame for the right side (text and translations)
        right_frame = customtkinter.CTkFrame(app)
        right_frame.place(relx=0.2, rely=0.0, relwidth=0.8, relheight=1.0)

        self.font = customtkinter.CTkFont(family="Yu Gothic UI", size=12)

        self.output_textbox = customtkinter.CTkTextbox(right_frame, font=self.font, text_color="blue", wrap=tkinter.WORD)
        self.output_textbox.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=0.5)

        self.translation_textbox = customtkinter.CTkTextbox(right_frame, font=self.font, text_color="red", wrap=tkinter.WORD)
        self.translation_textbox.place(relx=0.0, rely=0.5, relwidth=1.0, relheight=0.5)

        self.update_output_textbox()
        self.update_translation_textbox()

        app.mainloop()

    def load_api_key(self):
        if os.path.exists("save/api_key.txt"):
            with open("save/api_key.txt", "r") as f:
                api_key = f.read()
                self.deepl_api_key_textbox.insert(0, api_key)

    def save_api_key(self):
        api_key = self.deepl_api_key_textbox.get()
        with open("save/api_key.txt", "w") as f:
            f.write(api_key)

    def translation_combobox_callback(self, value):
        # print("Translation callback: " + value)
        self.translation_queue.put(value)

    def language_combobox_callback(self, value):
        clear_queue(self.language_queue)
        # print("Language callback: " + value)
        self.language_queue.put(value)

    def load_model(self):
        model = self.model_combobox.get()
        model = model.split(" ")[0]
        model = model.replace(" ", "")
        self.model_queue.put(model)

        if not self.load_pressed:
            self.load_event.set()
            self.load_pressed = True

    def clear_textbox(self):
        self.output_textbox.delete("1.0", "end")
        self.translation_textbox.delete("0.0", "end")

        self.subtitles = ['']
        self.messages.clear()
        self.clear_event.set()

    def update_translation_textbox(self):
        self.translation_textbox.delete("1.0", "end")

        api_key = self.deepl_api_key_textbox.get()
        self.save_api_key()

        original_language = self.language_combobox.get()
        original_language = convert_language_to_code(original_language)

        target_language = self.deepl_language_combobox.get()
        target_language = convert_language_to_code(target_language)

        for i in range(len(self.messages)):
            message = self.messages[i]
            text = message.text
            translation = message.translation
            if translation is None:
                formated_text = text
                if formated_text.startswith("[NEW]"):
                    formated_text = formated_text[5:]

                if formated_text == "" or formated_text == " " or formated_text == "\n":
                    continue

                translated_text = deepl_translate(formated_text, api_key=api_key, original_language=original_language, target_language=target_language)
                if not translated_text == "" and not translated_text == " " and not translated_text == "\n":
                    if translated_text.startswith(" "):
                        translated_text = translated_text[1:]

                    formated_text = translated_text + " (" + text + ")"
                    if text.startswith("[NEW]"):
                        formated_text = "[NEW] " + formated_text

                    self.translation_textbox.insert("end", formated_text + "\n\n")
                    self.messages[i].translation = translated_text
            else:
                formated_text = text
                if formated_text.startswith("[NEW]"):
                    formated_text = formated_text[5:]

                translated_text = translation
                if translated_text.startswith(" "):
                    translated_text = translated_text[1:]

                formated_text = translated_text + " (" + text + ")"
                if text.startswith("[NEW]"):
                    formated_text = "[NEW] " + formated_text

                self.translation_textbox.insert("end", formated_text + "\n\n")

        self.translation_textbox.see("end")
        self.translation_textbox.after(2000, self.update_translation_textbox)

    def update_output_textbox(self):
        self.output_textbox.delete("1.0", "end")
   
        paragraphs = []
        
        while not self.text_queue.empty():
            self.subtitles = self.text_queue.get()

        if not len(self.subtitles) == 0:
            for i in range(len(self.subtitles)):
                sentence = self.subtitles[i]
                if sentence == "" or sentence == " " or sentence == "\n":
                    continue
                if i == len(self.subtitles) - 1:
                    sentence = "[NEW] " + sentence

                paragraphs.append(sentence)
                self.output_textbox.insert(tkinter.INSERT, sentence + "\n" + "\n")

        for i in range(len(paragraphs)):
            if not i in self.messages:
                if paragraphs[i] == "" or paragraphs[i] == " " or paragraphs[i] == "\n":
                    continue

                message = LangNetUIMessage()
                message.text = paragraphs[i]
                message.translation = None
                self.messages[i] = message
                # print("Added message in messages: " + self.messages[i].text)
            else:
                # If the paragraph has changed
                if not self.messages[i].text == paragraphs[i]:
                    # Update the message
                    self.messages[i].text = paragraphs[i]
                    self.messages[i].translation = None
                    # print("Updated message in messages: " + self.messages[i].text)

        self.output_textbox.see("end")
        self.output_textbox.after(1000, self.update_output_textbox)

lang_net_ui = LangNetUI()