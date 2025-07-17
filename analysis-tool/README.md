# Snake Illusion Analysis Tool

A MATLAB-based analysis tool for evaluating participant responses in a psychophysical experiment on the "Snake Illusion". This script processes color and achromatic variants of the illusion and calculates success rates, produces grouped comparisons, and visualizes the data with standard deviation plots.

## Overview

Participants in the experiment viewed colored or achromatic Snake Illusion images and judged the direction of perceived motion. This script:

- Merges participant data from multiple .csv files
- Computes success rates based on predefined correct answers
- Supports comparison across color conditions (orange/purple)
- Integrates data from achromatic versions of the illusion
- Produces publication-ready graphs and summary tables

It is designed to be robust, customizable, and easy to extend for new experimental conditions.

## Features

### Data Merging
- Loads .csv files from a defined input folder
- Filters out invalid or empty rows
- Removes duplicate trials with the same pattern and color
- Automatically handles and fills missing responses where possible

### Success Rate Calculation
- Uses a configurable map of correct answers per pattern
- Separates analysis by color scheme (orange, purple)
- Computes proportion of correct responses per pattern/color

### Achromatic Image Analysis
- Matches grayscale image filenames to color-equivalent patterns
- Aggregates responses across participants
- Calculates success rates for achromatic conditions

### Graph Generation
Generates and saves six figure types:

1. **Grouped Bar Plot**: Orange vs Purple per pattern
2. **Flat Bar Plot**: All pattern/color combinations
3. **Grouped + STD Plot**: With error bars for standard deviation
4. **Flipped Pattern Pair Plot**: Comparing mirrored patterns
5. **Achromatic Comparison Plot**: Orange vs Purple vs Achromatic
6. **Achromat + STD Plot**: All three with ±STD labels

Each figure is saved as a PNG with a descriptive filename.

## Setup

### Folder Configuration
Before running the script, make sure you edit folder paths at the top of the script:

```matlab
input_folder     = 'C:\path\to\chromatic_csvs';
achromat_folder  = 'C:\path\to\achromatic_csvs';
output_folder    = 'C:\path\to\results';
```

#### Explanation:
- **input_folder**: Folder containing CSV files exported from the psychophysical experiment platform (Cognition.run). Each CSV represents a participant's responses to chromatic (colored) illusion trials. Required columns: `saturation_pattern`, `color_scheme`, `response`.

- **achromat_folder**: Folder containing CSV files of responses to achromatic images. These are also exported from the same experimental platform. Required columns: `actual_filename`, `response`.

- **output_folder**: A new empty folder where the MATLAB script will save:
  - The merged and cleaned data table
  - All result figures (PNG format)

You need to download participant response data from Cognition.run after running the experiment and place them into the appropriate folders above.

## Output Files

Output files will be saved in the folder defined as `output_folder` at the beginning of the script.

| File | Description |
|------|-------------|
| `all_fix.csv` | Merged, cleaned response table |
| `success_rate_plot_grouped.png` | Grouped color bars per pattern |
| `success_rate_plot_flat.png` | Flat bar chart for all combinations |
| `success_rate_combined_std.png` | ±STD grouped bars |
| `flipped_pairs_same_color_std.png` | Mirrored pattern comparison |
| `success_rate_achromat.png` | Orange vs Purple vs Achromatic |
| `success_rate_std_plot.png` | Triple condition ±STD |

## Requirements

- MATLAB R2021a or later
- CSV files formatted as output from the jsPsych experiment
- Compatible with Windows/macOS/Linux

## Example File Naming Convention

Achromatic images are matched based on filenames like:
```
snake_illusion_p35_c000000-ffffff-ffffff-707070_s0-0-0-0_w1.0-1.0-1.0-1.0_a-15.5_bg-808080.png
```

This is consistent with the naming structure produced by the Snake Illusion Generator.

## Customization for Your Research

To adapt this tool to new experiments:

- Add new pattern mappings in `correct_answers` and `achromat_map`
- Change plot aesthetics (colors, fonts, layout) directly in the figure sections
- Adjust data filtering or STD methods (e.g., population vs. sample std)

If images don't match or data fails to load:

- Check for typos in `saturation_pattern` or `actual_filename`
- Confirm all required fields are present in your CSVs
- Try running the script on a smaller dataset first for debugging