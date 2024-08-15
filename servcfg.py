import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, simpledialog
import configparser
import re
import random

class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("COD:MWR Server Config Editor")
        self.master.geometry("800x800")

        self.config = {}
        self.custom_dvars = {}
        self.maps = self.load_maps()
        self.map_rotation = []
        
        # Load default config
        default_config = self.generate_default_config()
        for line in default_config.split('\n'):
            if line.strip().startswith('set '):
                key, value = re.match(r'set\s+(\S+)\s+"?([^"]*)"?', line).groups()
                self.config[key] = value
    
        # Then load from file, overwriting defaults if file exists
        self.load_config()

        self.create_widgets()
        self.update_map_count()

    def load_maps(self):
        try:
            with open("maps.txt", "r") as f:
                lines = f.readlines()
            
            maps = {}
            current_category = ""
            for line in lines:
                line = line.strip()
                if line.endswith("ROTATION LIST"):
                    current_category = line.split(" ")[0]
                    maps[current_category] = []
                elif " - " in line:
                    map_name, map_code = line.split(" - ")
                    maps[current_category].append((map_name.strip(), map_code.strip()))
            return maps
        except FileNotFoundError:
            messagebox.showerror("Error", "maps.txt file not found!")
            return {}

    def load_config(self):
        try:
            with open("server.cfg", "r") as f:
                content = f.read()
                
            custom_section = False
            for line in content.split('\n'):
                if line.strip() == "// CUSTOM DVARS H2M CFG EDITOR //":
                    custom_section = True
                    continue
                if line.strip().startswith('set '):
                    key, value = re.match(r'set\s+(\S+)\s+"?([^"]*)"?', line).groups()
                    if custom_section:
                        self.custom_dvars[key] = value
                    else:
                        self.config[key] = value
                        if key == "sv_maprotation":
                            self.parse_map_rotation(value)
        except FileNotFoundError:
            # If file doesn't exist, we'll generate the config
            pass

    def parse_map_rotation(self, rotation_string):
        parts = rotation_string.split()
        i = 0
        while i < len(parts):
            if parts[i] == "gametype":
                gametype = parts[i+1]
                i += 2
            elif parts[i] == "map":
                self.map_rotation.append((gametype, parts[i+1]))
                i += 2
            else:
                i += 1

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.create_general_tab()
        self.create_gametype_tabs()
        self.create_custom_dvar_tab()
        self.create_map_rotation_tab()

        save_button = ttk.Button(self.master, text="Save Config", command=self.save_config, style='success.TButton')
        save_button.pack(pady=10)

    def create_general_tab(self):
        general_frame = ttk.Frame(self.notebook)
        self.notebook.add(general_frame, text="General")

        # Server name with color selection
        ttk.Label(general_frame, text="Server Name").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.server_name_entry = ttk.Entry(general_frame, width=40)
        self.server_name_entry.insert(0, self.config.get("sv_hostname", ""))
        self.server_name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.color_var = ttk.StringVar()
        color_dropdown = ttk.Combobox(general_frame, textvariable=self.color_var, width=10)
        color_dropdown['values'] = ('No Color', 'Red', 'Green', 'Yellow', 'Blue', 'Cyan', 'Pink', 'White', 'Team Color', 'Dark Red', 'Black', 'Rainbow')
        color_dropdown.current(0)
        color_dropdown.grid(row=0, column=2, padx=5, pady=5)
        color_dropdown.bind('<<ComboboxSelected>>', self.add_color_to_name)

        self.config["sv_hostname"] = self.server_name_entry

        other_settings = [
            ("Password", "g_password"),
            ("Max Clients", "sv_maxclients"),
            ("Timeout", "sv_timeout"),
            ("Inactivity Kick", "g_inactivity"),
            ("RCON Password", "rcon_password"),
        ]

        for i, (label, key) in enumerate(other_settings, start=1):
            ttk.Label(general_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = ttk.Entry(general_frame, width=40)
            entry.insert(0, self.config.get(key, ""))
            entry.grid(row=i, column=1, columnspan=2, padx=5, pady=5)
            self.config[key] = entry

    def add_color_to_name(self, event):
        color_codes = {
            'No Color': '', 'Red': '^1', 'Green': '^2', 'Yellow': '^3', 'Blue': '^4',
            'Cyan': '^5', 'Pink': '^6', 'White': '^7', 'Team Color': '^8',
            'Dark Red': '^9', 'Black': '^0', 'Rainbow': '^:'
        }
        selected_color = self.color_var.get()
        current_name = self.server_name_entry.get()
        
        # Remove any existing color codes
        clean_name = re.sub(r'\^[0-9:]', '', current_name)
        
        # Add new color code
        new_name = f"{color_codes[selected_color]}{clean_name}"
        self.server_name_entry.delete(0, END)
        self.server_name_entry.insert(0, new_name)

    def create_gametype_tabs(self):
        gametypes = [
            ("dm", "FFA"),
            ("war", "TDM"),
            ("conf", "KC"),
            ("dom", "DOM"),
            ("sd", "S&D"),
            ("sab", "SAB")
        ]
        
        for gametype, label in gametypes:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=label)

            settings = [
                ("Score Limit", f"scr_{gametype}_scorelimit"),
                ("Time Limit", f"scr_{gametype}_timelimit"),
                ("Player Respawn Delay", f"scr_{gametype}_playerrespawndelay"),
                ("Number of Lives", f"scr_{gametype}_numlives"),
                ("Round Limit", f"scr_{gametype}_roundlimit"),
                ("Win Limit", f"scr_{gametype}_winlimit"),
            ]

            for i, (setting_label, key) in enumerate(settings):
                ttk.Label(frame, text=setting_label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
                entry = ttk.Entry(frame, width=40)
                entry.insert(0, self.config.get(key, ""))
                entry.grid(row=i, column=1, padx=5, pady=5)
                self.config[key] = entry

    def create_custom_dvar_tab(self):
        custom_frame = ttk.Frame(self.notebook)
        self.notebook.add(custom_frame, text="Custom DVars")

        # Create a frame for the list of custom DVars
        list_frame = ttk.Frame(custom_frame)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Create a scrollable list of custom DVars
        self.dvar_listbox = ttk.Treeview(list_frame, columns=("Name", "Value"), show="headings")
        self.dvar_listbox.heading("Name", text="Name")
        self.dvar_listbox.heading("Value", text="Value")
        self.dvar_listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.dvar_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.dvar_listbox.configure(yscrollcommand=scrollbar.set)

        # Load existing custom DVars
        for key, value in self.custom_dvars.items():
            self.dvar_listbox.insert("", END, values=(key, value))

        # Create input fields for new DVars
        input_frame = ttk.Frame(custom_frame)
        input_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.dvar_name_entry = ttk.Entry(input_frame)
        self.dvar_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Value:").grid(row=0, column=2, padx=5, pady=5)
        self.dvar_value_entry = ttk.Entry(input_frame)
        self.dvar_value_entry.grid(row=0, column=3, padx=5, pady=5)

        # Create buttons for adding, editing, and removing DVars
        button_frame = ttk.Frame(custom_frame)
        button_frame.pack(fill=X, padx=10, pady=10)

        add_button = ttk.Button(button_frame, text="Add DVar", command=self.add_dvar)
        add_button.pack(side=LEFT, padx=5)

        edit_button = ttk.Button(button_frame, text="Edit DVar", command=self.edit_dvar)
        edit_button.pack(side=LEFT, padx=5)

        remove_button = ttk.Button(button_frame, text="Remove DVar", command=self.remove_dvar)
        remove_button.pack(side=LEFT, padx=5)

    def create_map_rotation_tab(self):
        rotation_frame = ttk.Frame(self.notebook)
        self.notebook.add(rotation_frame, text="Map Rotation")

        # Create a frame for the list of maps in rotation
        list_frame = ttk.Frame(rotation_frame)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.rotation_listbox = ttk.Treeview(list_frame, columns=("Gametype", "Map"), show="headings")
        self.rotation_listbox.heading("Gametype", text="Gametype")
        self.rotation_listbox.heading("Map", text="Map")
        self.rotation_listbox.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.rotation_listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.rotation_listbox.configure(yscrollcommand=scrollbar.set)

        # Load existing map rotation
        for gametype, map_code in self.map_rotation:
            map_name = next((name for category in self.maps.values() for name, code in category if code == map_code), map_code)
            self.rotation_listbox.insert("", END, values=(gametype, map_name))

        # Add a label to show the number of maps in rotation
        self.map_count_label = ttk.Label(rotation_frame, text="Maps in rotation: 0")
        self.map_count_label.pack(pady=5)

        # Create input fields for adding maps to rotation
        input_frame = ttk.Frame(rotation_frame)
        input_frame.pack(fill=X, padx=10, pady=10)

        ttk.Label(input_frame, text="Gametype:").grid(row=0, column=0, padx=5, pady=5)
        self.gametype_var = ttk.StringVar()
        self.gametype_dropdown = ttk.Combobox(input_frame, textvariable=self.gametype_var, values=["dm", "war", "conf", "dom", "sd", "sab"])
        self.gametype_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Map Category:").grid(row=0, column=2, padx=5, pady=5)
        self.map_category_var = ttk.StringVar()
        self.map_category_dropdown = ttk.Combobox(input_frame, textvariable=self.map_category_var, values=list(self.maps.keys()))
        self.map_category_dropdown.grid(row=0, column=3, padx=5, pady=5)
        self.map_category_dropdown.bind("<<ComboboxSelected>>", self.update_map_dropdown)

        ttk.Label(input_frame, text="Map:").grid(row=0, column=4, padx=5, pady=5)
        self.map_var = ttk.StringVar()
        self.map_dropdown = ttk.Combobox(input_frame, textvariable=self.map_var)
        self.map_dropdown.grid(row=0, column=5, padx=5, pady=5)

        # Rotation management
        button_frame = ttk.Frame(rotation_frame)
        button_frame.pack(fill=X, padx=10, pady=10)

        add_button = ttk.Button(button_frame, text="Add to Rotation", command=self.add_to_rotation)
        add_button.pack(side=LEFT, padx=5)

        remove_button = ttk.Button(button_frame, text="Remove from Rotation", command=self.remove_from_rotation)
        remove_button.pack(side=LEFT, padx=5)

        move_up_button = ttk.Button(button_frame, text="Move Up", command=self.move_up_in_rotation)
        move_up_button.pack(side=LEFT, padx=5)

        move_down_button = ttk.Button(button_frame, text="Move Down", command=self.move_down_in_rotation)
        move_down_button.pack(side=LEFT, padx=5)

        
        randomize_button = ttk.Button(button_frame, text="Randomize Maps", command=self.randomize_maps)
        randomize_button.pack(side=LEFT, padx=5)

    def update_map_dropdown(self, event):
        category = self.map_category_var.get()
        self.map_dropdown['values'] = [name for name, _ in self.maps.get(category, [])]

    def add_to_rotation(self):
        gametype = self.gametype_var.get()
        map_category = self.map_category_var.get()
        map_name = self.map_var.get()
        if gametype and map_category and map_name:
            map_code = next((code for name, code in self.maps[map_category] if name == map_name), "")
            self.rotation_listbox.insert("", END, values=(gametype, map_name))
            self.map_rotation.append((gametype, map_code))
            # Clear map selection
            self.map_category_var.set('')
            self.map_var.set('')
            self.update_map_count()
        else:
            messagebox.showwarning("Invalid Input", "Please select a gametype, map category, and map.")

    def remove_from_rotation(self):
        selected_item = self.rotation_listbox.selection()
        if selected_item:
            index = self.rotation_listbox.index(selected_item)
            self.rotation_listbox.delete(selected_item)
            del self.map_rotation[index]
            self.update_map_count()
        else:
            messagebox.showwarning("No Selection", "Please select an item to remove from the rotation.")

    def move_up_in_rotation(self):
        selected_item = self.rotation_listbox.selection()
        if selected_item:
            index = self.rotation_listbox.index(selected_item)
            if index > 0:
                self.map_rotation[index], self.map_rotation[index-1] = self.map_rotation[index-1], self.map_rotation[index]
                self.refresh_rotation_list()
                self.rotation_listbox.selection_set(index-1)
        else:
            messagebox.showwarning("No Selection", "Please select an item to move up in the rotation.")

    def move_down_in_rotation(self):
        selected_item = self.rotation_listbox.selection()
        if selected_item:
            index = self.rotation_listbox.index(selected_item)
            if index < len(self.map_rotation) - 1:
                self.map_rotation[index], self.map_rotation[index+1] = self.map_rotation[index+1], self.map_rotation[index]
                self.refresh_rotation_list()
                self.rotation_listbox.selection_set(index+1)
        else:
            messagebox.showwarning("No Selection", "Please select an item to move down in the rotation.")

    def refresh_rotation_list(self):
        self.rotation_listbox.delete(*self.rotation_listbox.get_children())
        for gametype, map_code in self.map_rotation:
            map_name = next((name for category in self.maps.values() for name, code in category if code == map_code), map_code)
            self.rotation_listbox.insert("", END, values=(gametype, map_name))

    def update_map_count(self):
        count = len(self.map_rotation)
        self.map_count_label.config(text=f"Maps in rotation: {count}")

    def randomize_maps(self):
        gametype = self.gametype_var.get()
        if not gametype:
            messagebox.showwarning("Invalid Input", "Please select a gametype first.")
            return

        # Prompt user for number of maps
        num_maps = simpledialog.askinteger("Randomize Maps", "How many maps do you want to add?", 
                                           minvalue=1, maxvalue=54)
        if num_maps is None:  # 
            return

        # Get all available maps
        all_maps = [(name, code) for category in self.maps.values() for name, code in category]
        
        # Randomly select the specified number of maps
        selected_maps = random.sample(all_maps, min(num_maps, len(all_maps)))

        # Clear current rotation
        self.map_rotation.clear()
        self.rotation_listbox.delete(*self.rotation_listbox.get_children())

        # Add selected maps to rotation
        for map_name, map_code in selected_maps:
            self.rotation_listbox.insert("", END, values=(gametype, map_name))
            self.map_rotation.append((gametype, map_code))

        self.update_map_count()
        messagebox.showinfo("Success", f"Added {len(selected_maps)} random maps to the rotation.")

    def add_dvar(self):
        name = self.dvar_name_entry.get().strip()
        value = self.dvar_value_entry.get().strip()
        if name and value:
            self.dvar_listbox.insert("", END, values=(name, value))
            self.custom_dvars[name] = value
            self.dvar_name_entry.delete(0, END)
            self.dvar_value_entry.delete(0, END)
        else:
            messagebox.showwarning("Invalid Input", "Please enter both a name and a value for the DVar.")

    def edit_dvar(self):
        selected_item = self.dvar_listbox.selection()
        if selected_item:
            name, value = self.dvar_listbox.item(selected_item)['values']
            self.dvar_name_entry.delete(0, END)
            self.dvar_name_entry.insert(0, name)
            self.dvar_value_entry.delete(0, END)
            self.dvar_value_entry.insert(0, value)
            self.dvar_listbox.delete(selected_item)
            del self.custom_dvars[name]
        else:
            messagebox.showwarning("No Selection", "Please select a DVar to edit.")

    def remove_dvar(self):
        selected_item = self.dvar_listbox.selection()
        if selected_item:
            name, _ = self.dvar_listbox.item(selected_item)['values']
            self.dvar_listbox.delete(selected_item)
            del self.custom_dvars[name]
        else:
            messagebox.showwarning("No Selection", "Please select a DVar to remove.")

    def generate_default_config(self):
        default_config = """
/////////////////////////////////////////////////////////////////////////
//  Call of duty: Modern Warfare Remastered MP Dedicated Server Config //
//                              H1-MOD                                 //
/////////////////////////////////////////////////////////////////////////

set sv_hostname "CHANGE ME - COLORS --->"
set g_password ""
set sv_maxclients "18"
set sv_timeout "20"
set sv_reconnectlimit "3"
set g_inactivity "420"
set sv_kickBanTime "3600"
seta g_allowVote "1"
seta g_deadChat "0"

seta sv_privateClients 0
seta sv_privatePassword ""

set logfile "2"
set g_logSync "1"
set g_log "logs\\games_mp.log"
set rcon_password "CHANGEME"
set sv_sayName "^7Server^7"

set scr_dm_scorelimit "1500"
set scr_dm_timelimit "10"
set scr_dm_playerrespawndelay "0"
set scr_dm_numlives "0"
set scr_dm_roundlimit "1"
set scr_dm_winlimit "1"

set scr_war_scorelimit "7500"
set scr_war_timelimit "10"
set scr_war_playerrespawndelay "0"
set scr_war_waverespawndelay "0"
set scr_war_numlives "0"
set scr_war_roundlimit "1"
set scr_war_winlimit "1"

set scr_conf_scorelimit "7500"
set scr_conf_timelimit "10"
set scr_conf_playerrespawndelay "0"
set scr_conf_waverespawndelay "0"
set scr_conf_numlives "0"
set scr_conf_roundlimit "1"
set scr_conf_winlimit "1"

set scr_dom_scorelimit "200"
set scr_dom_timelimit "0"
set scr_dom_playerrespawndelay "0"
set scr_dom_waverespawndelay "0"
set scr_dom_numlives "0"
set scr_dom_roundlimit "1"
set scr_dom_winlimit "1"

set scr_sd_scorelimit "1"
set scr_sd_timelimit "2.5"
set scr_sd_playerrespawndelay "0"
set scr_sd_waverespawndelay "0"
set scr_sd_numlives "1"
set scr_sd_roundlimit "0"
set scr_sd_winlimit "4"
set scr_sd_roundswitch "3"
set scr_sd_bombtimer "45"
set scr_sd_defusetime "5"
set scr_sd_multibomb "0"
set scr_sd_planttime "5"

set scr_sab_scorelimit "0"
set scr_sab_timelimit "20"
set scr_sab_bombtimer "30"
set scr_sab_defusetime "5"
set scr_sab_hotpotato "0"
set scr_sab_numlives "0"
set scr_sab_planttime "2.5"
set scr_sab_playerrespawndelay "7.5"
set scr_sab_roundlimit "1"
set scr_sab_roundswitch "1"
set scr_sab_waverespawndelay "0"

set g_gametype "dom"
set sv_maprotation "gametype dom map mp_farm map mp_bog map mp_crash map mp_vacant"

// CUSTOM DVARS H2M CFG EDITOR //
"""
        return default_config

    def save_config(self):
        # Start with the default configuration
        config_lines = self.generate_default_config().split('\n')

        # Update the configuration with the current settings
        for i, line in enumerate(config_lines):
            if line.strip().startswith('set '):
                parts = line.split(None, 2)
                if len(parts) >= 2:
                    key = parts[1]
                    if key in self.config:
                        value = self.config[key]
                        if isinstance(value, ttk.Entry):
                            value = value.get()
                        config_lines[i] = f'set {key} "{value}"'

        # Update map rotation
        rotation_string = self.generate_map_rotation_string()
        for i, line in enumerate(config_lines):
            if line.strip().startswith('set sv_maprotation'):
                config_lines[i] = f'set sv_maprotation "{rotation_string}"'
                break

        # Add custom DVars
        custom_dvar_section = ["// CUSTOM DVARS H2M CFG EDITOR //"]
        for key, value in self.custom_dvars.items():
            custom_dvar_section.append(f'set {key} "{value}"')

        # Find the custom DVars section and replace it
        custom_start = -1
        for i, line in enumerate(config_lines):
            if line.strip() == "// CUSTOM DVARS H2M CFG EDITOR //":
                custom_start = i
                break

        if custom_start != -1:
            config_lines = config_lines[:custom_start] + custom_dvar_section
        else:
            config_lines.extend(custom_dvar_section)

        # Write the new configuration to file
        with open("server.cfg", "w") as f:
            f.write('\n'.join(config_lines))

        messagebox.showinfo("Success", "Configuration saved successfully!")

    def generate_map_rotation_string(self):
        rotation_parts = []
        current_gametype = None
        for gametype, map_code in self.map_rotation:
            if gametype != current_gametype:
                rotation_parts.extend(["gametype", gametype])
                current_gametype = gametype
            rotation_parts.extend(["map", map_code])
        return " ".join(rotation_parts)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = ConfigEditor(root)
    root.mainloop()