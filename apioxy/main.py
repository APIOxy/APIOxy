"""
APIOxy's main module.
"""

import logging
import os

from apioxy.common import VERSION, apioxy_path, str_to_float_fail_none


class APIOxy(object):
    """
    The main APIOxy class.


    """

    def __init__(self,
                 project: str = None,
                 project_directory: str = None,
                 apioxy_settings: dict = None,
                 t3_settings: dict = None,
                 demo: bool = False,
                 try_defaults_if_empty: bool = True,
                 verbose=logging.INFO,
                 ) -> None:
        self.__version__ = VERSION

        self.project = project if project is not None else str()
        self.apioxy_settings = apioxy_settings if apioxy_settings is not None else dict()
        self.t3_settings = t3_settings if t3_settings is not None else dict()
        self.demo = demo
        self.verbose = verbose
        self.try_defaults_if_empty = try_defaults_if_empty
        self.project_directory = project_directory if project_directory is not None else str()

        self.mixture = None
        self.mode = None
        self.model_level = None
        self.temperature_deg_c = None
        self.sa_observables = None
        self.rmg_model_termination_time_hr = None
        self.rmg_model_termination_conversion = None
        self.rmg_model_termination_rate_ratio = None
        self.apioxy_run_time_limit_hr = None
        self.rmg_libraries_save_name = None
        self.rmg_libraries_to_load = None
        self.api_structures = None
        self.zeneth_output_path = None

        self.temperature_deg_c_is_valid = False
        self.rmg_model_termination_time_hr_is_valid = False

        if self.demo:
            self.set_up_demo()
        else:
            self.set_apioxy_settings()
            self.set_t3_settings()
            if self.try_defaults_if_empty:
                self.apply_default_settings()

        self.check_initialization()

        initialize_log(log_file=os.path.join(self.project_directory, 'apioxy.log'), project=self.project,
                       project_directory=self.project_directory, verbose=self.verbose)

    def check_initialization(self):
        """
        Check if any error exists in an instance of APIOxy object.
        """
        # todo: improve error message, give examples
        if not self.project:
            raise ValueError('A non-empty project name must be provided for a new APIOxy project.')
        if not self.mixture:
            raise ValueError('Mixture cannot be empty.')
        # todo: check if API exists in mixture
        if not self.temperature_deg_c_is_valid:
            raise ValueError('Temperature is not valid.')
        if not self.rmg_model_termination_time_hr_is_valid:
            raise ValueError('RMG model termination time is not valid.')

    def set_up_demo(self):
        """
        Set up a demo APIOxy job.
        """
        # todo: implement settings for demo
        self.project = 'apioxy_demo'
        raise NotImplementedError('demo under construction.')

    def set_apioxy_settings(self):
        """
        Create APIOxy attributes from apioxy_settings dictionary.
        """
        s = self.apioxy_settings

        self.project_directory = s.get('project_directory', str())
        self.project_directory = self.project_directory if self.project_directory \
            else os.path.join(apioxy_path, 'Projects', self.project)

        self.mixture = s.get('mixture', list())
        self.mode = s.get('mode', str())
        self.model_level = s.get('model_level', str())
        self.sa_observables = s.get('sa_observables', list())
        self.rmg_libraries_save_name = s.get('rmg_libraries_save_name', str())
        self.rmg_libraries_to_load = s.get('rmg_libraries_to_load', list())
        self.api_structures = s.get('api_structures', list())
        self.zeneth_output_path = s.get('zeneth_output_path', str())

        self.rmg_model_termination_conversion = str_to_float_fail_none(s.get('rmg_model_termination_conversion', None))
        self.rmg_model_termination_rate_ratio = str_to_float_fail_none(s.get('rmg_model_termination_rate_ratio', None))
        self.apioxy_run_time_limit_hr = str_to_float_fail_none(s.get('apioxy_run_time_limit_hr', None))

        self.temperature_deg_c = str_to_float_fail_none(s.get('temperature_deg_c', None))
        # temperature is still valid even if its numerical value is 0. Do not just check `if self.temperature_deg_c`.
        self.temperature_deg_c_is_valid = self.temperature_deg_c is not None

        self.rmg_model_termination_time_hr = str_to_float_fail_none(s.get('rmg_model_termination_time_hr', None))
        # time is not valid if its numerical value is 0.
        self.rmg_model_termination_time_hr_is_valid = True if self.rmg_model_termination_time_hr else False

    def set_t3_settings(self):
        pass

    def apply_default_settings(self):
        """
        Use default settings.
        """
        self.mode = self.mode if self.mode else 'modeling'
        self.model_level = self.model_level if self.model_level else 'fastest'
        self.rmg_libraries_save_name = self.rmg_libraries_save_name if self.rmg_libraries_save_name else self.project

        if not self.temperature_deg_c_is_valid:
            self.temperature_deg_c = 40.0
            self.temperature_deg_c_is_valid = True

        if not self.rmg_model_termination_time_hr_is_valid:
            self.rmg_model_termination_time_hr = 72.0
            self.rmg_model_termination_time_hr_is_valid = True


















