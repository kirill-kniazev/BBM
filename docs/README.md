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
│       ├── fire_cmap.py         # Colormap generation script
│       ├── Objective_Efficiency.txt  # Objective efficiency values
│       ├── Quantum_Efficiency_iXon_897.txt  # Quantum efficiency for iXon camera
│
├── data/                        
│   ├── SN9_100_3570.nd2         # Example input data (ND2 movie file)
│
├── docs/                        
│   ├── README.md                # Main project documentation
│
├── notebooks/                   
│   ├── data_analysis.ipynb      # Jupyter notebook for analysis and visualization
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

## Usage

### Running the Main Analysis
To run the main analysis script:
```bash
python src/Main.py
```

Make sure to update the paths in the script to point to your input `.nd2` file located in the `data/` directory.

### Steps in the Analysis

1. **Background Removal**: Background is subtracted using `sep.Background` to improve signal detection.
2. **Normalization**: Data is normalized between 0 and 1 to make intensity values comparable across datasets.
3. **Maxima Detection**: Local maxima are identified using OpenCV with a thresholding method.
4. **Intensity Extraction**: The intensity is extracted from the original unprocessed dataset for photon emission calculations.
5. **Photon Emission Rate Calculation**: The software computes the number of photons using custom equations from the raw camera counts.

### Example Input Data

The `data/SN9_100_3570.nd2` file is an example input file. Replace this with your own `.nd2` file for analysis.

### Photon Calculation

To calculate the number of photons arriving at the camera chip:
```bash
N_arrive = ((raw_count - bias_offset) * pre_amp_gain) / (EM_gain * Quantum_efficiency)
```

## Dependencies

- Python 3.x
- OpenCV
- NumPy
- sep (for background removal)
- Hidden Markov Models (HMM) for intensity analysis

Install them using:
```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

### Key Points:
- **File structure**: Reflects the structure you are using, including the `utils` folder for efficiency files.
- **Features and usage**: Detailed the functionality of the software, including background removal, signal normalization, and photon calculation.
- **Installation and dependencies**: Clear instructions on how to clone the repository, install dependencies, and run the analysis.