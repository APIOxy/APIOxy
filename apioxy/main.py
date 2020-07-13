"""
APIOxy's main module.
"""

import logging
import os
from typing import Optional

from t3 import T3
from t3.schema import RMGSpecies

from apioxy.common import PROJECTS_BASE_PATH, VERSION, initialize_log
from apioxy.levels import LEVELS


class APIOxy(object):
    """
    The main APIOxy class.

    Todo:
        Use self.apioxy['zeneth_output_paths']
    """

    def __init__(self,
                 project: str,
                 project_directory: Optional[str] = None,
                 apioxy: Optional[dict] = None,
                 t3: Optional[dict] = None,
                 rmg: Optional[dict] = None,
                 qm: Optional[dict] = None,
                 demo: bool = False,
                 verbose=logging.INFO,
                 ) -> None:
        self.__version__ = VERSION

        self.project = project if project is not None else str()
        self.project_directory = project_directory or os.path.join(PROJECTS_BASE_PATH, project)
        self.apioxy = apioxy or dict()
        self.t3 = t3 or dict()
        self.rmg = rmg or dict()
        self.qm = qm or dict()
        self.demo = demo
        self.verbose = verbose

        initialize_log(log_file=os.path.join(self.project_directory, 'apioxy.log'),
                       project=self.project,
                       project_directory=self.project_directory,
                       verbose=self.verbose,
                       )

        if self.demo:
            self.set_up_demo()
        else:
            self.apply_default_settings()

    def set_up_demo(self):
        """
        Set up a demo APIOxy job.

        Todo:
            implement settings for demo
        """
        self.project = 'apioxy_demo'
        raise NotImplementedError('demo under construction.')

    def apply_default_settings(self):
        """
        Apply default settings where not specified.
        Also checks syntax of self.apioxy['api_structures'] using T3's schema.
        """
        # apioxy
        if 'model_level' not in self.apioxy:
            self.apioxy['model_level'] = 'custom'
        if 'api_structures' not in self.apioxy or not self.apioxy['api_structures']:
            raise ValueError('APIOxy cannot be executed without specifying API structures.\n'
                             'Specify "api_structures" under the "apioxy" block of the input.')
        if not isinstance(self.apioxy['api_structures'], list):
            self.apioxy['api_structures'] = [self.apioxy['api_structures']]
        for api_dict in self.apioxy['api_structures']:
            # not using the output, just passing through the schema
            RMGSpecies(**api_dict)
        if 'run_in_parallel' not in self.apioxy:
            self.apioxy['run_in_parallel'] = False
        if 'zeneth_output_path' not in self.apioxy:
            self.apioxy['zeneth_output_paths'] = None
            logging.warning('No Zeneth output files were given.')
        elif len(self.apioxy['zeneth_output_paths']) != len(self.apioxy['api_structures']):
            raise ValueError(f"The length of zeneth_output_path ({len(self.apioxy['zeneth_output_paths'])}) "
                             f"must be equal to the length of api_structures ({self.apioxy['api_structures']}).")

        # t3
        if 'library_name' not in self.t3:
            self.t3['library_name'] = 'APIOxy'
        if 'sensitivity' not in self.t3:
            self.t3['sensitivity'] = {'top_SA_species': 10,
                                      'top_SA_reactions': 10,
                                      }

        # rmg
        if 'database' not in self.rmg:
            self.rmg['database'] = {'thermo_libraries': ['BurkeH2O2',
                                                         'thermo_DFT_CCSDTF12_BAC',
                                                         'DFT_QCI_thermo',
                                                         'primaryThermoLibrary',
                                                         'APIOxy',
                                                         'CBS_QB3_1dHR',
                                                         'CurranPentane'],
                                    'kinetics_libraries': ['BurkeH2O2inN2',
                                                           'api_soup',
                                                           'NOx2018',
                                                           'APIOxy',
                                                           'Klippenstein_Glarborg2016'],
                                    }
        if 'model' not in self.rmg:
            self.rmg['model'] = {'core_tolerance': 0.20}
        if 'options' not in self.rmg:
            self.rmg['options'] = {'save_html': True}
        if 'reactors' not in self.rmg:
            self.rmg['reactors'] = {'type': 'liquid batch constant T V',
                                    'T': 313,
                                    'termination_time': [72, 'hrs'],
                                    }
        if 'species' not in self.rmg:
            raise ValueError('APIOxy cannot be executed without specifying the species mixture.')

        # Todo: set self.rmg['species_constraints'] here

        # arc (qm)
        if 'adapter' not in self.qm:
            self.qm['adapter'] = 'ARC'
        if self.apioxy['model_level'] in [1, 2, 3]:
            self.qm.update(LEVELS[self.apioxy['model_level']])

    def execute(self):
        """
        Execute APIOxy by calling T3 with the respective arguments.

        Todo:
            Make self.apioxy['run_in_parallel'] functional
        """
        for i, api_dict in enumerate(self.apioxy['api_structures']):
            rmg = self.rmg.copy()
            rmg['species'] = api_dict
            if len(self.apioxy['api_structures']) > 1:
                project = f"{i}_{api_dict['label']}"
                project_directory = os.path.join(self.project_directory, f"{i}_{api_dict['label']}")
            else:
                project = self.project
                project_directory = self.project_directory
            t3_object = T3(project=project,
                           rmg=self.rmg,
                           t3=self.t3,
                           qm=self.qm,
                           project_directory=project_directory,
                           verbose=self.verbose,
                           clean_dir=False,
                           )
            t3_object.execute()
