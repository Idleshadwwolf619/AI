# Import necessary libraries
import os
import tkinter as tk
from tkinter import scrolledtext
from llama_cpp import Llama
import random
import datetime
import speech_recognition as sr
import pyttsx3

# Global variables
model_path = "llama-2-7b-chat.Q5_K_M.gguf"
version = "1.00"

# Function to load the language model
def load_model():
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"ERROR: The model path is not valid! Please check the path in the main.py file.")

    # Generate a random seed for the model
    seed = random.randint(1, 2**31)
    # Create and return a Llama language model
    return Llama(model_path=model_path, seed=seed)

# Function to generate a response from the model
def generate_response(model, input_tokens, prompt_input_text, text_area_display, engine):
    # Display user input in the text area
    text_area_display.insert(tk.INSERT, f'\n\nUser: {prompt_input_text}\n')
    # Display chatbot prompt in the text area
    text_area_display.insert(tk.INSERT, "\n\nPikaPikaOver9000: ")

    # Initialize an empty response string
    response_text = ""
    # Generate response tokens from the model
    for token in model.generate(input_tokens, top_k=40, top_p=0.95, temp=0.72, repeat_penalty=1.1):
        try:
            # Decode the token and append to the response text
            response_text = model.detokenize([token]).decode('utf-8', errors='replace')
        except UnicodeDecodeError as e:
            # Handle decoding errors by replacing invalid characters
            print(f"UnicodeDecodeError: {e}")
            response_text = "�"  # Replace invalid characters with the Unicode replacement character

        # Display the response text in the text area
        text_area_display.insert(tk.INSERT, response_text)
        # Update the tkinter window
        root.update_idletasks()

        # Break the loop when the end of the sequence is reached
        if token == model.token_eos():
            break

    # Speak the response using the text-to-speech engine
    engine.say(response_text)
    engine.runAndWait()

# Function to handle sending user-typed messages
def send_message(model, text_area_main_user_input, text_area_display, engine):
    # Get user input from the text area
    user_prompt_input_text = text_area_main_user_input.get('1.0', 'end-1c').strip()
    # Encode the user input
    byte_message = user_prompt_input_text.encode('utf-8')

    # Tokenize the user input for the model
    input_tokens = model.tokenize(b"### Human: " + byte_message + b"\n ### Assistant: ")
    print("Input tokens: ", input_tokens)

    # Generate and display the response
    generate_response(model, input_tokens, user_prompt_input_text, text_area_display, engine)
    # Clear the user input text area
    text_area_main_user_input.delete('1.0', 'end')

# Function to define the chatbot's personality and responses
def chatbot_personality(user_input):
    # Example of simple keyword-based responses
    if "hello" in user_input.lower():
        return "Hello! How can I help you today?"
    elif "how are you" in user_input.lower():
        return "I'm doing well, thank you for asking!"
    elif "bye" in user_input.lower():
        return "Goodbye! Have a great day!"
    else:
        # Default response for unrecognized input
        return "I'm not sure how to respond to that. Can you ask me something else?"

# Function to handle speech input
def speech_input(text_area_main_user_input, recognizer, microphone, text_area_display, engine):
    # Clear the text area for user input
    text_area_main_user_input.delete('1.0', 'end')

    try:
        # Adjust for ambient noise and listen for speech input
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            text_area_display.insert(tk.INSERT, "\nListening...")
            audio = recognizer.listen(source, timeout=5)
        print("Processing...")
        text_area_display.insert(tk.INSERT, "\nProcessing...")

        # Recognize speech using Google's speech recognition service
        user_input = recognizer.recognize_google(audio)
        print("You said:", user_input)
        # Display the recognized speech in the text area
        text_area_main_user_input.insert(tk.INSERT, user_input)

        # Process the user input and get the chatbot's response
        response = chatbot_personality(user_input)
        text_area_display.insert(tk.INSERT, f"\n\nPikaPikaOver9000: {response}")
        # Speak the response using the text-to-speech engine
        engine.say(response)
        engine.runAndWait()

    except sr.UnknownValueError:
        print("Could not understand audio")
        text_area_display.insert(tk.INSERT, "\nCould not understand audio")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service; {e}")
        text_area_display.insert(tk.INSERT, f"\nError with the speech recognition service; {e}")

# Main function to set up the GUI and run the application
def main():
    # Load the language model
    model = load_model()

    # Initialize the speech recognition components
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    # Initialize the text-to-speech engine
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)

    # Create the main tkinter window
    global root
    root = tk.Tk()
    root.title(f"The Pika Pika 9000 -v{version} - {datetime.datetime.now().strftime('%Y-%m-%d')}")

    # Create a frame for displaying the conversation
    frame_display = tk.Frame(root)
    scrollbar_frame_display = tk.Scrollbar(frame_display)
    text_area_display =  scrolledtext.ScrolledText(frame_display, height=25, width=128, yscrollcommand=scrollbar_frame_display.set)
    text_area_display.config(background="#202020", foreground="#ffff33", font=("Courier", 12))
    scrollbar_frame_display.config(command=text_area_display.yview)
    text_area_display.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar_frame_display.pack(side=tk.RIGHT, fill=tk.Y)
    frame_display.pack()

    # Create a frame for controls and information
    frame_controls = tk.Frame(root)
    model_path_label = tk.Label(frame_controls, text=f"Model Path: {model_path}", font=("Courier", 12))
    model_path_label.pack(side=tk.LEFT, padx=10)
    frame_controls.pack(fill=tk.BOTH, padx=5, pady=5)

    # Create a frame for user input
    frame_user_input = tk.Frame(root)
    frame_main_user_input = tk.Frame(root)
    scrollbar_main_user_input = tk.Scrollbar(frame_main_user_input)
    text_area_main_user_input = scrolledtext.ScrolledText(frame_main_user_input, height=5, width=128, yscrollcommand=scrollbar_main_user_input.set)
    text_area_main_user_input.config(background="#202020", foreground="#ffff33", font=("Courier", 12))
    scrollbar_main_user_input.config(command=text_area_main_user_input.yview)
    text_area_main_user_input.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar_main_user_input.pack(side=tk.RIGHT, fill=tk.Y)
    frame_main_user_input.pack()

    # Create a button to send user-typed messages
    send_button = tk.Button(root, text="Send", command=lambda: send_message(model, text_area_main_user_input, text_area_display, engine))
    send_button.pack()

    # Create a button to initiate speech input
    speech_input_button = tk.Button(root, text="Speech Input", command=lambda: speech_input(text_area_main_user_input, recognizer, microphone, text_area_display, engine))
    speech_input_button.pack()

    # Start the tkinter event loop
    root.mainloop()

# Entry point for the application
if __name__ == "__main__":
    main()
