from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen

KV = """

ScreenManager:
    HomeScreen:
    ApplyScreen:
    ContactScreen:

<HomeScreen>:
    name: "home"

    FloatLayout:

        Image:
            source: "hpcl_bg.jpg"
            allow_stretch: True
            keep_ratio: False

        BoxLayout:
            orientation: "vertical"
            size_hint: .9,.6
            pos_hint: {"center_x":.5,"center_y":.5}
            spacing: 20

            Label:
                text: "Hindustan Petroleum"
                font_size: 32
                bold: True
                color: 1,1,1,1

            Label:
                text: "HPCL Choices Application Portal"
                font_size: 20
                color: 1,1,1,1

            Button:
                text: "Apply Now"
                size_hint_y: None
                height: 60
                on_press: app.root.current = "apply"

            Button:
                text: "Contact Us"
                size_hint_y: None
                height: 60
                on_press: app.root.current = "contact"


<ApplyScreen>:
    name: "apply"

    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15

        Label:
            text: "Application Form"
            font_size: 24

        TextInput:
            hint_text: "Full Name"

        TextInput:
            hint_text: "Phone Number"

        TextInput:
            hint_text: "Email"

        TextInput:
            hint_text: "Address"

        Button:
            text: "Submit Application"

        Button:
            text: "Back"
            on_press: app.root.current = "home"


<ContactScreen>:
    name: "contact"

    BoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 15

        Label:
            text: "Contact Us"
            font_size: 24

        TextInput:
            hint_text: "Your Name"

        TextInput:
            hint_text: "Your Email"

        TextInput:
            hint_text: "Message"
            multiline: True

        Button:
            text: "Send Message"

        Button:
            text: "Back"
            on_press: app.root.current = "home"

"""


class HomeScreen(Screen):
    pass


class ApplyScreen(Screen):
    pass


class ContactScreen(Screen):
    pass


class HPCLApp(App):
    def build(self):
        return Builder.load_string(KV)


HPCLApp().run()
