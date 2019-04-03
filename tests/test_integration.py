import json
from multiprocessing import Value
import datetime
import itertools
import re
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import dash_dangerously_set_inner_html
import dash_flow_example

import dash_html_components as html
import dash_core_components as dcc

import dash

from dash.dependencies import Input, Output, State
from dash.exceptions import (
    PreventUpdate,
    DuplicateCallbackOutput,
    CallbackException,
    MissingCallbackContextException,
    InvalidCallbackReturnValue,
)

from easy_dash import EasyDash

from .IntegrationTests import IntegrationTests
from .utils import assert_clean_console, invincible, wait_for


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
        app = EasyDash(__name__)
        app.layout = html.Div(
            [
                dcc.Input(id="input", value="initial value"),
                html.Div(html.Div([1.5, None, "string", html.Div(id="output1")])),
            ]
        )

        call_count = Value("i", 0)

        @app.auto_callback()
        def update_output1_children(input_value):
            call_count.value = call_count.value + 1
            return input_value

        self.startServer(app)

        self.wait_for_text_to_equal("#output1", "initial value")
        self.percy_snapshot(name="auto-callback-1")

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
        self.percy_snapshot(name="auto-callback-2")

        self.assertEqual(
            call_count.value,
            # an initial call to retrieve the first value
            # and one for clearing the input
            2 +
            # one for each hello world character
            len("hello world"),
        )

        assert_clean_console(self)
