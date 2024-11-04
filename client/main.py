import json
import pathlib
import psutil
import requests
from kivy.properties import StringProperty, Clock
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.settings import SettingsWithNoMenu
from kivy.core.window import Window
from kivymd.uix.button import MDIconButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.tooltip import MDTooltip
from requests.auth import HTTPBasicAuth

Window.size = (1400, 900)


class TooltipMDIconButton(MDIconButton, MDTooltip):
    pass


class Tab(MDFloatLayout, MDTabsBase):
    pass


class RootWidget(FloatLayout):
    pass


class ChampionImage(Image):
    def __init__(self, **kwargs):
        super(ChampionImage, self).__init__(**kwargs)
        self.source = 'icons/0.png'
        self.size = self.texture_size


class StatGrid(GridLayout):
    def __init__(self, **kwargs):
        super(StatGrid, self).__init__(**kwargs)
        # self.minimum_height = self.height
        self.bind(minimum_height=self.setter("height"))
        self.size_hint_y = None
        self.row_default_height = 100
        # self.pos_hint = {'x': 0.5}
        # self.width = 0.9
        self.size_hint_x = 0.9


def hide_widget(wid, show=False):
    if show:
        wid.opacity, wid.disabled = 1, False
    else:
        wid.opacity, wid.disabled = 0, True


def bring_to_front():
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
        return f"https://127.0.0.1:{self.lol_client_port}/"

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
        self.root.ids.settings_content.add_widget(self.create_settings())
        self.load_statistics(self.root.ids.all_tab)
        Clock.schedule_interval(self.update_champion_select, 3)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Gray"
        self.settings_cls = SettingsWithNoMenu
        self.use_kivy_settings = False
        return RootWidget()

    def build_config(self, config):
        config.setdefaults(
            'Appsettings', {'server_url': 'localhost', 'port': 8000}
        )

    def build_settings(self, settings):
        settings.add_json_panel('AppSettings', self.config, filename='settings_custom.json')

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        instance_tab.clear_widgets()
        self.load_statistics(instance_tab)

    def load_statistics(self, tab):
        f = open('lobby/statistics.json', encoding="utf8")
        data = json.load(f)
        grid = StatGrid(cols=5)
        for label in ["", "Name", "Winratio", "Pickratio", "Banratio"]:
            grid.add_widget(Label(text=label))

        for c in data:
            winratio = c["Won"] / (c["Won"] + c["Lost"]) * 100
            pickratio = (c["Won"] + c["Lost"]) / c["Total"] * 100
            banratio = c["Banned"] / c["Total"] * 100
            grid.add_widget(Image(source=f"icons/{c['key']}.png"))
            grid.add_widget(Label(text=f"{c['name']}"))
            grid.add_widget(Label(text=f"{winratio:.2f}"))
            grid.add_widget(Label(text=f"{pickratio:.2f}"))
            grid.add_widget(Label(text=f"{banratio:.2f}"))

        tab.add_widget(MDScrollView(grid))

    def update_champion_select(self, *args):
        self.league_process_setup()
        # print(test.ids.champion_select_layout)
        if self.lockfile_data:
            ch_select_url = "lol-champ-select/v1/session"
            basic = HTTPBasicAuth('riot', self.lol_client_password)
            response = requests.get(self.lol_client_url + ch_select_url, auth=basic, verify='riotgames.pem')
            data = response.json()

            if response.status_code != 200:
                hide_widget(self.root.ids.champion_select_layout)
                hide_widget(self.root.ids.champion_select_label, show=True)
                return

            hide_widget(self.root.ids.champion_select_layout, show=True)
            hide_widget(self.root.ids.champion_select_label)
            # f = open('lobby/ranked_picked.json')
            # data = json.load(f)

            # try:
            allies = [(player["cellId"], player["championId"]) for player in data.get("myTeam")]
            enemies = [(player["cellId"], player["championId"]) for player in data.get("theirTeam")]
            bans = []
            for actions in data.get("actions"):
                for action in actions:
                    if action["type"] == "ban":
                        bans.append(action["championId"])

            # except TypeError:
            #     return

            for index, ally in enumerate(allies):
                attr = f'ally_{index}'
                item = getattr(self.root.ids, attr)
                item.source = f'icons/{ally[1]}.png'

            for index, enemy in enumerate(enemies):
                attr = f'enemy_{index}'
                item = getattr(self.root.ids, attr)
                item.source = f'icons/{enemy[1]}.png'

            self.root.ids.bans.clear_widgets()
            for ban in bans:
                self.root.ids.bans.add_widget(Image(source=f'icons/{ban}.png'))

            self.root.ids.suggestions.clear_widgets()
            f = open('lobby/proposition.json')
            data = json.load(f)
            grid = GridLayout(cols=3, row_default_height=70, row_force_default=True)
            grid.add_widget(Label(text=""))
            grid.add_widget(Label(text="Name"))
            grid.add_widget(Label(text="Winnig chance"))
            for c in data:
                grid.add_widget(Image(source=f"icons/{c['key']}.png"))
                grid.add_widget(Label(text=f"{c['name']}"))
                grid.add_widget(Label(text=f"{c['win']:.2f}%"))

            self.root.ids.suggestions.add_widget(grid)


if __name__ == '__main__':
    MainApp().run()
