from __future__ import print_function
import inspect
import os
from dash.dependencies import Input, Output
from dash.dash import Dash  # noqa: F401


class EasyDash(Dash):
    """Wraps Dash apps and adds useful functions"""

    def auto_callback(self, debug=False):
        """Creates callbacks using function name."""

        valid_prefix_names = ["update_", "callback_"]

        def check_prefix(in_name):
            for prefix_name in valid_prefix_names:
                if prefix_name in in_name:
                    return in_name.find(prefix_name) + len(prefix_name)

            raise ValueError(
                "auto_callback requires name to start with {}".format(
                    valid_prefix_names
                )
            )

        def process_output(callback_func):
            callback_name = getattr(callback_func, "__name__", "")
            comp_prop_start_idx = check_prefix(callback_name)
            comp_prop_name = callback_name[comp_prop_start_idx:]
            property_start = comp_prop_name.rfind("_of_")
            if property_start >= 1:
                comp_name = comp_prop_name[property_start + 4 :]
                prop_name = comp_prop_name[:property_start]
            else:
                # assume children if no underscore
                comp_name = comp_prop_name
                prop_name = "children"
            return Output(component_id=comp_name, component_property=prop_name)

        def process_input(callback_func):
            if hasattr(inspect, "getfullargspec"):
                spec_func = getattr(inspect, "getfullargspec")
            elif hasattr(inspect, "getargspec"):
                # pylint: disable=maybe-no-member, deprecated-method
                spec_func = getattr(inspect, "getargspec")
            else:
                raise ValueError("Requires Python 2/3")

            spec_args = spec_func(callback_func).args
            input_list = []
            for c_comp_prop_arg in spec_args:
                property_start = c_comp_prop_arg.rfind("_of_")
                if property_start >= 1:
                    prop_name = c_comp_prop_arg[:property_start]
                    comp_name = c_comp_prop_arg[property_start + 4 :]
                else:
                    # assume value if no underscore
                    comp_name = c_comp_prop_arg
                    prop_name = "value"
                input_list += [
                    Input(component_id=comp_name, component_property=prop_name)
                ]
            return input_list

        def wrap_callback(callback_func):
            # process outputs
            output = process_output(callback_func)
            if debug:
                print("Output:", output)
            # process inputs
            inputs = process_input(callback_func)
            if debug:
                print("Inputs:", inputs)
            return self.callback(output, inputs=inputs)(callback_func)

        return wrap_callback

    def _repr_html_(self):
        return self.show_app()

    def show_app(self, port=9999, width="100%", height=700, offline=False):
        """Show the dash app inside of jupyter."""
        # for cases inside of a jupyterhub or binder
        from IPython import display

        in_binder = None

        in_binder = (
            "JUPYTERHUB_SERVICE_PREFIX" in os.environ
            if in_binder is None
            else in_binder
        )
        if in_binder:
            base_prefix = "{}proxy/{}/".format(
                os.environ["JUPYTERHUB_SERVICE_PREFIX"], port
            )
            url = "https://hub.mybinder.org{}".format(base_prefix)
            self.config.requests_pathname_prefix = base_prefix
        else:
            url = "http://localhost:%d" % port

        iframe = '<a href="{url}" target="_new">Open in new window</a>'
        iframe += '<hr><iframe src="{url}" width={width} height={height}></iframe>'
        iframe = iframe.format(url=url, width=width, height=height)
        display.display_html(iframe, raw=True)
        if offline:
            self.css.config.serve_locally = True
            self.scripts.config.serve_locally = True
        return self.run_server(
            debug=False, host="0.0.0.0", port=port  # needs to be false in Jupyter
        )
