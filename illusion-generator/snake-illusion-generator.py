import sys
import numpy as np
import colorsys
import matplotlib

matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider, QRadioButton, QComboBox,
                             QFrame, QCheckBox, QFileDialog, QMessageBox, QSpinBox,
                             QColorDialog, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
import json
from datetime import datetime


class ColorButton(QPushButton):
    def __init__(self, color="#000000", parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 20)
        self.color = color
        self.setStyleSheet(f"background-color: {color}; border: 1px solid black;")

    def set_color(self, color):
        self.color = color
        self.setStyleSheet(f"background-color: {color}; border: 1px solid black;")


class SnakeIllusionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snake Illusion Generator")
        self.setMinimumSize(1200, 800)

        # Color palettes
        self.COLOR_PALETTES = {
            "Classic": ["#000000", "#B0B0B0", "#FFFFFF", "#707070"],
            "Vibrant": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"],
            "Pastel": ["#FFB6C1", "#AFEEEE", "#FFDAB9", "#D8BFD8"],
            "Monochrome": ["#000000", "#333333", "#666666", "#999999"],
            "Earthy": ["#8B4513", "#A0522D", "#CD853F", "#DEB887"],
            "Cool": ["#4682B4", "#5F9EA0", "#6495ED", "#87CEFA"],
            "Warm": ["#FF6347", "#FF7F50", "#FFA07A", "#FFDAB9"]
        }

        # State variables
        self.background_color = "#808080"
        self.bg_display_color = self.background_color
        self.background_saturation = 0.0
        self.num_patterns = 24
        self.shift_angle = -12.5
        self.num_colors = 4
        self.transparent_bg = False
        self.use_classic_pattern = False  # False = Complete reversal, True = Classic partial flip

        # Color variables
        self.colors = self.COLOR_PALETTES["Classic"].copy()
        self.original_colors = self.COLOR_PALETTES["Classic"].copy()
        self.color_saturation = [self.get_color_saturation(c) for c in self.colors]
        self.widths = [1.0, 1.0, 1.0, 1.0]

        # Figure references
        self.preview_figure = None
        self.current_figure = None

        # UI components
        self.color_frames = []
        self.color_buttons = []
        self.width_sliders = []
        self.width_spins = []
        self.sat_sliders = []
        self.sat_spins = []
        self.hex_values = []
        self.bg_color_btn = None
        self.bg_sat_slider = None
        self.bg_sat_spin = None
        self.bg_hex_value = None
        self.transparent_check = None
        self.pattern_slider = None
        self.pattern_spin = None
        self.shift_slider = None
        self.shift_spin = None
        self.shift_label = None
        self.preview_frame = None
        self.canvas_frame = None
        self.palette_combo = None
        self.radio_3_colors = None
        self.radio_4_colors = None
        self.radio_classic_pattern = None
        self.radio_reversed_pattern = None

        # Set up UI
        self.setup_ui()

        # Start preview timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_preview)
        self.update_timer.start(500)

        # Initial preview
        self.update_preview()

    def get_color_saturation(self, hex_color):
        """Get the saturation value of a hex color (0-1)"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        return s

    def set_color_saturation(self, hex_color, saturation_percent):
        """Set the saturation of a hex color to an absolute percentage (0-100%)"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

        # Check if this is a grayscale color (R=G=B or very close)
        if abs(r - g) < 5 and abs(g - b) < 5 and abs(r - b) < 5:
            # For gray colors, just return the original color
            # Adjusting saturation doesn't make sense for pure grays
            return f'#{hex_color}'

        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        # Convert percentage to 0-1 range for colorsys
        s = saturation_percent / 100.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return f'#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}'

    def get_current_saturated_colors(self):
        """Return all colors with proper saturation applied"""
        return [self.set_color_saturation(self.original_colors[i],
                                          int(self.color_saturation[i] * 100)) for i in range(len(self.colors))]

    def setup_ui(self):
        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left control panel
        control_panel = QWidget()
        control_panel.setFixedWidth(400)
        control_layout = QVBoxLayout(control_panel)
        main_layout.addWidget(control_panel)

        # Right display panel
        display_panel = QWidget()
        display_layout = QVBoxLayout(display_panel)
        main_layout.addWidget(display_panel)

        # Title
        title = QLabel("Snake Illusion Generator")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        control_layout.addWidget(title)

        # Palette selector
        palette_frame = QFrame()
        palette_layout = QHBoxLayout(palette_frame)
        palette_layout.addWidget(QLabel("Color Palette:"))

        self.palette_combo = QComboBox()
        self.palette_combo.addItems(self.COLOR_PALETTES.keys())
        self.palette_combo.currentTextChanged.connect(self.apply_palette)
        palette_layout.addWidget(self.palette_combo)

        apply_palette_btn = QPushButton("Apply Palette")
        apply_palette_btn.clicked.connect(self.apply_palette)
        apply_palette_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        palette_layout.addWidget(apply_palette_btn)

        control_layout.addWidget(palette_frame)

        # Number of colors
        color_count_frame = QFrame()
        color_count_layout = QHBoxLayout(color_count_frame)
        color_count_layout.addWidget(QLabel("Number of Colors:"))

        self.radio_3_colors = QRadioButton("3")
        self.radio_4_colors = QRadioButton("4")
        self.radio_4_colors.setChecked(True)

        self.radio_3_colors.toggled.connect(lambda: self.set_num_colors(3))
        self.radio_4_colors.toggled.connect(lambda: self.set_num_colors(4))

        color_count_layout.addWidget(self.radio_3_colors)
        color_count_layout.addWidget(self.radio_4_colors)

        control_layout.addWidget(color_count_frame)

        # Pattern type selection
        pattern_type_frame = QFrame()
        pattern_type_layout = QHBoxLayout(pattern_type_frame)
        pattern_type_layout.addWidget(QLabel("Pattern Type:"))

        self.radio_reversed_pattern = QRadioButton("Complete Reversal")
        self.radio_classic_pattern = QRadioButton("Classic (Partial)")
        self.radio_reversed_pattern.setChecked(True)  # Default to complete reversal

        self.radio_reversed_pattern.toggled.connect(lambda: self.set_pattern_type(False))
        self.radio_classic_pattern.toggled.connect(lambda: self.set_pattern_type(True))

        pattern_type_layout.addWidget(self.radio_reversed_pattern)
        pattern_type_layout.addWidget(self.radio_classic_pattern)

        control_layout.addWidget(pattern_type_frame)

        # Background color
        # First row: Color button, Choose button, and Hex code
        bg_frame = QFrame()
        bg_layout = QHBoxLayout(bg_frame)
        bg_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        bg_layout.setSpacing(5)  # Reduce spacing
        bg_layout.addWidget(QLabel("Background:"))

        self.bg_color_btn = ColorButton(self.background_color)
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        bg_layout.addWidget(self.bg_color_btn)

        bg_choose_btn = QPushButton("Choose")
        bg_choose_btn.clicked.connect(self.choose_bg_color)
        bg_choose_btn.setFixedSize(80, 25)  # "Choose" button dimensions-can turn global
        bg_layout.addWidget(bg_choose_btn)

        self.bg_hex_value = QLabel(f"Hex: {self.background_color}")
        bg_layout.addWidget(self.bg_hex_value)

        control_layout.addWidget(bg_frame)

        # Second row: Transparency checkbox (indented)
        transparent_frame = QFrame()
        transparent_layout = QHBoxLayout(transparent_frame)
        transparent_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Add indentation spacing
        transparent_layout.addSpacing(20)  # Indentation space

        self.transparent_check = QCheckBox("Transparent")
        self.transparent_check.toggled.connect(self.toggle_transparent_bg)
        transparent_layout.addWidget(self.transparent_check)
        transparent_layout.addStretch(1)  # Fill remaining space

        control_layout.addWidget(transparent_frame)

        # Third row: Saturation
        bg_sat_frame = QFrame()
        bg_sat_layout = QHBoxLayout(bg_sat_frame)
        bg_sat_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        bg_sat_layout.setSpacing(5)  # Reduce spacing
        bg_sat_layout.addWidget(QLabel("BG Saturation:"))

        self.bg_sat_slider = QSlider(Qt.Horizontal)
        self.bg_sat_slider.setRange(0, 100)
        self.bg_sat_slider.setValue(int(self.background_saturation * 100))
        self.bg_sat_slider.valueChanged.connect(self.update_bg_saturation)
        bg_sat_layout.addWidget(self.bg_sat_slider)

        # Add spin box for background saturation
        self.bg_sat_spin = QSpinBox()
        self.bg_sat_spin.setRange(0, 100)
        self.bg_sat_spin.setValue(int(self.background_saturation * 100))
        self.bg_sat_spin.setSuffix("%")
        self.bg_sat_slider.valueChanged.connect(self.bg_sat_spin.setValue)
        self.bg_sat_spin.valueChanged.connect(self.bg_sat_slider.setValue)
        self.bg_sat_spin.valueChanged.connect(self.update_bg_saturation)
        bg_sat_layout.addWidget(self.bg_sat_spin)

        control_layout.addWidget(bg_sat_frame)

        # Color controls
        for i in range(4):
            # Create frame for this color
            color_frame = QFrame()
            color_layout = QVBoxLayout(color_frame)

            # Color selection row
            color_row = QHBoxLayout()
            color_row.addWidget(QLabel(f"Color {i + 1}:"))

            color_btn = ColorButton(self.colors[i])
            color_btn.clicked.connect(lambda checked, idx=i: self.choose_color(idx))
            self.color_buttons.append(color_btn)
            color_row.addWidget(color_btn)

            choose_btn = QPushButton("Choose")
            choose_btn.clicked.connect(lambda checked, idx=i: self.choose_color(idx))
            choose_btn.setFixedSize(80, 25)  # "Choose" button dimensions
            color_row.addWidget(choose_btn)

            # Add hex code display
            hex_value = QLabel(f"Hex: {self.colors[i]}")
            color_row.addWidget(hex_value)
            self.hex_values.append(hex_value)

            color_layout.addLayout(color_row)

            # Width control - Updated with slider and spinbox
            width_row = QHBoxLayout()
            width_row.addWidget(QLabel("Width:"))

            # Width slider (scaled by 10 for 0.1 precision)
            width_slider = QSlider(Qt.Horizontal)
            width_slider.setRange(10, 100)  # Represents 1.0 to 10.0
            width_slider.setValue(int(self.widths[i] * 10))
            width_slider.valueChanged.connect(lambda value, idx=i: self.update_width_from_slider(idx, value))
            self.width_sliders.append(width_slider)
            width_row.addWidget(width_slider)

            # Width spinbox for precise control
            width_spin = QDoubleSpinBox()
            width_spin.setRange(1.0, 10.0)
            width_spin.setValue(self.widths[i])
            width_spin.setSingleStep(0.1)
            width_spin.setDecimals(1)
            width_spin.valueChanged.connect(lambda value, idx=i: self.update_width_from_spinbox(idx, value))
            self.width_spins.append(width_spin)
            width_row.addWidget(width_spin)

            color_layout.addLayout(width_row)

            # Saturation control
            sat_row = QHBoxLayout()
            sat_row.addWidget(QLabel("Saturation:"))

            sat_slider = QSlider(Qt.Horizontal)
            sat_slider.setRange(0, 100)
            sat_slider.setValue(int(self.color_saturation[i] * 100))
            sat_slider.valueChanged.connect(lambda value, idx=i: self.update_color_saturation(idx, value))
            self.sat_sliders.append(sat_slider)
            sat_row.addWidget(sat_slider)

            # Add spin box for saturation
            sat_spin = QSpinBox()
            sat_spin.setRange(0, 100)
            sat_spin.setValue(int(self.color_saturation[i] * 100))
            sat_spin.setSuffix("%")
            sat_slider.valueChanged.connect(sat_spin.setValue)
            sat_spin.valueChanged.connect(sat_slider.setValue)
            sat_spin.valueChanged.connect(lambda value, idx=i: self.update_color_saturation(idx, value))
            self.sat_spins.append(sat_spin)
            sat_row.addWidget(sat_spin)

            color_layout.addLayout(sat_row)

            control_layout.addWidget(color_frame)
            self.color_frames.append(color_frame)

        # Pattern count
        pattern_frame = QFrame()
        pattern_layout = QHBoxLayout(pattern_frame)
        pattern_layout.addWidget(QLabel("Number of Patterns:"))

        self.pattern_slider = QSlider(Qt.Horizontal)
        self.pattern_slider.setRange(1, 50)
        self.pattern_slider.setValue(self.num_patterns)
        self.pattern_slider.valueChanged.connect(self.update_patterns)
        pattern_layout.addWidget(self.pattern_slider)

        self.pattern_spin = QSpinBox()
        self.pattern_spin.setRange(1, 50)
        self.pattern_spin.setValue(self.num_patterns)
        self.pattern_slider.valueChanged.connect(self.pattern_spin.setValue)
        self.pattern_spin.valueChanged.connect(self.pattern_slider.setValue)
        pattern_layout.addWidget(self.pattern_spin)

        control_layout.addWidget(pattern_frame)

        # Shift angle
        shift_frame = QFrame()
        shift_layout = QHBoxLayout(shift_frame)
        shift_layout.addWidget(QLabel("Shift Angle:"))

        self.shift_slider = QSlider(Qt.Horizontal)
        self.shift_slider.setRange(-300, 300)  # Scale by 10 for decimal precision
        self.shift_slider.setValue(int(self.shift_angle * 10))
        self.shift_slider.valueChanged.connect(self.update_shift_angle)
        shift_layout.addWidget(self.shift_slider)

        # Add QDoubleSpinBox for precise control
        self.shift_spin = QDoubleSpinBox()
        self.shift_spin.setRange(-30.0, 30.0)
        self.shift_spin.setValue(self.shift_angle)
        self.shift_spin.setSingleStep(0.1)  # Increment by 0.1
        self.shift_spin.setDecimals(1)  # Show 1 decimal place
        self.shift_spin.valueChanged.connect(self.update_shift_angle_from_spinbox)
        shift_layout.addWidget(self.shift_spin)

        control_layout.addWidget(shift_frame)

        # Control buttons
        button_frame = QFrame()
        button_layout = QVBoxLayout(button_frame)  # Create vertical layout

        # First row - illusion operations
        illusion_buttons = QHBoxLayout()
        generate_btn = QPushButton("Generate Illusion")
        generate_btn.clicked.connect(self.generate_illusion)
        generate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        illusion_buttons.addWidget(generate_btn)

        save_btn = QPushButton("Save Illusion")
        save_btn.clicked.connect(self.save_illusion)
        save_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        illusion_buttons.addWidget(save_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_settings)
        reset_btn.setStyleSheet("background-color: #F44336; color: white; font-weight: bold;")
        illusion_buttons.addWidget(reset_btn)

        button_layout.addLayout(illusion_buttons)

        # Second row - project operations
        project_buttons = QHBoxLayout()
        save_project_btn = QPushButton("Save Project")
        save_project_btn.clicked.connect(self.save_project)
        save_project_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        project_buttons.addWidget(save_project_btn)

        load_project_btn = QPushButton("Load Project")
        load_project_btn.clicked.connect(self.load_project)
        load_project_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        project_buttons.addWidget(load_project_btn)

        button_layout.addLayout(project_buttons)
        control_layout.addWidget(button_frame)

        # Preview label and save button in the same row
        preview_header = QWidget()
        preview_header_layout = QHBoxLayout(preview_header)
        preview_header_layout.setContentsMargins(0, 0, 0, 0)

        # Add stretch to push elements to center
        preview_header_layout.addStretch(1)

        # Preview label
        preview_label = QLabel("Pattern Preview (Left Circle)")
        preview_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        preview_header_layout.addWidget(preview_label)

        # Add minimal spacing between label and button
        preview_header_layout.addSpacing(5)

        # Save Preview button
        save_preview_btn = QPushButton("Save Pattern")
        save_preview_btn.clicked.connect(self.save_preview)
        save_preview_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        save_preview_btn.setFixedWidth(120)
        preview_header_layout.addWidget(save_preview_btn)

        # Add stretch to push elements to center
        preview_header_layout.addStretch(1)

        # Add the header to the main layout
        control_layout.addWidget(preview_header)

        # Preview canvas
        self.preview_frame = QWidget()
        self.preview_frame.setMinimumHeight(150)
        preview_frame_layout = QVBoxLayout(self.preview_frame)
        control_layout.addWidget(self.preview_frame)

        # Add stretch to push everything up
        control_layout.addStretch(1)

        # Main display canvas
        self.canvas_frame = QWidget()
        canvas_layout = QVBoxLayout(self.canvas_frame)
        display_layout.addWidget(self.canvas_frame)

        # Show initial colors
        self.set_num_colors(self.num_colors)

    def choose_bg_color(self):
        if self.transparent_bg:
            return

        color = QColorDialog.getColor(QColor(self.background_color), self, "Choose Background Color")
        if color.isValid():
            self.background_color = color.name()
            self.bg_color_btn.set_color(self.background_color)
            self.background_saturation = self.get_color_saturation(self.background_color)
            self.bg_sat_slider.setValue(int(self.background_saturation * 100))
            self.bg_sat_spin.setValue(int(self.background_saturation * 100))
            self.bg_hex_value.setText(f"Hex: {self.background_color}")
            self.update_preview()

    def choose_color(self, idx):
        color = QColorDialog.getColor(QColor(self.colors[idx]), self, f"Choose Color {idx + 1}")
        if color.isValid():
            self.original_colors[idx] = color.name()
            self.colors[idx] = color.name()
            self.color_buttons[idx].set_color(color.name())
            self.color_saturation[idx] = self.get_color_saturation(color.name())
            self.sat_sliders[idx].setValue(int(self.color_saturation[idx] * 100))
            self.sat_spins[idx].setValue(int(self.color_saturation[idx] * 100))
            self.hex_values[idx].setText(f"Hex: {color.name()}")
            self.update_preview()

    def toggle_transparent_bg(self, checked):
        self.transparent_bg = checked
        self.bg_color_btn.setEnabled(not checked)
        self.bg_sat_slider.setEnabled(not checked)
        self.bg_sat_spin.setEnabled(not checked)
        self.update_preview()

    def update_bg_saturation(self, value):
        # Value is now 0-100
        self.background_saturation = value / 100.0  # Store internally as 0-1
        adjusted_color = self.set_color_saturation(self.background_color, value)
        self.bg_color_btn.set_color(adjusted_color)
        self.bg_hex_value.setText(f"Hex: {adjusted_color}")
        self.update_preview()

    def update_color_saturation(self, idx, value):
        # Value is now 0-100
        self.color_saturation[idx] = value / 100.0  # Store internally as 0-1
        adjusted_color = self.set_color_saturation(self.original_colors[idx], value)
        self.colors[idx] = adjusted_color
        self.color_buttons[idx].set_color(adjusted_color)
        self.hex_values[idx].setText(f"Hex: {adjusted_color}")
        self.update_preview()

    def update_width_from_slider(self, idx, value):
        """Update width from slider (scaled by 10)"""
        self.widths[idx] = float(value) / 10.0

        # Update spinbox without triggering its valueChanged signal
        self.width_spins[idx].blockSignals(True)
        self.width_spins[idx].setValue(self.widths[idx])
        self.width_spins[idx].blockSignals(False)

        self.update_preview()

    def update_width_from_spinbox(self, idx, value):
        """Update width from spinbox"""
        self.widths[idx] = value

        # Update slider without triggering its valueChanged signal
        self.width_sliders[idx].blockSignals(True)
        self.width_sliders[idx].setValue(int(self.widths[idx] * 10))
        self.width_sliders[idx].blockSignals(False)

        self.update_preview()

    def update_width(self, idx, value):
        """Legacy method for compatibility"""
        self.widths[idx] = float(value)
        self.update_preview()

    def update_patterns(self, value):
        self.num_patterns = value
        self.update_preview()

    def update_shift_angle(self, value):
        """Update shift angle from slider (scaled by 10)"""
        self.shift_angle = float(value) / 10.0

        # Update spinbox without triggering its valueChanged signal
        self.shift_spin.blockSignals(True)
        self.shift_spin.setValue(self.shift_angle)
        self.shift_spin.blockSignals(False)

        self.update_preview()

    def update_shift_angle_from_spinbox(self, value):
        """Update shift angle from spinbox"""
        self.shift_angle = value

        # Update slider without triggering its valueChanged signal
        self.shift_slider.blockSignals(True)
        self.shift_slider.setValue(int(self.shift_angle * 10))
        self.shift_slider.blockSignals(False)

        self.update_preview()

    def set_num_colors(self, count):
        self.num_colors = count
        for i, frame in enumerate(self.color_frames):
            frame.setVisible(i < count)

        # Hide classic pattern option for 3 colors since classic Snake Illusion uses 4 colors
        if count == 3:
            self.radio_classic_pattern.setVisible(False)
            if self.use_classic_pattern:
                # If classic was selected, switch to reversed
                self.use_classic_pattern = False
                self.radio_reversed_pattern.setChecked(True)
        else:
            self.radio_classic_pattern.setVisible(True)

        self.update_preview()

    def set_pattern_type(self, is_classic):
        self.use_classic_pattern = is_classic
        self.update_preview()

    def apply_palette(self):
        palette_name = self.palette_combo.currentText()
        palette = self.COLOR_PALETTES[palette_name]

        for i in range(len(palette)):
            if i < 4:
                self.original_colors[i] = palette[i]
                self.colors[i] = palette[i]
                self.color_buttons[i].set_color(palette[i])
                self.color_saturation[i] = self.get_color_saturation(palette[i])
                self.sat_sliders[i].setValue(int(self.color_saturation[i] * 100))
                self.sat_spins[i].setValue(int(self.color_saturation[i] * 100))
                self.hex_values[i].setText(f"Hex: {palette[i]}")

        # Set appropriate background color
        background_color = "#808080"  # Default gray
        if palette_name == "Vibrant":
            background_color = "#FFFFFF"
        elif palette_name == "Pastel":
            background_color = "#F0F0F0"
        elif palette_name == "Monochrome":
            background_color = "#FFFFFF"
        elif palette_name == "Earthy":
            background_color = "#F5F5DC"
        elif palette_name == "Cool":
            background_color = "#F0F8FF"
        elif palette_name == "Warm":
            background_color = "#FFFAF0"

        self.background_color = background_color
        self.bg_color_btn.set_color(background_color)
        self.background_saturation = self.get_color_saturation(background_color)
        self.bg_sat_slider.setValue(int(self.background_saturation * 100))
        self.bg_sat_spin.setValue(int(self.background_saturation * 100))
        self.bg_hex_value.setText(f"Hex: {background_color}")

        self.update_preview()

    def update_preview(self):
        try:
            # Generate preview pattern
            pattern = self.widths[:self.num_colors]
            colors = self.get_current_saturated_colors()[:self.num_colors]

            # Determine background color
            if self.transparent_bg:
                bg_color = None
            else:
                # Use the properly saturated background color
                bg_color = self.set_color_saturation(self.background_color,
                                                     int(self.background_saturation * 100))
                self.bg_display_color = bg_color  # Store for consistency

            # Generate preview
            fig = self.generate_preview(pattern, self.num_patterns, colors, bg_color, self.shift_angle)

            # Close previous figure if it exists
            if self.preview_figure is not None:
                plt.close(self.preview_figure)

            self.preview_figure = fig

            # Clear previous canvas
            for i in reversed(range(self.preview_frame.layout().count())):
                widget = self.preview_frame.layout().itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Create new canvas
            canvas = FigureCanvas(fig)
            self.preview_frame.layout().addWidget(canvas)

        except Exception as e:
            print(f"Preview error: {e}")

    def generate_illusion(self):
        try:
            # Get current values with proper saturation
            pattern = self.widths[:self.num_colors]
            colors = self.get_current_saturated_colors()[:self.num_colors]

            # Determine background color
            if self.transparent_bg:
                bg_color = None
            else:
                # Use the properly saturated background color
                bg_color = self.set_color_saturation(self.background_color,
                                                     int(self.background_saturation * 100))

            # Generate full illusion
            fig = self.generate_full_illusion(pattern, self.num_patterns, colors, bg_color, self.shift_angle)

            # Close previous figure if it exists
            if self.current_figure is not None:
                plt.close(self.current_figure)

            self.current_figure = fig

            # Clear previous canvas
            for i in reversed(range(self.canvas_frame.layout().count())):
                widget = self.canvas_frame.layout().itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            # Create new canvas
            canvas = FigureCanvas(fig)
            self.canvas_frame.layout().addWidget(canvas)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating illusion: {e}")

    def save_illusion(self):
        if self.current_figure is None:
            QMessageBox.information(self, "Info", "Generate an illusion first")
            return

        try:
            # Generate filename with all parameters
            colors_str = '-'.join([self.colors[i].replace('#', '') for i in range(self.num_colors)])
            saturations_str = '-'.join([f"{int(self.color_saturation[i] * 100)}" for i in range(self.num_colors)])
            widths_str = '-'.join([f"{self.widths[i]:.1f}" for i in range(self.num_colors)])

            if self.num_colors == 3:
                colors_str += "-X"
                saturations_str += "-X"
                widths_str += "-X"

            # Add background specification - either transparent or hex code
            if self.transparent_bg:
                bg_str = "bg-transparent"
            else:
                # Get the actual background color with saturation applied
                actual_bg = self.set_color_saturation(self.background_color,
                                                      int(self.background_saturation * 100))
                bg_str = f"bg-{actual_bg.replace('#', '')}"

            # Add pattern type to filename
            pattern_type_str = "classic" if self.use_classic_pattern else "reversed"

            # Updated filename format with pattern type
            default_filename = (f"snake_illusion_p{self.num_patterns}_c{colors_str}_"
                                f"s{saturations_str}_w{widths_str}_a{self.shift_angle:.1f}_{bg_str}_{pattern_type_str}.png")

            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Illusion", default_filename, "PNG Files (*.png);;All Files (*)"
            )

            if file_path:
                self.current_figure.savefig(file_path, dpi=100, bbox_inches='tight',
                                            pad_inches=0, transparent=self.transparent_bg)
                QMessageBox.information(self, "Success", f"File saved as: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving file: {e}")

    def save_preview(self):
        """Save the current preview pattern as an image"""
        if self.preview_figure is None:
            QMessageBox.information(self, "Info", "No preview available to save")
            return

        try:
            # Generate filename with parameters
            colors_str = '-'.join([self.colors[i].replace('#', '') for i in range(self.num_colors)])
            saturations_str = '-'.join([f"{int(self.color_saturation[i] * 100)}" for i in range(self.num_colors)])
            widths_str = '-'.join([f"{self.widths[i]:.1f}" for i in range(self.num_colors)])

            if self.num_colors == 3:
                colors_str += "-X"
                saturations_str += "-X"
                widths_str += "-X"

            # Filename for preview
            default_filename = (f"single_pattern_c{colors_str}_"
                                f"s{saturations_str}_w{widths_str}.png")

            # Get save path
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Preview", default_filename, "PNG Files (*.png);;All Files (*)"
            )

            if file_path:
                # Create a new figure with the same pattern but transparent background
                pattern = self.widths[:self.num_colors]
                colors = self.get_current_saturated_colors()[:self.num_colors]

                # Generate a transparent version of the preview
                temp_fig = self.generate_preview(pattern, self.num_patterns, colors, None, self.shift_angle)

                # Save with transparent background to extract only the pattern
                temp_fig.savefig(file_path, dpi=100, bbox_inches='tight',
                                 pad_inches=0, transparent=True)

                # Close the temporary figure
                plt.close(temp_fig)

                QMessageBox.information(self, "Success", f"Pattern-only preview saved as: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving preview: {e}")

    def reset_settings(self):
        # Reset all settings to defaults
        self.background_color = "#808080"
        self.bg_color_btn.set_color(self.background_color)
        self.background_saturation = 0.0
        self.bg_sat_slider.setValue(0)
        self.bg_sat_spin.setValue(0)
        self.bg_hex_value.setText(f"Hex: {self.background_color}")

        self.num_patterns = 24
        self.pattern_slider.setValue(self.num_patterns)
        self.pattern_spin.setValue(self.num_patterns)

        self.shift_angle = -12.5
        self.shift_slider.setValue(int(self.shift_angle * 10))
        self.shift_spin.setValue(self.shift_angle)

        self.num_colors = 4
        self.radio_4_colors.setChecked(True)
        self.set_num_colors(4)

        self.use_classic_pattern = False
        self.radio_reversed_pattern.setChecked(True)

        self.transparent_bg = False
        self.transparent_check.setChecked(False)
        self.bg_color_btn.setEnabled(True)
        self.bg_sat_slider.setEnabled(True)
        self.bg_sat_spin.setEnabled(True)

        # Reset palette
        self.palette_combo.setCurrentText("Classic")

        # Reset colors
        default_colors = self.COLOR_PALETTES["Classic"]
        for i in range(4):
            self.original_colors[i] = default_colors[i]
            self.colors[i] = default_colors[i]
            self.color_buttons[i].set_color(default_colors[i])
            self.color_saturation[i] = self.get_color_saturation(default_colors[i])
            self.sat_sliders[i].setValue(int(self.color_saturation[i] * 100))
            self.sat_spins[i].setValue(int(self.color_saturation[i] * 100))
            self.hex_values[i].setText(f"Hex: {default_colors[i]}")
            self.widths[i] = 1.0
            self.width_sliders[i].setValue(10)  # Updated for scaled slider
            self.width_spins[i].setValue(1.0)  # Reset width spinbox

        QMessageBox.information(self, "Reset", "All settings reset to defaults")
        self.update_preview()

    def generate_preview(self, pattern, num_patterns, colors, background, shift_angle):
        """Generate a simple preview of the pattern showing all colors, properly centered vertically"""
        # Create a compact figure
        fig, ax = plt.subplots(figsize=(4, 2))

        # Only use the colors we need based on num_colors
        colors_to_use = colors[:self.num_colors]
        pattern_to_use = pattern[:self.num_colors]

        # Create a simple horizontal bar chart
        bar_height = 0.5
        total_width = 0.8  # Fixed total width

        # Calculate position for each bar
        positions = []
        current_pos = 0.1  # Start at 0.1 to leave some margin

        # Calculate relative widths
        total_pattern = sum(pattern_to_use)
        for width in pattern_to_use:
            relative_width = (width / total_pattern) * total_width
            positions.append((current_pos, relative_width))
            current_pos += relative_width

        # Draw the bars - use y=0 to center vertically
        for i, (pos, width) in enumerate(positions):
            ax.barh(0, width=width, left=pos, height=bar_height, color=colors_to_use[i])

        # Configure plot - set y limits to center the bar vertically
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.25, 0.25)  # Center the bar vertically
        ax.set_aspect('auto')

        # Set background
        if background is None:  # Transparent
            fig.patch.set_alpha(0.0)
            ax.set_facecolor('none')
        else:
            fig.patch.set_facecolor(background)
            ax.set_facecolor(background)

        ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        return fig

    def generate_full_illusion(self, width_pattern, pattern_repeats, left_colors, background, shift_angle):
        """Generate the full snake illusion"""
        # Create the repeating pattern for left circle (original)
        colors_length = len(left_colors)
        left_pattern_widths = width_pattern * pattern_repeats

        # Setup figure
        fig, ax = plt.subplots(figsize=(8, 6))
        inner_r = np.array(np.linspace(1, 0.03, num=9)) * 2
        x = 2

        # Left circle (original pattern)
        startangle = 90
        for radius in range(len(inner_r)):
            startangle += shift_angle
            left_color_list = left_colors * pattern_repeats
            ax.pie(left_pattern_widths, colors=left_color_list, radius=inner_r[radius],
                   center=(-x, 0), startangle=startangle, counterclock=False)

        # Left center circle
        center_color = ['none'] if background is None else [background]
        ax.pie([1], colors=center_color, radius=inner_r[8],
               center=(-x, 0), counterclock=False)

        # Generate right circle pattern based on pattern type
        if self.use_classic_pattern:
            # Safety check: Classic pattern only works with 4 colors
            if colors_length != 4:
                print(f"Warning: Classic pattern requires 4 colors, got {colors_length}")

            # Classic: swap colors and widths [0,1,2,3] -> [0,3,2,1]
            right_colors = [left_colors[0], left_colors[3], left_colors[2], left_colors[1]]
            right_width_pattern = [width_pattern[0], width_pattern[3], width_pattern[2], width_pattern[1]]
            right_pattern_widths = right_width_pattern * pattern_repeats
        else:
            # Complete reversal: reverse everything
            right_colors = left_colors[::-1]
            right_pattern_widths = left_pattern_widths[::-1]

        # Right circle
        startangle = 90  # Reset startangle
        for radius in range(len(inner_r)):
            startangle += shift_angle
            right_color_list = right_colors * pattern_repeats
            ax.pie(right_pattern_widths, colors=right_color_list, radius=inner_r[radius],
                   center=(x, 0), startangle=startangle, counterclock=False)

        # Right center circle
        ax.pie([1], colors=center_color, radius=inner_r[8],
               center=(x, 0), counterclock=False)

        # Background and display settings
        if background is None:
            fig.patch.set_alpha(0.0)
        else:
            fig.patch.set_facecolor(background)

        plt.xlim([-2.5, 2.5])
        plt.ylim([-2.5, 2.5])
        plt.axis('off')
        return fig

    def adjust_color_saturation(self, hex_color, saturation):
        """Legacy method for compatibility - uses set_color_saturation with percentage conversion"""
        return self.set_color_saturation(hex_color, saturation * 100)

    def closeEvent(self, event):
        """Clean up when window is closed"""
        plt.close('all')
        event.accept()

    def save_project(self):
        """Save the current configuration to a JSON file with naming matching the illusion format"""
        try:
            # Create a dictionary with all current settings
            project_data = {
                "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "app_version": "1.0.0",
                "background": {
                    "color": self.background_color,
                    "saturation": self.background_saturation,
                    "transparent": self.transparent_bg
                },
                "colors": self.original_colors[:self.num_colors],
                "saturations": [s * 100 for s in self.color_saturation[:self.num_colors]],  # Save as percentages
                "widths": [w for w in self.widths[:self.num_colors]],
                "num_patterns": self.num_patterns,
                "shift_angle": self.shift_angle,
                "num_colors": self.num_colors,
                "use_classic_pattern": self.use_classic_pattern
            }

            # Generate filename with all parameters - matching the illusion naming convention
            colors_str = '-'.join([self.colors[i].replace('#', '') for i in range(self.num_colors)])
            saturations_str = '-'.join([f"{int(self.color_saturation[i] * 100)}" for i in range(self.num_colors)])
            widths_str = '-'.join([f"{self.widths[i]:.1f}" for i in range(self.num_colors)])

            if self.num_colors == 3:
                colors_str += "-X"
                saturations_str += "-X"
                widths_str += "-X"

            # Add background specification - either transparent or hex code
            if self.transparent_bg:
                bg_str = "bg-transparent"
            else:
                # Get the actual background color with saturation applied
                actual_bg = self.set_color_saturation(self.background_color,
                                                      int(self.background_saturation * 100))
                bg_str = f"bg-{actual_bg.replace('#', '')}"

            # Use the same format as illusion filenames, but with .json extension
            pattern_type_str = "classic" if self.use_classic_pattern else "reversed"
            default_filename = (f"snake_illusion_p{self.num_patterns}_c{colors_str}_"
                                f"s{saturations_str}_w{widths_str}_a{self.shift_angle:.1f}_{bg_str}_{pattern_type_str}.json")

            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Project", default_filename, "JSON Files (*.json);;All Files (*)"
            )

            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(project_data, f, indent=2)
                QMessageBox.information(self, "Success", f"Project saved as: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving project: {e}")

    def load_project(self):
        """Load configuration from a JSON file"""
        try:
            # Get file path
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Load Project", "", "JSON Files (*.json);;All Files (*)"
            )

            if not file_path:
                return

            # Read project data
            with open(file_path, 'r') as f:
                project_data = json.load(f)

            # Apply background settings
            bg_data = project_data["background"]
            self.background_color = bg_data["color"]
            self.background_saturation = bg_data["saturation"]
            self.transparent_bg = bg_data["transparent"]

            # Update UI for background
            self.bg_color_btn.set_color(self.background_color)
            self.bg_sat_slider.setValue(int(self.background_saturation * 100))
            self.bg_sat_spin.setValue(int(self.background_saturation * 100))
            self.bg_hex_value.setText(f"Hex: {self.background_color}")
            self.transparent_check.setChecked(self.transparent_bg)
            self.bg_color_btn.setEnabled(not self.transparent_bg)
            self.bg_sat_slider.setEnabled(not self.transparent_bg)
            self.bg_sat_spin.setEnabled(not self.transparent_bg)

            # Apply color settings
            self.num_colors = project_data["num_colors"]
            if self.num_colors == 3:
                self.radio_3_colors.setChecked(True)
            else:
                self.radio_4_colors.setChecked(True)

            colors = project_data["colors"]
            saturations = project_data["saturations"]
            widths = project_data["widths"]

            for i in range(len(colors)):
                self.original_colors[i] = colors[i]
                self.color_saturation[i] = saturations[i] / 100.0  # Convert from percentage to 0-1
                self.widths[i] = widths[i]

                # Update controls
                adjusted_color = self.set_color_saturation(colors[i], saturations[i])
                self.colors[i] = adjusted_color
                self.color_buttons[i].set_color(adjusted_color)
                self.hex_values[i].setText(f"Hex: {adjusted_color}")
                self.sat_sliders[i].setValue(int(saturations[i]))
                self.sat_spins[i].setValue(int(saturations[i]))

                # Update width controls (both slider and spinbox)
                self.width_sliders[i].setValue(int(widths[i] * 10))  # Scaled for slider
                self.width_spins[i].setValue(widths[i])  # Direct value for spinbox

            # Apply other settings
            self.num_patterns = project_data["num_patterns"]
            self.pattern_slider.setValue(self.num_patterns)
            self.pattern_spin.setValue(self.num_patterns)

            self.shift_angle = project_data["shift_angle"]
            self.shift_slider.setValue(int(self.shift_angle * 10))
            self.shift_spin.setValue(self.shift_angle)

            # Apply pattern type setting
            self.use_classic_pattern = project_data.get("use_classic_pattern", False)
            if self.use_classic_pattern:
                self.radio_classic_pattern.setChecked(True)
            else:
                self.radio_reversed_pattern.setChecked(True)

            # Show the first num_colors color frames
            self.set_num_colors(self.num_colors)

            # Update the preview
            self.update_preview()

            QMessageBox.information(self, "Success", f"Project loaded from: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading project: {e}")


# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnakeIllusionApp()
    window.show()
    sys.exit(app.exec_())