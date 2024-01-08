from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class CustomProductLayout(GridLayout):
    def __init__(self, product_name, quantity, product_price, **kwargs):
        super(CustomProductLayout, self).__init__(cols=3, **kwargs)
        # , row_force_default=True, row_default_height=dp(50

        self.add_widget(TextInput(text=product_name))
        self.add_widget(TextInput(text=str(quantity)))
        self.add_widget(TextInput(text=str(product_price)))


class ScrollableProductList(ScrollView):
    def __init__(self, **kwargs):
        super(ScrollableProductList, self).__init__(**kwargs)

        self.add_button = Button(text="Add to your Local Database", size_hint_y=None)
        self.add_button.height = "30dp"
        self.empty_label = Label(text="")

        self.product_layout = BoxLayout(orientation='vertical', spacing=5, padding="20dp", size_hint_y=None)  # , size_hint_y=None
        self.product_layout.height = "500dp"
        self.add_widget(self.product_layout)
        self.product_layout.add_widget(self.empty_label)
        self.product_layout.add_widget(self.add_button)

    def add_product(self, product_name, quantity, product_price):
        custom_layout = CustomProductLayout(product_name, quantity, product_price, size_hint_y=None)
        custom_layout.height = "30dp"
        self.product_layout.add_widget(custom_layout, 2)

