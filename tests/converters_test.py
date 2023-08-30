#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  4 12:57:39 2022

@author: lpeurey
"""
from conversations import Conversation
from conversations.standards import standard_columns
from collections import defaultdict
import pytest
import pandas as pd

CSV_INPUT = 'tests/data/example_2.csv'
TXT_INPUT = 'tests/data/example_2.txt'
RTTM_INPUT = 'tests/data/example.rttm'
ITS_INPUT = 'tests/data/example_lena_new.its'
EMPTY_FILE = 'tests/data/empty_file'

@pytest.fixture()
def conv():
    return Conversation(**standard_columns)

@pytest.mark.parametrize("file,test", [
       (CSV_INPUT,'correct'),
       (EMPTY_FILE,'empty'),])
def test_import_csv(conv, file, test):
    caught = False
    try:
        res = conv.from_csv(file)
    except Exception as e:
        caught = True    
    truth = pd.read_csv('tests/truth/df-csv.csv')
    if test == 'correct':
        #res.to_csv('tests/truth/2df-csv.csv', index=False) ###TMP
        pd.testing.assert_frame_equal(res.reset_index(drop=True), truth.reset_index(drop=True), check_like=True)
    elif test == 'empty' : assert caught
    else : raise NotImplementedError('this test is not captured')

RTTM_MAP = (defaultdict(lambda: pd.NA,
                         {"CHI": "OCH",
                          "KCHI": "CHI",
                          "FEM": "FEM",
                          "MAL": "MAL"}))
    
@pytest.mark.parametrize("mapg,file,source,test", [
       (RTTM_MAP,RTTM_INPUT,None,'mapping'),
       (None,RTTM_INPUT,None,'vanilla'),
       ('str',RTTM_INPUT,None, 'no-dict'),
       (None,RTTM_INPUT,'namibie_aiku_20160714_1', 'source_file'),
       (RTTM_MAP,RTTM_INPUT,'namibie_aiku_20160714_1', 'source_and_map'),
       (None,EMPTY_FILE,None,'empty')])
def test_import_rttm(conv,mapg,file,source,test):
    caught = False
    try:
        res = conv.from_rttm(file, mapg, source)
    except Exception as e:
        caught = True
    
    truth = pd.read_csv('tests/truth/df-rttm.csv')
    truth_mapped = truth.copy()
    truth_mapped.speaker_type = truth_mapped.speaker_type.map(RTTM_MAP)
    
    if test == "mapping":
        pd.testing.assert_frame_equal(res.reset_index(drop=True), truth_mapped.reset_index(drop=True), check_like=True)
    elif test == "vanilla": 
        res.to_csv('tests/truth/2df-rttm.csv', index=False) ###TMP
        pd.testing.assert_frame_equal(res.reset_index(drop=True), truth.reset_index(drop=True), check_like=True)
    elif test == "no-dict" : assert caught
    elif test == 'source_file' : pd.testing.assert_frame_equal(res.reset_index(drop=True), truth.head(5).reset_index(drop=True), check_like=True)
    elif test == 'source_and_map' : pd.testing.assert_frame_equal(res.reset_index(drop=True), truth_mapped.head(3).reset_index(drop=True), check_like=True)
    elif test == 'empty' : pd.testing.assert_frame_equal(res.reset_index(drop=True), pd.DataFrame(columns=['type', 'file', 'chnl', 'tbeg', 'tdur', 'ortho', 'stype', 'name','conf', 'slat', 'segment_onset', 'segment_offset', 'speaker_type']).reset_index(drop=True), check_like=True, check_dtype=False)
    else : raise NotImplementedError('this test is not captured')


ITS_MAP = defaultdict(
        lambda: pd.NA, {"CHN": "CHI", "CXN": "OCH", "FAN": "FEM", "MAN": "MAL"}
    )

@pytest.mark.parametrize("mapg,file,source,test", [
       (ITS_MAP,ITS_INPUT,None,'mapping'),
       (None,ITS_INPUT,None,'vanilla'),
       ('str',ITS_INPUT,None, 'no-dict'),
       (None,ITS_INPUT,1, 'source_file'),
       (ITS_MAP,ITS_INPUT,2, 'source_and_map'),
       (None,EMPTY_FILE,None,'empty')])  
def test_import_its(conv,mapg,file,source,test):
    caught = False
    try:
        res = conv.from_its(file, mapg, source)
    except Exception as e:
        caught = True
        
    truth = pd.read_csv('tests/truth/df-its.csv')
    truth_mapped = truth.copy()
    truth_mapped.speaker_type = truth_mapped.speaker_type.map(ITS_MAP)
    truth_mapped.dropna(inplace=True)
    
    if test == "mapping": pd.testing.assert_frame_equal(res.reset_index(drop=True), truth_mapped.reset_index(drop=True), check_like=True)
    elif test == "vanilla": pd.testing.assert_frame_equal(res.reset_index(drop=True), truth.reset_index(drop=True), check_like=True)
    elif test == "no-dict" : assert caught
    elif test == 'source_file' : pd.testing.assert_frame_equal(res.reset_index(drop=True), truth.head(23289).reset_index(drop=True), check_like=True)
    elif test == 'source_and_map' : pd.testing.assert_frame_equal(res.reset_index(drop=True), pd.DataFrame(columns=['segment_onset','segment_offset', 'speaker_type']).reset_index(drop=True), check_like=True)
    elif test == 'empty' : assert caught
    else : raise NotImplementedError('this test is not captured')
    
@pytest.mark.parametrize("file,test", [
       (TXT_INPUT,'correct'),
       (EMPTY_FILE,'empty'),])
def test_import_txt(conv, file, test):
    caught = False
    try:
        res = conv.from_txt(file)
    except Exception as e:
        caught = True    
    truth = pd.read_csv('tests/truth/df-csv.csv')
    #res.to_csv('tests/truth/df-csv.csv',index=False)
    if test == 'correct': pd.testing.assert_frame_equal(res.reset_index(drop=True), truth.reset_index(drop=True), check_like=True)
    elif test == 'empty' : assert caught
    else : raise NotImplementedError('this test is not captured')