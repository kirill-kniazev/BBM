# Blinking-Based Multiplexing (BBM) for Single Molecule Localised Microscopy (SMLM) Software (Alpha)

This repository contains a Python-based software for analyzing Single-Molecule Localization Microscopy (SMLM) data using **Blinking-Based Multiplexing**. The analysis includes background removal, signal normalization, particle localization, intensity extraction, and photon emission calculations. The software is optimized for Python 3.10.

## Features
- **Blinking-Based Multiplexing**: Uses temporal blinking patterns of fluorophores to differentiate molecules.
- **Background Removal**: Utilizes `sep.Background` to remove noise and improve the signal-to-noise ratio.
- **Signal Normalization**: Normalizes intensity data to ensure consistency across datasets.
- **Particle Localization**: Identifies local maxima corresponding to single molecules using OpenCV.
- **Intensity Extraction**: Extracts raw camera counts to calculate photon emission rates and photobleaching dynamics.
- **Photon Emission Calculations**: Converts EMCCD counts to photon arrival rates using a custom equation.

## File Structure

```
BlinkSMLM/
│
├── src/                         
│   ├── BBM_Functions.py         # Python functions for blink detection and background removal
│   ├── GUIs.py                  # GUI for the analysis (if applicable)
│   ├── Main.py                  # Main analysis script
│   ├── utils/                   # Utility files for efficiency and colormap
│       ├── fire_cmap.py         # Custom colormap
│       ├── Objective_Efficiency.txt  # Objective efficiency values
│       ├── Quantum_Efficiency_iXon_897.txt  # Quantum efficiency for iXon camera
│
├── data/                        
│   ├── Cy8_Dye.nd2              # Example input data (ND2 movie file)
│
├── docs/                        
│   ├── README.md                # Main project documentation
│
├── requirements.txt             # Python dependencies list
├── LICENSE                      # License file
```

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/kirill-kniazev/BlinkSMLM.git
   cd BlinkSMLM
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
Here's a refined and more polished version of the **Usage** section based on your input:

---

## Usage

### 1. **Launching the GUI**:
To begin the analysis, open the graphical user interface (GUI) by running the `Main.py` script:

```bash
python src/Main.py
```

Once the GUI, titled **"Analysis Workflow"**, is launched, you will see two options: **"Start"** to begin the analysis or **"Close"** to exit the process. To proceed with the analysis, click the **Start** button.

This action will initialize the analysis workflow, and a status message **"Data Analysis in Process"** will appear. A new window titled **"Open the file"** will be displayed.

### 2. **Data Input (Drag and Drop)**:
In the **"Open the file"** window, you will be prompted to drag and drop your `.nd2` or `.tif` file into the designated area. Once you do this, the input GUI will close, and a new window called **"Parameters Input"** will open.

### 3. **User Input Configuration**:
After selecting the data file, a popup window will appear, asking for specific parameters needed for the analysis. These include:

- **Time interval between frames acquired** (default: 11 ms)
- **Number of frames to process** (default: full data stack)
- **Camera pre-amplification gain** (default: 5.1)
- **Camera EM gain** (default: 285)
- **Wavelength of emission for the dye** in the optical range (665-705 nm, default: 677 nm for SF8(d4)₂)

The window will have two buttons: **"Continue"** to proceed and **"Close"** to exit.

Once you click **Continue**, the next step for thresholding will begin.

### 4. **Thresholding for Particle Localization**:
In the **"Select Threshold to Localize Particles"** window, you will define the threshold values for particle localization. The GUI provides a visual interface that helps you adjust the threshold to detect particles accurately. Ideally, you should slightly oversample the particles, and a good starting number is around **100 particles**.

After setting the threshold, click **Continue**, and the analysis will begin. A **"Trace Processing"** window will pop up, displaying the processing progress in real-time.

### 5. **Results**:
Once the analysis is complete, the software will create a **"Results"** folder in the same directory as the file being analyzed.

Within this folder, there will be two groups of files:
- **"False Positive"**: Contains particles that were detected but did not exhibit any photobleaching or a two-state process.
- **"Positive"**: Contains particles that exhibited clear multi-optical processes.

These results will help you differentiate between valid and invalid single-molecule signals.  

### Example Input Data

The `data/Cy5_Dye.nd2` file is an example input file. Replace this with your own `.nd2` file for analysis.

### Photon Calculation

To calculate the number of photons arriving at the camera chip:
```bash
N_arrive = ((raw_count - bias_offset) * pre_amp_gain) / (EM_gain * Quantum_efficiency)
```
