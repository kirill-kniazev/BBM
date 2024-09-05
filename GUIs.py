import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
from BBM_Functions import BBM_Class
BBM = BBM_Class()                       # Create an instance of the class
from tkinter import messagebox
from tkinter import ttk
import sys                              # Import sys to allow us to call sys.exit()
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.exceptions import ConvergenceWarning
import warnings

# (GUI) Get file path and folder path from the user using a drag-and-drop interface
def get_file_and_folder_path():
    
    def drop(event):                            # Function to handle the drop event
        file_path = event.data.strip('{}')      # Remove curly braces from the path if they exist
        folder_path = os.path.dirname(file_path)# Get the folder path
        file_path_var.set(file_path)            # Store the values in the tkinter variables
        folder_path_var.set(folder_path)
        DnD.quit()                              # Close the window
        DnD.destroy()
    
    DnD = TkinterDnD.Tk()                       # Create a TkinterDnD window
    DnD.title('Open the file')
    file_path_var = tk.StringVar()              # Variables to store file and folder paths
    folder_path_var = tk.StringVar()
    frame = tk.Frame(DnD, width=400, height=200)# Create a frame inside the window
    frame.pack_propagate(False)
    frame.pack()
    label = tk.Label(frame, text="Drag and drop a .nd2 or .tif file here", bg='lightgrey') # Create a label with instructions
    label.pack(fill=tk.BOTH, expand=True)
    label.drop_target_register(DND_FILES)       # Register the label as a drop target for files
    label.dnd_bind('<<Drop>>', drop)            # Bind the drop event to the function
    DnD.mainloop()                              # Start the TkinterDnD main loop

    return file_path_var.get(), folder_path_var.get() # Return both the file and folder paths after the window closes
# Call the function and retrieve the file and folder paths
file_path, folder_path = get_file_and_folder_path()
data, shape = BBM.import_data(file_path)    # Import the data in nd2 or tif formats

# (GUI) Get user input
def get_user_input(shape):                  # Function to get user input for frame interval and number of frames
    input = tk.Tk()                         # Create a window
    input.title("Parameters Input")
    input.geometry('300x400')               # Set window size
    frame_interval_var = tk.IntVar(value=11)# Default value 11
    n_frames_var = tk.IntVar(value=shape[0])# Default value is the data shape
    pre_amp_var = tk.DoubleVar(value=5.1)   # Default value 5.1
    em_gain_var = tk.DoubleVar(value=285)   # Default value 285
    wavelength_var = tk.DoubleVar(value=677)# Default value 677

    def continue_button():                                                      # Function to handle the "Continue" button
        # Get the input values
        frame_interval, n_frames, pre_amp, em_gain, wavelength = frame_interval_var.get(), n_frames_var.get(), pre_amp_var.get(), em_gain_var.get(), wavelength_var.get()
        if frame_interval <= 0 or n_frames <= 0:                                # Check if the values are valid
            messagebox.showerror("Invalid Input", "Please enter positive numbers.")
        else:                                                                   # Destroy the window and return the input values
            input.quit()                                                        # This will exit the event loop but keep the window open for possible input retrieval
            input.destroy()                                                     # This will fully close the window

    def close_button(): # Function to handle the "Close" button
        input.quit()    # Exit the entire program
        input.destroy()
        exit()

    # Create labels and entry widgets
    label_frame_interval = tk.Label(input, text="Frame interval in ms:")
    label_frame_interval.pack(pady=5)
    entry_frame_interval = tk.Entry(input, textvariable=frame_interval_var)
    entry_frame_interval.pack(pady=5)

    label_n_frames = tk.Label(input, text="Number of frames to process:")
    label_n_frames.pack(pady=5)
    entry_n_frames = tk.Entry(input, textvariable=n_frames_var)
    entry_n_frames.pack(pady=5)

    label_pre_amp = tk.Label(input, text="Pre Amp value:")
    label_pre_amp.pack(pady=5)
    label_pre_amp = tk.Entry(input, textvariable=pre_amp_var)
    label_pre_amp.pack(pady=5)

    label_em_gain = tk.Label(input, text="EM Gain value:")
    label_em_gain.pack(pady=5)
    label_em_gain = tk.Entry(input, textvariable=em_gain_var)
    label_em_gain.pack(pady=5)

    label_wavelength = tk.Label(input, text="Wavelength value (665-705) (SF8=677, Cy5=665):")
    label_wavelength.pack(pady=5)
    label_wavelength = tk.Entry(input, textvariable=wavelength_var)
    label_wavelength.pack(pady=5)

    # Create "Continue" and "Close" buttons
    button_continue = tk.Button(input, text="Continue", command=continue_button)
    button_continue.pack(pady=10)
    button_close = tk.Button(input, text="Close", command=close_button)
    button_close.pack(pady=10)

    # Start the Tkinter event loop
    input.mainloop()

    # Return user inputs
    return frame_interval_var.get(), n_frames_var.get(), pre_amp_var.get(), em_gain_var.get(), wavelength_var.get()
