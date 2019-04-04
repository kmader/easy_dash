# easy_dash
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/kmader/easy_dash/master)
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![CircleCI](https://circleci.com/gh/kmader/easy_dash.svg?style=svg)](https://circleci.com/gh/kmader/easy_dash)
[![codecov](https://codecov.io/gh/kmader/easy_dash/branch/master/graph/badge.svg)](https://codecov.io/gh/kmader/easy_dash/branch)
[![This project is using Percy.io for visual regression testing.](https://percy.io/static/images/percy-badge.svg)](https://percy.io)

A simple wrapper library for making Dash apps easier to build
## Overview

The idea is to make [Dash](https://github.com/plotly/dash) easier to use for new developers, harder to make bugs with,
and include a few common patterns and integrations like matplotlib support and `interact` from ipywidgets

## Usage

#### Simple Names Automagic Callbacks

```python
from easy_dash import EasyDash
import dash_html_components as html
import dash_core_components as dcc

app = EasyDash(__name__)
app.layout = html.Div(
    [
        dcc.Input(id="input", value="initial value"),
        html.Div(id="output1")
    ]
)

@app.auto_callback()
def update_output1(input):
    return input

```

#### Detailed Names Automagic Callbacks
```python
from easy_dash import EasyDash
import dash_html_components as html
import dash_core_components as dcc

app = EasyDash(__name__)
app.layout = html.Div(
    [
        dcc.Input(id="input", value="initial value"),
        html.Div(id="output1")
    ]
)

@app.auto_callback()
def update_children_of_output1(value_of_input):
    return value_of_input

```
