import customtkinter as ctk
import pandas as pd
from settings import *
from data_retriever import convert_data_entry_to_dict
from PIL import Image


class EntriesFrame(ctk.CTkFrame):
    def __init__(self, parent, data, update_layout_display, update_info_panel):
        super().__init__(master=parent, fg_color=WINDOW_BG_COLOR)
        self.grid(row=0, rowspan=2, column=0, sticky='nsew')

        # Layout
        self.rowconfigure(0, weight=5, uniform='a')
        self.columnconfigure(0, weight=1, uniform='a')

        # Widgets
        self.list_entry_frame = ListEntryPanel(self, data, update_layout_display, update_info_panel)


class ListEntryPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, data, update_layout_display, update_info_panel):
        super().__init__(
            master=parent,
            fg_color='transparent',
            scrollbar_button_color=ENTRY_TEXT_COLOR,
            scrollbar_button_hover_color=SCROLLBAR_HOVER_COLOR)
        self.grid(row=0, column=0, sticky='nsew')

        self.data = data
        self.layouts_list = []

        # Widgets
        self.create_entries_list(update_layout_display, update_info_panel)

    def create_entries_list(self, update_layout_display, update_info_panel):
        for index in range(self.data.shape[0]):  # shape[0] returns the number of rows in the DataFrame.
            ctk.CTkFrame(self, fg_color=ENTRY_TEXT_COLOR, height=2).pack(fill='x')
            ListEntry(self, self.data.iloc[index], update_layout_display, update_info_panel)
        ctk.CTkFrame(self, fg_color=ENTRY_TEXT_COLOR, height=2).pack(fill='x')


class ListEntry(ctk.CTkFrame):
    def __init__(self, parent, data_series, update_layout_display, update_info_panel):
        super().__init__(master=parent, fg_color='transparent', corner_radius=0)
        self.pack(fill='both')

        self.update_layout_display = update_layout_display
        self.update_info_panel = update_info_panel

        # Split the data from the Series into variables that represent the data of a layout. Since some layouts do not
        # have all the data available, check for the occurrences of empty data to store the proper representation.
        self.layout_title = data_series['Name']
        self.image_path = data_series['Image']
        self.cost = convert_data_entry_to_dict(data_series['Cost']) if not pd.isna(data_series['Cost']) else 'N/A'
        self.size = data_series['Size'] if not pd.isna(data_series['Size']) else 'N/A'
        self.tiles = data_series['Tiles'] if not pd.isna(data_series['Tiles']) else 'N/A'
        self.space_eff = data_series['Space Efficiency'] if not pd.isna(data_series['Space Efficiency']) else 'N/A'
        self.production = convert_data_entry_to_dict(
            data_series['Production']) if not pd.isna(data_series['Production']) else 'N/A'

        # Layout
        self.rowconfigure((0, 1), weight=1, uniform='a')
        self.columnconfigure((0, 2), weight=2, uniform='a')
        self.columnconfigure(1, weight=3, uniform='a')
        self.columnconfigure(3, weight=2, uniform='a')

        # Widgets
        self.production_line = ctk.CTkLabel(
            master=self,
            text=self.layout_title,
            text_color=ENTRY_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=TITLE_FONT_SIZE, weight='bold'))
        self.production_line.grid(row=0, column=0, columnspan=4, sticky='nsew')

        self.production_data_label = ctk.CTkLabel(
            master=self, text='Produces:',
            text_color=ENTRY_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=INFO_FONT_SIZE))
        self.production_data_label.grid(row=1, column=0, sticky='nsew')

        # Since the production varies in the different layouts, creating a frame to customize the layout of this
        # varying data is best.
        self.production_data_frame = ProductionDataFrame(self, self.production)

        self.space_eff_label = ctk.CTkLabel(
            master=self,
            text='Space Eff:',
            text_color=ENTRY_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=INFO_FONT_SIZE))
        self.space_eff_label.grid(row=1, column=2, sticky='nsew')

        self.space_eff_data_label = ctk.CTkLabel(
            master=self,
            text=self.space_eff,
            text_color=ENTRY_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=INFO_FONT_SIZE))
        self.space_eff_data_label.grid(row=1, column=3, sticky='nsew')

        self.bind_all_widgets(self.production_data_frame)

    def bind_all_widgets(self, production_data_frame):
        # Bind the mouse button event to all widgets in the entry list frame.
        self.bind('<Button>', self.selected)
        for child in self.winfo_children():
            child.bind('<Button>', self.selected)
        for child in production_data_frame.winfo_children():
            child.bind('<Button>', self.selected)

    def selected(self, event):
        self.update_layout_display(self.image_path)
        self.update_info_panel(self.cost, self.size, self.tiles, self.space_eff, self.production)


class ProductionDataFrame(ctk.CTkFrame):
    def __init__(self, parent, production_data):
        super().__init__(master=parent, fg_color=WINDOW_BG_COLOR)
        self.grid(row=1, column=1, sticky='nsew', padx=5)

        # Check for empty production data.
        if production_data != 'N/A':
            self.rowconfigure(0, weight=1)

            # Set up the grid layout depending on how many goods the Anno 1800 layout produces.
            if len(production_data.keys()) > 1:
                self.columnconfigure((0, 3), weight=2, uniform='a')
                self.columnconfigure(2, weight=1, uniform='a')
                self.columnconfigure((1, 4), weight=3, uniform='a')
            else:
                self.columnconfigure(0, weight=1, uniform='a')
                self.columnconfigure(1, weight=3, uniform='a')

            # Place the widgets in the correct column based on how many goods the layout produces. Using a variable to
            # keep track of the column index and the index of the enumeration of the keys will return the correct column
            # index.
            column_index = 0
            for index, key in enumerate(production_data.keys()):
                image = Image.open(PRODUCE_GOODS_IMAGE_PATH_DICT[key])
                image_tk = ctk.CTkImage(light_image=image, dark_image=image)
                ctk.CTkLabel(
                    self,
                    text='',
                    image=image_tk).grid(row=0, column=column_index + index, sticky='nse')

                column_index += 1

                ctk.CTkLabel(
                    master=self,
                    text=production_data[key],
                    text_color=ENTRY_TEXT_COLOR,
                    font=ctk.CTkFont(family=FONT_FAMILY, size=INFO_FONT_SIZE)).grid(row=0, column=column_index + index,
                                                                                    sticky='nsw', padx=1)

                # Add middle dot separator unless it's the last value.
                if index != len(production_data.values()) - 1:
                    column_index += 1
                    ctk.CTkLabel(
                        master=self,
                        text='\u00B7',  # Unicode for middle dot character.
                        text_color=ENTRY_TEXT_COLOR,
                        font=ctk.CTkFont(family=FONT_FAMILY, size=INFO_FONT_SIZE)).grid(row=0,
                                                                                        column=column_index + index,
                                                                                        sticky='nsew')
        else:
            ctk.CTkLabel(
                master=self,
                text='N\\A',
                text_color=ENTRY_TEXT_COLOR,
                font=ctk.CTkFont(family=FONT_FAMILY, size=INFO_FONT_SIZE)).pack()
