from multiprocessing import Value

import dash_core_components as dcc
import dash_html_components as html
import matplotlib
import matplotlib.pyplot as plt
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from easy_dash import EasyDash
from .IntegrationTests import IntegrationTests
from .utils import assert_clean_console, invincible, wait_for

matplotlib.use("Agg")


class Tests(IntegrationTests):
    def setUp(self):
        def wait_for_element_by_id(id):
            wait_for(
                lambda: None
                is not invincible(lambda: self.driver.find_element_by_id(id))
            )
            return self.driver.find_element_by_id(id)

        self.wait_for_element_by_id = wait_for_element_by_id

    def test_auto_callback(self):
        app = EasyDash("auto_callback")
        app.layout = html.Div(
            [
                dcc.Input(id="input", value="initial value"),
                html.Div(html.Div([1.5, None, "string", html.Div(id="output1")])),
                html.Div(id="output2"),
            ]
        )

        call_count = Value("i", 0)

        @app.auto_callback()
        def update_output1(input):
            call_count.value = call_count.value + 1
            return input

        @app.auto_callback()
        def update_children_of_output2(value_of_input):
            return value_of_input

        self.startServer(app, 8050)

        self.wait_for_text_to_equal("#output1", "initial value")
        self.percy_snapshot(name="auto-callback-1")

        self.wait_for_text_to_equal("#output2", "initial value")
        self.percy_snapshot(name="auto-callback-2")

        input1 = self.wait_for_element_by_id("input")

        chain = (
            ActionChains(self.driver)
            .click(input1)
            .send_keys(Keys.HOME)
            .key_down(Keys.SHIFT)
            .send_keys(Keys.END)
            .key_up(Keys.SHIFT)
            .send_keys(Keys.DELETE)
        )
        chain.perform()

        input1.send_keys("hello world")

        self.wait_for_text_to_equal("#output1", "hello world")
        self.percy_snapshot(name="auto-callback-3")

        self.wait_for_text_to_equal("#output2", "hello world")
        self.percy_snapshot(name="auto-callback-4")

        self.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value
            # and one for clearing the input
            2 +
            # one for each hello world character
            len("hello world"),
        )

        assert_clean_console(self)

    def test_mpl_callback(self):
        app = EasyDash("mpl_callback")
        app.layout = html.Div(
            [
                dcc.Input(id="plot_size", value="5"),
                html.Div(id="output_mpl"),
                html.Div(id="plot"),
            ]
        )

        @app.auto_callback()
        def update_output_mpl(value_of_plot_size):
            return "New Size: {}".format(value_of_plot_size)

        @app.mpl_callback()
        def update_children_of_plot(value_of_plot_size):
            height = float(value_of_plot_size)
            fig, ax1 = plt.subplots(1, 1, figsize=(height, 5))
            ax1.plot([0, 1, 1, 0], [0, 0, 1, 1], "r-.")
            ax1.set_title(height)
            return fig

        self.startServer(app, 8052)

        self.wait_for_text_to_equal("#output_mpl", "New Size: 5")
        self.percy_snapshot(name="mpl-callback-1")

        input_ps = self.wait_for_element_by_id("plot_size")

        chain = (
            ActionChains(self.driver)
            .click(input_ps)
            .send_keys(Keys.HOME)
            .key_down(Keys.SHIFT)
            .send_keys(Keys.END)
            .key_up(Keys.SHIFT)
            .send_keys(Keys.DELETE)
        )
        chain.perform()

        input_ps.send_keys("20")
        self.wait_for_text_to_equal("#output_mpl", "New Size: 20")
        self.percy_snapshot(name="mpl-callback-2")

        assert_clean_console(self)
