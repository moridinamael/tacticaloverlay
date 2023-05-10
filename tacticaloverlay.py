# -*- coding: utf-8 -*-
"""
Created on Tue May  9 14:58:58 2023

@author: mfreeman
"""

import mss
import openai
import base64
from io import BytesIO
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import pyautogui
from PIL import Image
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtGui import QIcon
import subprocess

class TacticalOverlayApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Initialize components
        self.init_ui()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_screen_analysis)
        self.timer.start(1000)  # Update interval in milliseconds

        # Set attributes and flags for click-through and translucency
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Set the window to fullscreen
        self.showFullScreen()

    def init_ui(self):
        # Create and configure UI components
        self.setWindowOpacity(0.5)
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Tactical Overlay')

        # Create a grid layout and set it as the layout for the widget
        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)

    def update_overlay(self, recommendations):
        # Remove existing buttons
        for child in self.findChildren(QtWidgets.QPushButton):
            child.setParent(None)

        # Add new buttons for recommendations
        for rec, position in recommendations:  # Process the tuple of button text and position
            rec = rec.strip()
            button = QtWidgets.QPushButton(rec, self)
            button.clicked.connect(lambda _, r=rec: self.execute_action(r))

            # Set button color, border, and size
            button.setStyleSheet("background-color: #007BFF; color: white; border: 1px solid black;")

            # Measure the text width and set the button size accordingly
            font_metrics = QFontMetrics(button.font())
            text_width = font_metrics.width(rec)
            button.setFixedSize(text_width + 20, 50)  # Add some padding to the width

            # Add the button to the grid layout using the row and column information from the position tuple
            row, col = position
            self.grid_layout.addWidget(button, row, col)


    def capture_screen_state(self):
        # Capture screen state as an image
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGBA", screenshot.size, screenshot.bgra)

            img_bytes = BytesIO()
            img.save(img_bytes, format="PNG")
            return base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    def analyze_screen_using_gpt4(self, image_data, context=None):
        # Send screen image to GPT-4 API and retrieve analysis
        # Stub: Call the GPT-4 multimodal API using the image_data as input
        # Replace with actual API call when available. We do not yet know what 
        # the API will look like, so this is just a stub.
        skiptrue = False
        if skiptrue:
            openai.api_key = "your_openai_api_key_here"
            response = openai.Completion.create(
                engine="image-gpt4",
                image = image_data,
                prompt = context,
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.0,
            )
            return response.choices[0].text.strip()
        else:
            # This is a stub that returns a hardcoded response with button text and row/column.
            # The idea here is that the GPT-4 API will return a list of tuples, each containing
            # the button text and the row/column position of the button, so that the overlay can
            # be updated accordingly, with buttons placed near the corresponding objects on the screen.
            return [
            (f"Open file: {os.path.join(os.getcwd(), 'example.txt')}", (3, 2)),
            ("Open MS Paint", (4, 1))
        ]

    def update_screen_analysis(self):
        # Capture screen state, analyze it, and update the overlay
        image_data = self.capture_screen_state()
        recommendations = self.analyze_screen_using_gpt4(image_data)
        self.update_overlay(recommendations)

    def execute_action(self, action):
        # Execute the corresponding action using pyautogui
        if action.startswith("Open file:"):
            file_path = action.replace("Open file:", "").strip()
            pyautogui.hotkey('win', 'r')  # Open Run dialog
            pyautogui.typewrite(file_path)
            pyautogui.press('enter')  # Open the file
        elif action == "Open MS Paint":
            subprocess.run("mspaint")  # Open MS Paint

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setWindowIcon(QIcon('thumbnail.ico'))  # Set the icon
    tactical_overlay = TacticalOverlayApp()
    tactical_overlay.show()
    app.exec_()