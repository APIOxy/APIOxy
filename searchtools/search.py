#!/usr/bin/env python
# encoding: utf-8
"""
search species and reactions in rmg mechanism
"""
from IPython.display import display
from rmgpy.molecule import Molecule

def find_species_by_label(rmg_spc: list,label: str) -> Molecule:
    """
    find species by label and returns rmg molecules
    :param rmg_spc: (list) rmg species list form RMGsp,RMGrxn=load_chemkin_file(chemkin_file,dict_file)
    :param label: (str) label of the species
    :return: rmg molecules
    """

    mol = None
    for sp in rmg_spc:
        if label == sp.label:
            print(sp.label,sp.molecule)
            display(sp)
            mol =sp
    if mol is None:
        print ("couldn't find the species")
    else:
        return mol

def find_species_by_smiles(rmg_spc: list, smiles: str) -> Molecule:
    """
    for list of rmg species find species by smiles
    :param rmg_spc: list of rmg species list
    :param smiles: (str) species as smiles
    :return: rmg species
    """

    sp1=Molecule().from_smiles(smiles)
    display(sp1)
    mol = None
    res=sp1.generate_resonance_structures()
    for i,x in enumerate(rmg_spc):
        for s in res:
            if x.is_isomorphic(s):
                print(x.molecule)
                print(x.thermo.comment)
                mol = x
    if mol is None:
        print ("couldn't find the species")
    else:
        return mol

def find_reactions_by_label(rmg_rxn: list, label: str) -> list:
    """
    for given species find all the reactions involved in
    RMGrxn: is from RMGsp,RMGrxn=load_chemkin_file(chemkin_file,dict_file) or list of RMG reactions
    :param rmg_rxn: (list) rmg reaction list
    :param label: (str) label of the species
    :return: list of reactions
    """

    x1 = []
    for rxn in rmg_rxn:
        if label in [x.label for x in rxn.reactants + rxn.products]:
            x1.append(rxn)
            print(rxn.index, [y.label for y in rxn.reactants], "->", [y.label for y in rxn.products])
    return x1

def display_reactions(rxn_list:list, t = 313.0):
    """
    print list of reactions
    :param rxn_list: list of rmg reactions
    :return: None
    """
    for react in rxn_list:
        print(react.index, react)
        display(react)
        if hasattr(react, 'library'):
            print("reaction library:",react.library)
        else:
            print("reaction object has no library attribute")
        print('---forward kinetic---')
        print(react.kinetics)
        kf = react.get_rate_coefficient(t)
        print(f'forward rate at {t}: {kf}')
        print('---reverse kinetic---')
        print(react.generate_reverse_rate_coefficient())
        kr = react.generate_reverse_rate_coefficient().get_rate_coefficient(t)
        print(f'reverse rate at {t}: {kr}')
        print('-----------------------------------------------------\n')

def find_reaction_by_index(rxn:list,num:int)-> object:
    """
    find reactions by chemkin reaction index
    :param rxn: (list) rmg reaction list
    :param num: (int) chemkin reaction index
    :return: rmg reaction
    """
    #x1 = []
    for react in rxn:
        if react.index==num:
            #x1.append(react)
            display(react)
            if hasattr(react, 'library'):
                print(react.library)
            else:
                print("reaction object has no library attribute")
            print(react.kinetics,"\n")
            return react

def find_all_reaction_from_library(rxn:list,lib: str)->list:
    """
    find all the reactions form a specific library
    :param rxn: RMG reaction list
    :param lib: (str) rmg library name
    :return: (list) of reactions
    """
    i=1
    x1=[]
    for react in rxn:
        if hasattr(react, 'library'):
            if react.library==lib:
                x1.append(react)
                print(i,react)
                display(react)
                print(react.kinetics,"\n")
                i=i+1

    return x1