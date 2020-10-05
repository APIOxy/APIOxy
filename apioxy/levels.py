"""
APIOxy levels module
used for storing default levels of theory
"""

from arc.level import Level


# Not implementing the "ML" and "0" levels

LEVELS = {1: {'sp_level': Level(method='b3lyp',
                                basis='6-31g(d,p)',
                                ),
              'opt_level': Level(method='b3lyp',
                                 basis='6-31g(d,p)',
                                 ),
              },
          2: {'sp_level': Level(method='wB97xd',
                                basis='def2TZVP',
                                solvation_method='SMD',
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
                                # solvation_method='COSMO/tzvpd-fine',
                                solvation_method='SMD',
                                solvent='water',
                                ),
              'opt_level': Level(method='wB97xd',
                                 basis='def2SVP',
                                 ),
              },
          }
