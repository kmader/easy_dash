from __future__ import print_function
import inspect

from dash.dependencies import Input, Output, State
from dash.dash import Dash  # noqa: F401

class EasyDash(Dash):
    def auto_callback(self, debug=False):
        """Creates callbacks using function name
        """

        valid_prefix_names = ['update_', 'callback_']

        def check_prefix(in_name):
            for prefix_name in valid_prefix_names:
                if prefix_name in in_name:
                    return in_name.find(prefix_name) + len(prefix_name)

            raise ValueError(
                'auto_callback requires name to start with {}'.format(
                    valid_prefix_names)
            )

        def process_output(callback_func):
            callback_name = getattr(callback_func, '__name__', '')
            comp_prop_start_idx = check_prefix(callback_name)
            comp_prop_name = callback_name[comp_prop_start_idx:]
            property_start = comp_prop_name.rfind('_')
            if property_start >= 1:
                prop_name = comp_prop_name[property_start + 1:]
                comp_name = comp_prop_name[:property_start]
            else:
                # assume children if no underscore
                comp_name = comp_prop_name
                prop_name = 'children'
            return Output(component_id=comp_name,
                          component_property=prop_name)

        def process_input(callback_func):
            if sys.version_info[0] == 3:
                # pylint: disable=maybe-no-member
                spec_args = inspect.getfullargspec(callback_func).args
            elif sys.version_info[0] == 2:
                # pylint: disable=maybe-no-member, deprecated-method
                spec_args = inspect.getargspec(callback_func).args
            else:
                raise ValueError(
                    "Requires Python 2 or 3, {}".format(
                        sys.version_info)
                )

            input_list = []
            for c_comp_prop_arg in spec_args:
                property_start = c_comp_prop_arg.rfind('_')
                if property_start >= 1:
                    comp_name = c_comp_prop_arg[:property_start]
                    prop_name = c_comp_prop_arg[property_start + 1:]
                else:
                    # assume value if no underscore
                    comp_name = c_comp_prop_arg
                    prop_name = 'value'
                input_list += [Input(component_id=comp_name,
                                     component_property=prop_name)]
            return input_list

        def wrap_callback(callback_func):
            # process outputs
            output = process_output(callback_func)
            if debug:
                print('Output:', output)
            # process inputs
            inputs = process_input(callback_func)
            if debug:
                print('Inputs:', inputs)
            return self.callback(output, inputs=inputs)(callback_func)

        return wrap_callback