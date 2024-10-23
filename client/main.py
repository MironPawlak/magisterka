import pathlib

import psutil
from kivy.properties import StringProperty, Clock

from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.settings import SettingsWithNoMenu
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import ImageLeftWidget, OneLineAvatarListItem, MDList
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.tooltip import MDTooltip

# from kivymd.uix.segmentedbutton import MDSegmentButtonLabel
# )

Window.size = (1400, 900)


class TooltipMDIconButton(MDIconButton, MDTooltip):
    pass


# class MDSegmentButtonLabel(MDSegmentedControl):
#     pass


class Tab(MDFloatLayout, MDTabsBase):
    pass


class RootWidget(FloatLayout):
    pass


def bring_to_front(self):
    Window.always_on_top = True
    Window.always_on_top = False


class MainApp(MDApp):
    icon = StringProperty('')

    def __init__(self, **kwargs):
        super().__init__()
        self.lockfile_data = None

    @property
    def lol_client_password(self):
        return self.lockfile_data[3]

    @property
    def lol_client_port(self):
        return self.lockfile_data[2]

    @property
    def lol_client_url(self):
        return f"https://127.0.0.1:{self.lol_client_port}"

    def league_process_setup(self):
        process = next((x for x in psutil.process_iter() if 'LeagueClient' in x.name()), None)
        if process is None:
            self.lockfile_data = None
            self.icon = "alpha-x-circle"
            return
        path = pathlib.Path(psutil.Process(process.pid).cmdline()[0]).parent
        lockfile = path.joinpath('lockfile')
        try:
            with open(lockfile, 'r') as file:
                self.lockfile_data = file.readlines()[0].split(':')
                self.icon = "check"
        except FileNotFoundError:
            self.lockfile_data = None
            self.icon = "alpha-x-circle"

    def on_start(self):
        self.league_process_setup()
        s = self.create_settings()
        self.root.ids.settings_content.add_widget(s)
        Clock.schedule_once(bring_to_front, 5)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Gray"
        self.settings_cls = SettingsWithNoMenu
        self.use_kivy_settings = False
        return RootWidget()

    def build_config(self, config):
        config.setdefaults(
            'Appsettings', {'text': 'Hello Python', 'font_size': 20}
        )

    def build_settings(self, settings):
        settings.add_json_panel('AppSettings', self.config, filename='settings_custom.json')

    # def refresh_list(self, segmented_control, segmented_item):
    #     print(segmented_item.text)

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        instance_tab.clear_widgets()
        md_list = MDList(
                id="container"
            )
        for i in range(5):
            o = OneLineAvatarListItem(
                ImageLeftWidget(
                    source="1.png"
                ),
                text=f"Champion {i}",
            )
            md_list.add_widget(o)

        instance_tab.add_widget(MDScrollView(md_list))
        # for child in instance_tab.children:
        #     print(child)
        # print()


if __name__ == '__main__':
    MainApp().run()
