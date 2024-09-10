import tkinter as tk
import subprocess
import threading
import os

def start():
    button_start.pack_forget()                                                      # Remove the buttons and display the message
    button_close.pack_forget()
    label_processing = tk.Label(root, text='Data Analysis in Process', bg='yellow') # Create a label to show that the process is ongoing
    label_processing.pack(pady=20)

    def run_analysis():                             # Run the subprocess in a separate thread to prevent blocking the GUI

        # Get the path to the current script's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to GUIs.py
        gui_script_path = os.path.join(current_dir, 'GUIs.py')

        subprocess.run(['python', gui_script_path]) # Run the analysis script
        label_processing.pack_forget()              # After the process completes, update the GUI (re-enable buttons)
        button_start.pack(pady=20)
        button_close.pack(pady=20)
    threading.Thread(target=run_analysis).start()   # Start the process in a new thread

def close():                                        # Close the window
    print('Close')
    root.destroy()

root = tk.Tk()                                              # Create the main window
root.title('Analysis Workflow')                             # Set the title of the window
root.geometry('400x200')                                    # Set the window size to 400x200 pixels
button_start = tk.Button(root, text='Start', command=start) # Create the "Start" button
button_start.pack(pady=20)
button_close = tk.Button(root, text='Close', command=close) # Create the "Close" button
button_close.pack(pady=20)

root.mainloop()                                             # Start the main loop of the window