frame_interval, n_frames, pre_amplifier_gain, em_gain, wavelength = get_user_input(shape)

data = data [0:n_frames]           # Crop out corrupted data
data_full = data                   # Save the full data for later use

# Prepare data for the h analysis
def data_optimization(data, shape, n_frames=4000): # Function to optimize the data for the h analysis
    if shape[0] >= n_frames:
        data = data[0:n_frames-1]           # Crop the data to the specified number of frames
        shape = data.shape
    elif shape[0] <= n_frames:              # Process the original data if it has fewer frames than n_frames
        pass
    # Background removal and normalization
    data = BBM.data_normalization(np.array([BBM.background_removal(data[i]) for i in range(data.shape[0])]))
    max_frame = BBM.max_frame(data)
    return data, shape, max_frame
data, shape, max_frame = data_optimization(data, shape, n_frames)

# (GUI) Get the h value from the user using a slider
def get_h(max_frame):
    max_frame = BBM.data_normalization(max_frame)   # Normalize the max frame

    def on_slider_move(value):

        # Update the slider and the particles positions
        gather_h.h = float(value)                   # Convert the slider value to a float
        maxima_locations_arr, maxima_locations_arr_joined, maxima_locations_quantity = BBM.locate_maxima(max_frame, gather_h.h, 5)

        # Plot the images with the maxima locations
        fig, ax = BBM.plot_images(max_frame,  maxima=maxima_locations_arr_joined, normalize = False, cmap = 'gray', axis = False, title=f"Detected {maxima_locations_quantity} particles.", lable="Maximum Count Recived per Pixel")

        # Replace the figure on the existing canvas
        on_slider_move.canvas.figure = fig
        on_slider_move.canvas.draw()
        
        print(f"Slider value: {gather_h.h}")

    def on_continue():     # Function to close the window
        plt.close('all')   # Close all figures
        gather_h.quit()    # This method tells the Tkinter main loop to exit
        gather_h.destroy() # This ensures the window is closed properly

    def on_close():        # Function to handle the window close (X button)
        plt.close('all')   # Close all figures
        gather_h.quit()    # Exit the Tkinter loop
        gather_h.destroy() # Destroy the Tkinter window
        sys.exit()         # Exit the entire script

    # Create the main window
    gather_h = tk.Tk()
    gather_h.title("Select Threshold to Locate Particles")  # Set the window title
    gather_h.geometry("600x700")                            # Set the window size

    # Bind the window close (X) button to the on_close function
    gather_h.protocol("WM_DELETE_WINDOW", on_close)

    # Create frames for structured layout
    top_frame = tk.Frame(gather_h)
    top_frame.pack(side='top', fill='x', padx=10, pady=10)

    middle_frame = tk.Frame(gather_h)
    middle_frame.pack(side='top', fill='both', expand=True, padx=10, pady=10)

    bottom_frame = tk.Frame(gather_h)
    bottom_frame.pack(side='bottom', fill='x', padx=10, pady=10)

    # Create and pack the slider in the top frame
    slider = tk.Scale(
        top_frame, 
        from_=0, 
        to=1, 
        orient='horizontal', 
        resolution=0.01, 
        command=on_slider_move,
        label="Select 'h' Value"
    )
    slider.set(0.2)  # Set the default value
    slider.pack(fill='x')

    # Create and pack the "Continue" button in the bottom frame
    continue_button = tk.Button(
        bottom_frame, 
        text="Continue with the Current 'h' Value", 
        command=on_continue
    )
    continue_button.pack(pady=5)

    # Plot the initial figure (before any slider movement)
    fig, ax = BBM.plot_images(max_frame, maxima=[], normalize=False, cmap = 'gray', axis=False, title="Maximum Projection", lable="Maximum Count Recived per Pixel")

    # Initialize the canvas and pack it in the middle frame
    canvas = FigureCanvasTkAgg(fig, master=middle_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
    on_slider_move.canvas = canvas  # Assign the canvas to the slider move handler

    # Start the Tkinter event loop
    gather_h.mainloop()

    return gather_h.h
h = get_h(max_frame)

# Create results folder where all the results will be saved, use the folder path parameter and use the file name to create a folser
results_path = f"{folder_path}/{os.path.splitext(os.path.basename(file_path))[0]}_Results"
if not os.path.exists(results_path): # Check if the folder already exists
    os.makedirs(results_path)        # Create the folder if it doesn't exist

# Create a folder to save the traces
def get_positions(data, h):
    # Locate maxima in the data
    maxima_locations_arr, maxima_locations_arr_joined, maxima_locations_quantity = BBM.locate_maxima(data, h, 5)
    # print (f'Maxima locations collected from {0} frame; Quantity: {len(maxima_locations_arr[0])}')
    # print (f'Maxima locations collected from all {shape[0]} frames; Resulting in average of {int(maxima_locations_quantity/shape[0])} maxima per frame')

    # Show 2-dimensional histogram and data with maxima locations
    histogram_2d = BBM.histogram_2d_gradient(shape, maxima_locations_arr_joined)
    maxima_locations_arr, maxima_locations_arr_joined, maxima_locations_quantity = BBM.locate_maxima(histogram_2d, 4, 5)
    maxima_locations_arr_joined = np.array(maxima_locations_arr_joined)                             # Save the maxima locations in txt file

    # Create and save the figures
    fig1, ax1 = BBM.plot_images(histogram_2d, maxima=maxima_locations_arr_joined, title='Two-Dimmentional Histogram', normalize=False, cmap='gray', lable="Particle occurrence (factor of 3)")  # Plot the first image (2D histogram)
    fig1.savefig(f"{results_path}/2d_histogram.png")                                                # Save the figure to the specified path
    np.savetxt(f"{results_path}/2d_histogram.txt", histogram_2d)                                    # Save the histogram in txt file
    fig2, ax2 = BBM.plot_images(max_frame, cmap='gray', title="Maximum Projection", lable="Normalized Counts Recived per Pixel")  # Plot the second image (max frame)
    ax2.set_title('Maximum Projection')
    fig2.savefig(f"{results_path}/Maximum Projection.png")                                          # Save the figure to the specified path
    np.savetxt(f"{results_path}/Maximum Projection.txt", max_frame)                                 # Save the max frame in txt file

    # Close the figures
    plt.close(fig1)
    plt.close(fig2)
    
    # Save the maxima locations in txt file
    trace_numbers = np.arange(maxima_locations_arr_joined.shape[0]).reshape(-1, 1)      # Create an array with trace numbers
    new_array = np.hstack((trace_numbers, maxima_locations_arr_joined))                 # Combine the trace numbers with the maxima locations
    header = 'Trace Number, y, x'                                                       # Create a header for the txt file
    np.savetxt(f"{results_path}/Particles_Positions.txt", new_array, header=header, comments='', delimiter=',')   

    # Return the maxima locations
    return maxima_locations_arr, maxima_locations_arr_joined, maxima_locations_quantity  
maxima_locations_arr, maxima_locations_arr_joined, maxima_locations_quantity = get_positions(data, h) # Get the positions of the particles
del data        # Remove the data to free up memory

# Create a folders to save the traces
positive_path = f"{results_path}/Positive"
if not os.path.exists(positive_path):  # Check if the folder already exists
    os.makedirs(positive_path)         # Create the folder if it doesn't exist

false_positive_path = f"{results_path}/False_Positive"
if not os.path.exists(false_positive_path):  # Check if the folder already exists
    os.makedirs(false_positive_path)         # Create the folder if it doesn't exist

# (GUI feedback) Analyse the traces: Remove traces that don't show photobleaching
emissions = BBM.extract_intensities_max(data_full, maxima_locations_arr_joined, maxima_locations_quantity, frame_interval) # Gather emissions from the data

def progress_analysis (emissions, maxima_locations_quantity, positive_path, false_positive_path):
    # Create the main window
    root = tk.Tk()
    root.title("Trace Processing")
    
    # Set window size
    root.geometry("400x200")
    
    # Create a label to show the status of processing
    status_label = tk.Label(root, text="Loading...")
    status_label.pack(pady=20)

    # Create a progress bar
    progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=20)

    # Set the progress bar's maximum value
    progress['maximum'] = maxima_locations_quantity - 1

    # Start processing traces (simulating a loop with real data)
    for i in range(maxima_locations_quantity):
        status_label.config(text=f"Processing trace {i} out of {maxima_locations_quantity}")
        progress['value'] = i       # Update the progress bar

        process_traces(emissions, i, positive_path, false_positive_path)

        root.update_idletasks()     # Update the GUI with current progress

    # Completion message after loop finishes
    status_label.config(text="Processing complete!")
    progress['value'] = maxima_locations_quantity - 1  # Ensure the progress bar is full

    # Start the Tkinter main loop
    root.mainloop()

