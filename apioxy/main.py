"""
APIOxy's main module.
"""

import logging
import os
import time
from typing import Optional

from t3 import T3
from t3.common import get_rmg_species_from_a_species_dict
from t3.main import RMG_THERMO_LIB_BASE_PATH
from t3.schema import RMGSpecies

from apioxy.common import PROJECTS_BASE_PATH, VERSION, initialize_log
from apioxy.levels import LEVELS
from apioxy.logger import Logger


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
        self.t0 = time.time()  # initialize the timer

        self.project = project
        self.project_directory = project_directory or os.path.join(PROJECTS_BASE_PATH, project)
        if not os.path.isdir(self.project_directory):
            os.makedirs(self.project_directory)

        self.apioxy = apioxy or dict()
        self.t3 = t3 or dict()
        self.rmg = rmg or dict()
        self.qm = qm or dict()
        self.demo = demo
        self.verbose = verbose

        # initialize the logger
        self.logger = Logger(project=self.project,
                             project_directory=self.project_directory,
                             verbose=self.verbose,
                             t0=self.t0,
                             )
        # log the input
        self.logger.log_args(schema={'apioxy': apioxy,
                                     't3': t3,
                                     'rmg': rmg,
                                     'qm': qm,
                                     'demo': demo,
                                     'verbose': verbose,
                                     })

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
        self.logger.log('Running APIOxy in Demo mode')
        raise NotImplementedError('demo under construction.')

    def apply_default_settings(self):
        """
        Apply default settings where not specified.
        Also checks syntax of self.apioxy['api_structures'] using T3's schema.
        """
        # apioxy
        if 'model_level' not in self.apioxy:
            self.logger.warning('Setting model_level to custom')
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
            self.logger.debug('Not running in parallel.')
            self.apioxy['run_in_parallel'] = False
        if 'zeneth_output_paths' not in self.apioxy:
            self.apioxy['zeneth_output_paths'] = [None] * len(self.apioxy['api_structures'])
            self.logger.warning('No Zeneth output files were given.')
        elif len(self.apioxy['zeneth_output_paths']) != len(self.apioxy['api_structures']):
            raise ValueError(f"The length of zeneth_output_paths ({len(self.apioxy['zeneth_output_paths'])}) "
                             f"must be equal to the length of api_structures ({self.apioxy['api_structures']}).")

        # t3
        if 'options' not in self.t3:
            self.t3['options'] = dict()
        if 'library_name' not in self.t3['options']:
            self.t3['options']['library_name'] = 'APIOxy'
            self.logger.debug('Setting library_name to APIOxy.')
        if 'sensitivity' not in self.t3:
            self.t3['sensitivity'] = {'adapter': 'RMG',
                                      'top_SA_species': 10,
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

        rmg_thermo_libs = [subdir_tuple[0] for subdir_tuple in os.walk(RMG_THERMO_LIB_BASE_PATH)]
        if self.t3['options']['library_name'] in rmg_thermo_libs:
            # this library already exists, use it from the firts T3 iteration
            self.rmg['database']['thermo_libraries'].append(self.t3['options']['library_name'])

        # Todo: Do the same for kinetics libraries

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

        # arc (qm)
        if 'adapter' not in self.qm:
            self.qm['adapter'] = 'ARC'
        if self.apioxy['model_level'] in [1, 2, 3]:
            self.qm.update(LEVELS[self.apioxy['model_level']])

    def set_species_constraints(self, species_dict):
        """
        Set RMG species constraints for an API

        Args:
            species_dict (dict): THe dictionary representation of the API species.
        """
        rmg_spc = get_rmg_species_from_a_species_dict(RMGSpecies(**species_dict).dict())

        # Count the number of each element in the molecule
        element_dict = {}
        for atom in rmg_spc.molecule[0].vertices:
            symbol = atom.element.symbol
            element_dict[symbol] = element_dict.get(symbol, 0) + 1

        species_constraints = {'allowed': ['input species', 'seed mechanisms', 'reaction libraries'],
                               'max_C_atoms': element_dict['C'] + 2 if 'C' in element_dict else 0,
                               'max_O_atoms': element_dict['O'] + 6 if 'O' in element_dict else 6,
                               'max_N_atoms': element_dict['N'] if 'N' in element_dict else 0,
                               'max_Si_atoms': element_dict['Si'] if 'Si' in element_dict else 0,
                               'max_S_atoms': element_dict['S'] if 'S' in element_dict else 0,
                               'max_heavy_atoms': sum(element_dict[element] for element in element_dict.keys()
                                                      if element != 'H') + 10,
                               'max_radical_electrons': 1,
                               'max_singlet_carbenes': 0,
                               'max_carbene_radicals': 0,
                               'allow_singlet_O2': True,
                               }
        self.rmg['species_constraints'] = species_constraints

    def execute(self):
        """
        Execute APIOxy by calling T3 with the respective arguments.

        Todo:
            Make self.apioxy['run_in_parallel'] functional
        """
        for i, api_dict in enumerate(self.apioxy['api_structures']):
            rmg = self.rmg.copy()
            api_dict_copy = api_dict.copy()
            if self.apioxy['model_level'] != 0:
                # Rename the API so RMG won't H_abstract from the API (but only if level != 0)
                api_dict_copy['label'] = 'API'
            if 'seed_all_rads' not in api_dict_copy:
                api_dict_copy['seed_all_rads'] = ['radical', 'peroxyl']
            self.set_species_constraints(api_dict_copy)
            rmg['species'].append(api_dict_copy)
            if len(self.apioxy['api_structures']) > 1:
                project = f"{i + 1}_{api_dict['label']}"
                project_directory = os.path.join(self.project_directory, f"{i + 1}_{api_dict['label']}")
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
        self.logger.log_footer()
