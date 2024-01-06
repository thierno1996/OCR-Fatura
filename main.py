import time
from kivy.core.window import Window
from PIL import Image as PILImage
import numpy as np
from kivy.uix.image import Image
from kivy.graphics import Color, Line
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.floatlayout import MDFloatLayout

from ClientSide import ImageUploader
from GuiForResult import ScrollableProductList

Window.size = (500, 600)


class ImageWithLines(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.copied_image = None
        self.line = None
        self.source = "bill.jpg"  # r"C:\Users\casper\Desktop\second.png"
        # self.size_hint = (None, None)
        # self.width = self.texture_size[0]
        # self.height = self.texture_size[1]

    def on_touch_down(self, touch):
        self.left_and_right_empty_space = (self.width - self.norm_image_size[0]) / 2
        self.above_and_below_empty_space = (self.height - self.norm_image_size[1]) / 2

        if not self.collide_point(*touch.pos) or not self.collide_point(*touch.opos):
            return

        if self.line is not None:
            self.canvas.remove(self.line)
            self.line = None

        pixel_x = touch.x - self.left_and_right_empty_space - self.x
        pixel_y = touch.y - self.above_and_below_empty_space - self.y

        if not (0 <= pixel_x <= self.norm_image_size[0] and 0 <= pixel_y <= self.norm_image_size[1]):
            print('Clicked value is out of bounds')
            return True

        print('Clicked inside image, coordinates:', pixel_x, pixel_y)
        self.draw_line(touch.x, touch.y)

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos) or not self.collide_point(*touch.opos):
            return

        if self.line is not None:
            self.calculate_points(touch)
            self.line.points = [self.bl_x, self.bl_y, self.br_x, self.br_y,
                                self.ur_x, self.ur_y, self.ul_x, self.ul_y,
                                self.bl_x, self.bl_y]

    def calculate_points(self, touch):
        self.ur_x, self.ur_y = touch.x, touch.y
        self.br_x, self.br_y = self.ur_x, self.bl_y
        self.ul_x, self.ul_y = self.bl_x, self.ur_y

    def draw_line(self, x, y):
        with self.canvas:
            Color(0, 0, 1)
            self.bl_x, self.bl_y = x, y
            self.br_x, self.br_y = 0, 0
            self.ur_x, self.ur_y = 0, 0
            self.ul_x, self.ul_y = 0, 0
            self.line = Line(points=([self.bl_x, self.bl_y]), width=2)

    def extract_region(self, filename):
        scale_x = self.texture_size[0] / self.norm_image_size[0]
        scale_y = self.texture_size[1] / self.norm_image_size[1]
        if self.line is not None:
            original_texture = self.texture
            width, height = self.calculate_rectangle_size()
            x, y = self.get_rectangle_position()

            box_tuple = (x, y + self.y + 10, width * scale_x - self.left_and_right_empty_space,
                         height * scale_y - self.above_and_below_empty_space)

            # box_tuple = (x, y-self.y, width, height) these are the right coordinates in case the image widget
            # has the same size as the texture
            # the rectangle is evenly aligned but the texture is not, therefore some items will always be distorted

            # I subtract the y pos from the self.y to get the actual pos, why I don't really know ?

            copied_texture = original_texture.get_region(*box_tuple)
            self.copied_image = Image(texture=copied_texture)

            image_data = np.frombuffer(copied_texture.pixels, dtype=np.uint8)
            image_data = image_data.reshape(copied_texture.size[1], copied_texture.size[0], 4)
            pil_image = PILImage.fromarray(image_data)
            pil_image.save(f"{filename}.png")
            self.canvas.remove(self.line)
            self.line = None

    def get_rectangle_position(self):
        rectangle_coordinates = [(self.bl_x, self.bl_y), (self.br_x, self.br_y),
                                 (self.ur_x, self.ur_y), (self.ul_x, self.ul_y),
                                 (self.bl_x, self.bl_y)]
        pos_x = min(coord[0] for coord in rectangle_coordinates)
        pos_y = min(coord[1] for coord in rectangle_coordinates)
        return round(pos_x), round(pos_y)

    def calculate_rectangle_size(self):
        rectangle_coordinates = [(self.bl_x, self.bl_y), (self.br_x, self.br_y),
                                 (self.ur_x, self.ur_y), (self.ul_x, self.ul_y),
                                 (self.bl_x, self.bl_y)]
        x_values = [coord[0] for coord in rectangle_coordinates]
        y_values = [coord[1] for coord in rectangle_coordinates]

        width = max(x_values) - min(x_values)
        height = max(y_values) - min(y_values)

        return round(width), round(height)


class ImageDisplayerApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scrollable_product_list = None
        self.previous_img = None
        self.file_manager = None
        self.box_for_selection = None
        self.back_button = None
        self.box_for_buttons = None
        self.image_with_lines = None
        self.root_layout = None
        self.path_to_name = None

    def build(self):
        self.root_layout = MDBoxLayout(orientation='vertical', spacing="5dp")
        self.image_with_lines = ImageWithLines()
        self.box_for_buttons = MDBoxLayout(orientation="horizontal", spacing="100", size_hint_y=None)
        self.back_button = MDIconButton(icon="refresh")
        read_img_button = MDIconButton(icon="line-scan")
        read_img_button.bind(on_press=self.connect_to_server)
        close_button = MDIconButton(icon="close-circle", theme_icon_color="Custom", icon_color="red")
        close_button.bind(on_release=self.close_image_widget)
        self.box_for_selection = MDFloatLayout()
        cam = MDIconButton(icon="camera", size_hint=(None, None), pos_hint={'x': .6, 'y': .5})
        file = MDIconButton(icon="file", size_hint=(None, None), pos_hint={'x': .2, 'y': .5})
        self.box_for_selection.add_widget(cam)
        self.box_for_selection.add_widget(file)
        self.root_layout.add_widget(self.box_for_selection)
        button = MDIconButton(icon="crop")
        self.box_for_buttons.height = "50dp"
        button.bind(on_release=self.extract_and_display_region)
        self.back_button.bind(on_release=self.go_back)
        self.root_layout.add_widget(self.box_for_buttons)
        self.box_for_buttons.add_widget(close_button)
        self.box_for_buttons.add_widget(self.back_button)
        self.box_for_buttons.add_widget(button)
        self.box_for_buttons.add_widget(read_img_button)
        self.scrollable_product_list = ScrollableProductList()

        # Bind show_file_chooser to the "file" button
        file.bind(on_release=self.show_file_chooser)

        return self.root_layout

    def extract_and_display_region(self, *args):
        name = "img_" + str(int(time.time()))  # Creating a unique name
        if self.image_with_lines.copied_image:
            self.root_layout.remove_widget(self.image_with_lines.copied_image)

        self.image_with_lines.extract_region(name)
        self.image_with_lines.source = name + ".png"

        self.path_to_name = name + ".png"

    def show_file_chooser(self, instance):
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            ext=[".png", ".jpg", ".jpeg"],  # Specify allowed file extensions
        )
        self.file_manager.show('.')  # Start file manager in the current directory

    def select_path(self, path):
        self.previous_img = path
        print(f"Selected File: {path}")
        self.root_layout.remove_widget(self.box_for_selection)
        self.image_with_lines.source = path
        self.root_layout.add_widget(self.image_with_lines, 1)
        self.file_manager.close()

    def exit_manager(self, *args):
        print("File manager is closed or exited")
        self.file_manager.close()

    def go_back(self, *args):

        self.image_with_lines.source = self.previous_img

    def close_image_widget(self, *args):
        if self.image_with_lines in self.root_layout.children:
            self.root_layout.remove_widget(self.image_with_lines)
        if self.box_for_selection not in self.root_layout.children:
            self.root_layout.add_widget(self.box_for_selection, 1)

    def connect_to_server(self, *args):
        url = "http://127.0.0.1:5000/upload"
        image_path = self.path_to_name

        if image_path:
            loading_popup = Popup(title='Loading...', content=Label(text='  ....'),
                                  auto_dismiss=False,
                                  size_hint=(None, None), size=(200, 100))
            loading_popup.open()

            uploader = ImageUploader(url, image_path)
            response_json = uploader.upload_image()

            loading_popup.dismiss()

            if response_json:
                for product, values in response_json.items():
                    print(f"{product}: Quantity={values[0]}, Price={values[1]}")
                    print("------------------------------------------")


if __name__ == '__main__':
    ImageDisplayerApp().run()