def process_traces(emissions, i, positive_path, false_positive_path):

    number_of_states = 1
    for guess_state in range(2, 3):    
        states = BBM.states_assignment(guess_state, emissions, int(i))              # Assign states to the emissions      
        warnings.filterwarnings("ignore", category=ConvergenceWarning)              # Suppress specific warnings if needed           
        silhouette_avg = BBM.calculate_silhouette(emissions, states, int(i))        # Calculate silhouette coefficient
        if silhouette_avg > 0.65:
            number_of_states = guess_state                                          # Update the number of states if silhouette coefficient is above threshold
            break
    states = BBM.states_assignment(number_of_states, emissions, int(i))             # Fit HMM with the optimal number of states

    print(f"Trace {i}: {number_of_states} states(s). Silhouette coefficient {round(silhouette_avg, 2)}/{0.65}.")

    if number_of_states >= 2:
        mono, trace_path, trace_name = False, positive_path, f"Trace_{i}"
    else:
        mono, trace_path, trace_name = True, false_positive_path, f"Mono_Trace_{i}"

    # COUNTS
    # Plot the emissions and save the trace in a txt file
    fig, ax =BBM.plot_emissions(emissions, int(i), states, mono=mono)
    fig.savefig(f"{trace_path}/{trace_name}.png")
    plt.close()

    # PHOTONS - R
    # Count Convert
    counts = emissions[i + 1]
    photons_received = BBM.count_convert(counts, pre_amplifier_gain = pre_amplifier_gain, em_gain = em_gain, wavelength = wavelength)
    emissions[i + 1] = photons_received
    # Plot the emissions and save the trace in a txt file
    fig, ax =BBM.plot_emissions(emissions, int(i), states, mono=mono, lable_Oy="Photons Received")
    fig.savefig(f"{trace_path}/{trace_name}_Photons_R.png")
    plt.close()

    # PHOTONS - E
    # Emitted Phototns
    recorded_to_emitted = BBM.recorded_to_emitted(photons_received, wavelength = wavelength)
    emissions[i + 1] = recorded_to_emitted
    # Plot the emissions and save the trace in a txt file
    fig, ax =BBM.plot_emissions(emissions, int(i), states, mono=mono, lable_Oy="Emitted Photons")
    fig.savefig(f"{trace_path}/{trace_name}_Photons_E.png")
    plt.close()

    # Save trace in txt file
    trace = np.zeros((len(emissions[0]), 4))
    trace[:, 0], trace[:, 1], trace[:, 2], trace[:, 3] = emissions[0], counts, photons_received, recorded_to_emitted
    header = "Time, Emissions, Photons Received, Emitted Photons" 
    np.savetxt(f"{trace_path}/{trace_name}.txt", trace, header=header)

progress_analysis(emissions, maxima_locations_quantity,  positive_path, false_positive_path)