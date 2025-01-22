import os
import sys
import pathlib
from contextlib import suppress
from kivy.resources import resource_add_path
import psutil
import requests
from kivy.properties import StringProperty, Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivymd.toast import toast
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


class CustomDropDown(DropDown):
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


# class StatScroll()


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

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath('.')
        return os.path.join(base_path, relative_path)

    def __init__(self, **kwargs):
        super().__init__()
        self.lockfile_data = None
        self.champion_select_schedule = None
        self.champion_select_clock = 10
        self.last_state = None
        self.last_position = None

    @property
    def server_url(self):
        return f"http://{self.config.get('Appsettings', 'server_url')}:{self.config.get('Appsettings', 'port')}"

    @property
    def lol_client_password(self):
        return self.lockfile_data[3]

    @property
    def lol_client_port(self):
        return self.lockfile_data[2]

    @property
    def lol_client_url(self):
        return f"https://127.0.0.1:{self.lol_client_port}/"

    def league_process_setup(self, *args):
        if self.lockfile_data is None:
            process = next((x for x in psutil.process_iter() if 'LeagueClient' in x.name()), None)
            if process is None:
                self.lockfile_data = None
                self.icon = "alpha-x-circle"
                with suppress(AttributeError):
                    self.champion_select_schedule.cancel()
                    self.champion_select_clock = 10
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
                return
            self.champion_select_schedule = Clock.schedule_interval(self.update_champion_select,
                                                                    self.champion_select_clock)

    def on_start(self):
        self.league_process_setup()
        self.root.ids.settings_content.add_widget(self.create_settings())
        self.load_statistics(self.root.ids.top_tab)
        Clock.schedule_interval(self.league_process_setup, 4)

    def return_player_numbers(self):
        player_number = self.root.ids.drop_btn.text
        print(player_number)
        return player_number

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Gray"
        self.settings_cls = SettingsWithNoMenu
        self.use_kivy_settings = False
        # Clock.schedule_once(self.build_dropdown, 0.5)
        return RootWidget()

    def build_config(self, config):
        config.setdefaults(
            'Appsettings', {'server_url': 'pyron.asuscomm.com', 'port': 7000}
        )

    def build_settings(self, settings):
        settings.add_json_panel('AppSettings', self.config, filename=self.resource_path('settings_custom.json'))

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        instance_tab.clear_widgets()
        self.load_statistics(instance_tab)

    def load_statistics(self, tab):
        pos_map = {
            "Top": "TOP",
            "Jungle": "JGL",
            "Mid": "MID",
            "Adc": "BOT",
            "Support": "SUP"
        }
        url = f"{self.server_url}/get_statistics/{pos_map[tab.title]}/"
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            toast("No connection with server")
            return
        data = response.json()
        grid = StatGrid(cols=5)
        for label in ["", "Name", "Winratio", "Pickratio", "Banratio"]:
            grid.add_widget(Label(text=label))

        for champion in data:
            # TODO FIX THIS TOTAL
            total = 100000
            pickratio = (champion["wins"] + champion["losses"]) / total * 100
            banratio = champion["bans"] / total * 100
            grid.add_widget(Image(source=self.resource_path(f"icons/{champion['champion']['key']}.png")))
            grid.add_widget(Label(text=f"{champion['champion']['name']}"))
            grid.add_widget(Label(text=f"{champion['ratio'] * 100:.2f}%"))
            grid.add_widget(Label(text=f"{pickratio:.2f}%"))
            grid.add_widget(Label(text=f"{banratio:.2f}%"))
        tab.add_widget(MDScrollView(grid))

    def load_counters(self):
        champion = self.root.ids.counter_input.text
        if champion == '':
            toast("Empty champion field")
            return
        url = f"{self.server_url}/get_counters/{champion}/"
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            toast("No connection with server")
            return
        if response.status_code != 200:
            toast("Invalid champion name")
            return
        data = response.json()
        scroll_view = self.root.ids.counter_stats
        grid = StatGrid(cols=5)
        scroll_view.clear_widgets()
        for label in ["", "Name", "Winratio", "Wins", "Losses"]:
            grid.add_widget(Label(text=label))
        for champion in data:
            grid.add_widget(Image(source=self.resource_path(f"icons/{champion['champion']['key']}.png")))
            grid.add_widget(Label(text=f"{champion['champion']['name']}"))
            grid.add_widget(Label(text=f"{champion['ratio']:.2f}%"))
            grid.add_widget(Label(text=f"{champion['wins']}"))
            grid.add_widget(Label(text=f"{champion['losses']}"))
        scroll_view.add_widget(MDScrollView(grid))

    def update_champion_select(self, *args):

        if self.lockfile_data:
            ch_select_url = "lol-champ-select/v1/session"
            basic = HTTPBasicAuth('riot', self.lol_client_password)
            try:
                response = requests.get(self.lol_client_url + ch_select_url, auth=basic, verify=self.resource_path('riotgames.pem'))
            except requests.exceptions.ConnectionError:
                return

            if response.status_code != 200:
                hide_widget(self.root.ids.champion_select_layout)
                hide_widget(self.root.ids.champion_select_label, show=True)
                if self.champion_select_clock == 2:
                    self.champion_select_schedule.cancel()
                    self.champion_select_clock = 10
                    self.champion_select_schedule = Clock.schedule_interval(self.update_champion_select,
                                                                            self.champion_select_clock)
                return

            data = response.json()

            if self.champion_select_clock == 10:
                self.champion_select_schedule.cancel()
                self.champion_select_clock = 2
                self.champion_select_schedule = Clock.schedule_interval(self.update_champion_select,
                                                                        self.champion_select_clock)

            hide_widget(self.root.ids.champion_select_layout, show=True)
            hide_widget(self.root.ids.champion_select_label)

            allies = [(player["cellId"], player["championId"]) for player in data.get("myTeam")]
            enemies = [(player["cellId"], player["championId"]) for player in data.get("theirTeam")]
            bans = []
            for actions in data.get("actions"):
                for action in actions:
                    if action["type"] == "ban":
                        bans.append(action["championId"])

            current_state = set(allies + enemies + bans)
            current_position = self.root.ids.drop_btn.text
            if self.last_state is None:
                self.last_state = current_state
                self.last_position = current_position
            else:
                if set(allies + enemies + bans) == self.last_state and self.last_position == current_position:
                    return
                else:
                    self.last_state = current_state
                    self.last_position = current_position

            for index, ally in enumerate(allies):
                attr = f'ally_{index}'
                item = getattr(self.root.ids, attr)
                item.source = self.resource_path(f'icons/{ally[1]}.png')

            for index, enemy in enumerate(enemies):
                attr = f'enemy_{index}'
                item = getattr(self.root.ids, attr)
                item.source = self.resource_path(f'icons/{enemy[1]}.png')

            self.root.ids.bans.clear_widgets()
            for ban in bans:
                self.root.ids.bans.add_widget(Image(source=self.resource_path(f'icons/{ban}.png')))

            self.root.ids.suggestions.clear_widgets()
            pos_map = {
                "Top": "TOP",
                "Jungle": "JGL",
                "Middle": "MID",
                "Bottom": "BOT",
                "Support": "SUP"
            }
            if current_position == 'Select your role':
                return

            url = f"{self.server_url}/get_prediction/"
            post_data = {
                "position": pos_map[current_position],
                "allies": [x[1] for x in allies],
                "enemies": [x[1] for x in enemies],
                "bans": bans
            }
            response = requests.post(url=url, data=post_data)
            prediciton_data = response.json()
            grid = GridLayout(cols=3, row_default_height=70, row_force_default=True)
            grid.add_widget(Label(text=""))
            grid.add_widget(Label(text="Name"))
            grid.add_widget(Label(text="Winnig chance"))
            for prediction in prediciton_data['top_predictions']:
                grid.add_widget(Image(source=self.resource_path(f"icons/{prediction['champion']['key']}.png")))
                grid.add_widget(Label(text=f"{prediction['champion']['name']}"))
                grid.add_widget(Label(text=f"{prediction['predicted'] * 100:.2f}%"))
            self.root.ids.suggestions.add_widget(
                Label(text=f"Current prediction: {prediciton_data['current_prediction'] * 100:.2f}%", size_hint_y=.2))
            self.root.ids.suggestions.add_widget(grid)


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    MainApp().run()
