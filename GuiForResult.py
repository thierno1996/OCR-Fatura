from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class CustomProductLayout(GridLayout):
    def __init__(self, product_name, quantity, product_price, **kwargs):
        super(CustomProductLayout, self).__init__(cols=3, row_force_default=True, row_default_height=dp(50),
                                                  **kwargs)

        self.add_widget(TextInput(text=product_name))
        self.add_widget(TextInput(text=str(quantity)))
        self.add_widget(TextInput(text=str(product_price)))


class ScrollableProductList(ScrollView):
    def __init__(self, **kwargs):
        super(ScrollableProductList, self).__init__(**kwargs)

        self.product_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.product_layout.bind(minimum_height=self.product_layout.setter('height'))
        self.add_widget(self.product_layout)

    def add_product(self, product_name, quantity, product_price):
        custom_layout = CustomProductLayout(product_name, quantity, product_price)
        self.product_layout.add_widget(custom_layout)