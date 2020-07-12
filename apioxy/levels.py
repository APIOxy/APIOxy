"""
APIOxy levels module
used for storing default levels of theory
"""

from arc.level import Level


# Not implementing the "ML" and "0" levels

LEVELS = {1: {'sp_level': Level(method='wB97xd',
                                basis='def2TZVP',
                                solvation_method='COSMO/tzvpd-fine',  # Turbomol / Gaussian?
                                solvent='water',  # mixture
                                ),
              'opt_level': Level(method='wB97xd',
                                basis='def2SVP',
                                ),
              },
          2: {'sp_level': Level(method='wB97MV',
                                basis='def2TZVP',
                                solvation_method='COSMO/tzvpd-fine',
                                solvent='water',
                                ),
              'opt_level': Level(method='wB97xd',
                                basis='def2SVP',
                                ),
              },
          3: {'sp_level': Level(method='DLPNO',
                                basis='def2TZVP',
                                auxiliary_basis='def2TZVP/C',
                                args={'keyword': {'dlpno_threshold': 'normalPNO'}},
                                solvation_method='COSMO/tzvpd-fine',
                                solvent='water',
                                ),
              'opt_level': Level(method='wB97xd',
                                 basis='def2SVP',
                                ),
              },
          }
