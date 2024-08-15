# COD:MWR Server Configuration Tool

## Description

This tool is a graphical user interface (GUI) application designed to simplify the process of configuring Call of Duty: Modern Warfare Remastered (MWR) dedicated servers. It provides an easy-to-use interface for modifying server settings, managing game modes, customizing map rotations, and adding custom DVars (Dynamic Variables).

## Features

- **General Server Settings**: Easily configure basic server parameters such as server name, password, max clients, timeout, and RCON password.
- **Game Mode Configuration**: Separate tabs for each game mode (FFA, TDM, KC, DOM, S&D, SAB) allow fine-tuning of mode-specific settings.
- **Custom DVars**: Add, edit, and remove custom DVars to extend server functionality.
- **Map Rotation Management**: 
  - Add and remove maps from the rotation
  - Reorder maps within the rotation
  - Randomize map selection for a chosen game mode
  - View the current number of maps in the rotation
- **Server Name Colorization**: Apply color codes to the server name for enhanced visibility in the server browser.
- **Configuration File Handling**: 
  - Load existing configurations from `server.cfg`
  - Generate new configurations based on user input
  - Save modifications back to `server.cfg`

## Requirements

- Python 3.x
- ttkbootstrap library

## Installation

1. Ensure Python 3.x is installed on your system.
2. Install the required library: pip install ttkbootstrap
3. Place the script in the same directory as your `server.cfg` and `maps.txt` files.

## Usage

1. Run the script: python server_config_tool.py
2. Use the GUI to modify server settings, game modes, map rotations, and custom DVars.
3. Click the "Save Config" button to apply your changes to the `server.cfg` file.

## File Structure

- `server_config_tool.py`: The main Python script containing the configuration tool code.
- `server.cfg`: The server configuration file that will be read from and written to.
- `maps.txt`: A file containing the list of available maps, categorized by H2M, MW2CR, MWR, MW2.

## Notes

- Always backup your original `server.cfg` file before making changes.
- The tool assumes a specific format for the `maps.txt` file. Ensure it's properly formatted for correct map loading.
- Custom DVars are added to a specific section in the configuration file, marked by a comment.

## Contributing

Contributions to improve the tool are welcome. Please feel free to submit pull requests or open issues for bugs and feature requests.
