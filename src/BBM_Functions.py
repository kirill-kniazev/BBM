from utils.fire_cmap import fire_cmap  # Import the custom color map
import os
import nd2                       # To read Nikon ND2 files
import tifffile as tiff          # To read and write TIFF files
import numpy as np               # Numpy for numerical calculations
import sep                       # Source Extractor for single molecule images
import cv2                       # OpenCV for image processing
import matplotlib.pyplot as plt  # Matplotlib for plotting
import matplotlib.patches as patches # Matplotlib for patches
from hmmlearn import hmm
import time
from sklearn.metrics import silhouette_score
from sklearn.exceptions import ConvergenceWarning
import warnings

# Class with all necessary methods for the project
class BBM_Class:
        def __init__(self):
            self.cmap = fire_cmap
            warnings.filterwarnings("ignore", category=ConvergenceWarning) # Suppress specific warnings if needed

        def import_data(self, path):   # Import data from the file
            # Check if the data is tif or nd2, otherwise raise an exception
            _, ext = os.path.splitext(path)
            if ext.lower() == '.nd2':
                return self.import_nd2(path)
            elif ext.lower() == '.tif':
                return self.import_tif(path)
            else:
                raise ValueError("Unsupported file format")

        def import_nd2(self, path):           # Import nd2 file as int numpy array
            try:
                data = nd2.imread(path)
                data = np.array(data, dtype=int)
                print(f"ND2 Data imported. Shape: {data.shape}")
                return data, data.shape
            except Exception as e:
                print(f"Failed to import ND2 file: {str(e)}")
                raise

        def import_tif(self, path):           # Import tif file as int numpy array
            try:
                data = tiff.imread(path)
                data = np.array(data, dtype=int)
                print(f"TIF Data imported. Shape: {data.shape}")
                return data, data.shape
            except Exception as e:
                print(f"Failed to import TIF file: {str(e)}")
                raise

        def background_removal (self, data):  # Remove background from the image
            bkg = sep.Background(data, bw=64, bh=64, fw=3, fh=3) # Background estimation can be adjusted if needed
            data_subtracted = data - np.array(np.array(bkg))
            return data_subtracted

        def data_normalization(self, data):   # Normalize the image data to range [0, 1]
            data_min, data_max = np.min(data), np.max(data)
            normalized_data = (data - data_min) / (data_max - data_min)
            print (f"Data normalized from {data_min} - {data_max} to 0 - 1")
            return normalized_data

        def data_interpolation(self, data, height, width):   # Interpolate data to increase the resolution
            # If initial resolution is 107.3 nm/pix, then we change the resolution to 10 nm/pix by multiplying dimenions 10 times
            if len(data.shape) == 3:            # Check if data is a 3D array
                interpolated_slices = []        # Initialize an empty list to store the interpolated 2D slices
                for i in range(data.shape[0]):  # Iterate over each 2D slice in the 3D array
                    interpolated_slice = cv2.resize(data[i].astype(np.float32), (height, width), interpolation=cv2.INTER_CUBIC) # Interpolate the current 2D slice
                    interpolated_slices.append(interpolated_slice)          # Append the interpolated slice to the list
                data_interpolated = np.stack(interpolated_slices, axis=0)   # Stack the interpolated 2D slices back into a 3D array
            else: # If data is not a 3D array, interpolate it directly
                data_interpolated = cv2.resize(data.astype(np.float32), (height, width), interpolation=cv2.INTER_CUBIC)
            shape = data_interpolated.shape
            print (f"Data interpolated from {data.shape} to {shape}")
            return data_interpolated, shape

        def locate_maxima(self, data, h, box):              # Locate local maxima in the movies
            if len(data.shape) == 3:                        # Check if data is a 3D array
                maxima_locations_arr = []                   # Create an empty list to store the maxima locations
                for i in range(data.shape[0]):              # Loop through all frames
                    neighborhood_size = (2 * box + 1)       # For each pixel, checks the surrounding neighborhood box to evaluate local maxima
                    local_max = cv2.dilate(data[i], np.ones((neighborhood_size, neighborhood_size))) == data[i] # Finds the local maxima
                    maxima = (data[i] > h) & local_max                                     # Exclude the local maxima that are below the threshold 'h'
                    maxima_locations = np.argwhere(maxima)                                 # Get the positions of the maxima
                    maxima_locations_arr.append(maxima_locations)                          # Append the maxima locations to the list          
                maxima_locations_arr_joined = np.concatenate(maxima_locations_arr, axis=0) # Join all maxima locations into a single array
                print (f"Maxima located in {len(maxima_locations_arr_joined)} positions or about {int(round(len(maxima_locations_arr_joined) / data.shape[0]))} per frame")
            else:
                neighborhood_size = (2 * box + 1)                   # For each pixel, checks the surrounding neighborhood box to evaluate local maxima
                local_max = cv2.dilate(data, np.ones((neighborhood_size, neighborhood_size))) == data # Finds the local maxima
                maxima = (data > h) & local_max                     # Exclude the local maxima that are below the threshold 'h'
                maxima_locations_arr_joined = np.argwhere(maxima)   # Get the positions of the maxima  
                maxima_locations_arr = [0]                          # Create empty placeholder
                print (f"Maxima located in {len(maxima_locations_arr_joined)} positions")
            return maxima_locations_arr, maxima_locations_arr_joined, len(maxima_locations_arr_joined)

        def histogram_2d (self, shape, maxima_locations):   # Create a 2D histogram of the maxima
            if len(shape) == 3:                             # Define is shape 2- or 3-dimensional
                height, width = shape[1], shape[2]
            else:
                height, width = shape[0], shape[1]
            histogram_2d = np.zeros((height, width))        # Extract the final dimensions for the histogram
            for i in range(maxima_locations.shape[0]):      # Fill the histogram with the maxima locations
                histogram_2d[int(maxima_locations[i, 0]), int(maxima_locations[i, 1])] += 1 
            print ("2-D histogram created")
            return histogram_2d

        def histogram_2d_gradient(self, shape, maxima_locations):   # Similar to the previous function, but with a box around the maxima. Center = 3, First layes = 2, Second layer = 3. 
            if len(shape) == 3:                                     # Define is shape 2- or 3-dimensional
                height, width = shape[1], shape[2]
            else:
                height, width = shape[0], shape[1]
            histogram_2d = np.zeros((height, width))                # Extract the final dimensions for the histogram
            for location in maxima_locations:                       # Process each maxima location
                x, y = int(location[0]), int(location[1])
                histogram_2d[x, y] += 3                             # Add 3 at the maxima location
                for dx in [-1, 0, 1]:                               # Add to the immediate neighbors value of 2
                    for dy in [-1, 0, 1]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < height and 0 <= ny < width and (dx != 0 or dy != 0):
                            histogram_2d[nx, ny] += 2
                for dx in [-2, -1, 0, 1, 2]:                        # Add to the next layer of neighbors value of 1
                    for dy in [-2, -1, 0, 1, 2]:
                        if abs(dx) == 2 or abs(dy) == 2:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < height and 0 <= ny < width:
                                histogram_2d[nx, ny] += 1
            print("2-D histogram created")
            return histogram_2d

        def max_frame(self, data):                                  # Max all frames in the movie
            data_max = np.max(data, axis=0)                         # Max all frames in the movie
            return data_max                    

        def extract_intensities (self, data, maxima_locations, maxima_quantity, frame_interval):       # Extract emission withn 5 pixels around maxima vs time data
            emissions = np.zeros((maxima_quantity + 1, data.shape[0]))                                 # Create an empty array
            emissions[0] = (np.arange(0, data.shape[0] * frame_interval, frame_interval))/1000         # Fill array with the time in seconds
            for i in range(maxima_quantity):                                                           # Fill array with the emission data
                x, y = maxima_locations[i]
                for j in range(data.shape[0]):
                    emissions[i + 1, j] = data[j, x, y]
            return emissions

        def extract_intensities_max (self, data, maxima_locations, maxima_quantity, frame_interval):        # Extract emission withn 5 pixels around maxima vs time data
            emissions = np.zeros((maxima_quantity + 1, data.shape[0]))                                      # Create an empty array
            emissions[0] = (np.arange(0, data.shape[0] * frame_interval, frame_interval))/1000              # Fill array with the time in seconds
            for i in range(maxima_quantity):                                                                # Fill array with the emission data
                x, y = maxima_locations[i]
                for j in range(data.shape[0]):                                                              # Define the bounds of the box ensuring they are within the image boundaries
                    x_min = max(x - 3, 0)
                    x_max = min(x + 3, data.shape[1])                                                       # Use shape[1] as x corresponds to columns
                    y_min = max(y - 3, 0)
                    y_max = min(y + 3, data.shape[2])                                                       # Use shape[2] as y corresponds to rows
                    emissions[i + 1, j] = np.max(data[j, x_min:x_max, y_min:y_max])                         # Extract the maximum value safely within the bounded region
            return emissions

        def plot_images(self, data, maxima=None, normalize=True, cmap=fire_cmap, radius=5, axis=False, title=None, lable='Normalized Detected Counts'): # Plot the image
            fig, ax = plt.subplots(1, 1, figsize=(6.5, 5))
            
            if normalize:
                im = ax.imshow(data, cmap=cmap, vmin=0, vmax=1)                                         # Create an image
                cbar = fig.colorbar(im, ax=ax)
                cbar.set_label(f'{lable}', rotation=90, labelpad=15)        # Add label to colorbar
                cbar.set_ticks([0, 0.25, 0.5, 0.75, 1])                                                 # Optional: set specific ticks if needed
                cbar.set_ticklabels(['0.00', '0.25', '0.50', '0.75', '1.00'])                           # Set tick labels to reflect the normalized scale
            else:
                im = ax.imshow(data, cmap=cmap)                                                         # Create an image
                cbar = fig.colorbar(im, ax=ax)
                cbar.set_label(f'{lable}', rotation=90, labelpad=15)
            if axis:
                ax.axis('on')                                                                           # Turn on the axis
            else:
                ax.axis('off')                                                                          # Turn off the axis
            if maxima is not None:
                for pos in maxima:
                    circle = patches.Circle((pos[1], pos[0]), radius=radius, edgecolor='red', facecolor='none')
                    ax.add_patch(circle)
            if title is not None:
                ax.set_title(title)                                                                # Add title to the plot
            return fig, ax

        def states_assignment (self, number_of_states, emissions, i):   # Function to assign states to the emissions
            gm = hmm.GMMHMM(n_components=number_of_states)              # Initialize HMM with sertain number states to look for
            gm.fit(emissions[i + 1].reshape(-1, 1))                     # Fit HMM to the intensity values
            states = gm.predict(emissions[i + 1].reshape(-1, 1))        # Predict states
            return states

        def calculate_silhouette(self, emissions, states, i, retry_count=3, delay=1):           # Define a function to calculate silhouette coefficient with retries
            for attempt in range(retry_count):
                try:
                    silhouette_avg = silhouette_score(emissions[i + 1].reshape(-1, 1), states)  # Attempt to calculate the silhouette score
                    return silhouette_avg                                                       # If the calculation is successful, return the result
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed with error: {e}")
                    if attempt == retry_count - 1:                                              # If it's the last attempt, handle the failure
                        print("Max retries reached, skipping this calculation.")
                        return 0                                                                # Return 0 or any default value as appropriate
                    else:
                        time.sleep(delay)                                                       # Optional: wait before retrying

        def plot_emissions(self, emissions, i, states, mono=False, lable_Oy = 'Detected Counts'): # Plot emissions with states
            state_colors = {0: "r", 1: "g", 2: "b", 3: "c", 4: "m"} # Define a color map for states
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
            ax.plot(emissions[0], emissions[i + 1], color='k', alpha=0.5)
            ax.set_xlabel('Time, s')
            ax.set_ylabel(f'{lable_Oy}')

            # Set y-limits for the primary y-axis based on emissions
            ax.set_ylim(np.min(emissions[i + 1]), np.max(emissions[i + 1]))

            if mono == False:
                for state in np.unique(states):                     # Plot emissions with different colors for each state
                    state_mask = states == state
                    ax.scatter(emissions[0][state_mask], emissions[i + 1][state_mask], label=f'State {state}', color=state_colors[state])
                last_state_change_idx = np.max(np.where(np.diff(states) != 0)[0])
                last_state_change_x = emissions[0][last_state_change_idx + 1]
                # Add vertical line at the last state change
                ax.axvline(x=last_state_change_x, color='black', linestyle='--')
                ax.text(last_state_change_x, np.max(emissions[i + 1]), f'{last_state_change_x:.2f}', rotation=90, verticalalignment='bottom', color='black')

            return fig, ax
        
        def count_convert(self, trace_Oy, bias_offset = 200, pre_amplifier_gain = 5.1, em_gain = 285, wavelength = 677):# Convert counts into photons. Defoult wavelength 677 for SF8
            if wavelength <= 665 or wavelength >= 705:                                                                    # Check if the wavelength is within the optical filters transmission range
                print ("The wavelength is out of range")
            if wavelength >= 665 and wavelength <= 705: 
                
                current_dir = os.path.dirname(os.path.abspath(__file__))                                                # Get the current directory and Load the quantum efficiency of the Andor iXon 897 camera
                quantum_efficiency = np.loadtxt(os.path.join(current_dir, "utils/Quantum_Efficiency_iXon_897.txt"), delimiter=',', skiprows=1)

                qe_data = quantum_efficiency[np.where(quantum_efficiency[:, 0] == wavelength)] / 100                    # Extract the quantum efficiency in % for the given wavelength
                trace_Oy = ((trace_Oy - bias_offset) * pre_amplifier_gain) / (em_gain * qe_data[0, 1])                  # Convert counts into photons
            return trace_Oy
        
        def recorded_to_emitted(self, trace_Oy, NA = 1.49, n = 1.515, n_ellements = 4, wavelength = 677):  # Convert recieved photons by camera into emitted photons by the sample
            if wavelength <= 665 or wavelength >= 705:                                                       # Check if the wavelength is within the optical filters transmission range
                print ("The wavelength is out of range")
            if wavelength >= 665 and wavelength <= 705:    
                theta = np.degrees(np.arcsin(NA / n))                                                      # Calculate theta (half-angle of the collected light cone 
                eta_coll = (1 - np.cos(theta)) / 2                                                         # Calculate the light collection efficiency (eta_coll)

                current_dir = os.path.dirname(os.path.abspath(__file__))                                   # Get the current directory and Load the objective transmission efficiency data
                OL_efficiency = np.loadtxt(os.path.join(current_dir, "utils/Objective_Efficiency.txt"), delimiter=',', skiprows=1)
                
                OL_data = OL_efficiency[np.where(OL_efficiency[:, 0] == wavelength)] / 100                 # Extract the quantum efficiency data for the given wavelength in %
                eta_opt = OL_data[0, 1] * 0.96 ** n_ellements                                              # Calculate the optical efficiency (eta_opt)
                trace_Oy = trace_Oy / (eta_coll * eta_opt)                                                 # Convert the recieved photons into emitted photons
            return trace_Oy