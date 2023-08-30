#!usr/bin/env python
# -*- coding: utf8 -*-
#
# -----------------------------------------------------------------------------
#   File: converters.py (as part of project conversations)
#   Created: 14/12/2022 16:27
#   Last Modified: 14/12/2022 16:27
# -----------------------------------------------------------------------------
#   Author: William N. Havard
#           Postdoctoral Researcher
#
#   Mail  : william.havard@ens.fr / william.havard@gmail.com
#  
#   Institution: ENS / Laboratoire de Sciences Cognitives et Psycholinguistique
#
# ------------------------------------------------------------------------------
#   Description: 
#       • 
# -----------------------------------------------------------------------------

import re
import pandas as pd
import logging


def from_csv(filepath) -> pd.DataFrame:
    """
    Reads a CSV file and return a data frame
    :param filepath: path to the CSV file to be read
    :type filepath: str
    :return: pandas DataFrame
    :rtype: pd.DataFrame
    """
    # TODO: for CLI interface, allow user to drop lines based on condition
    df = pd.read_csv(filepath)

    return df


def from_rttm(filepath, name_mapping=None, source_file: str = None):
    """
    Reads a RTTM file and return a data frame with columns {"segment_onset","segment_offset","speaker_type"}
    :param filepath: path to the RTTM file to be read
    :type filepath: str
    :param name_mapping: mapping of the names used in the RTTM to new names, defaults to None, keeping the original names
    :type name_mapping: dict
    :param source_file: only keep lines belonging to that file, when not set, every line will be kept even if from different recordings
    :type source_file: str
    :return: pandas DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.read_csv(
        filepath,
        sep=" ",
        names=[
            "type",
            "file",
            "chnl",
            "tbeg",
            "tdur",
            "ortho",
            "stype",
            "name",
            "conf",
            "slat",
        ],
    )
    n_recordings = len(df["file"].unique())
    if n_recordings > 1 and not source_file:
        logging.warning(
            "WARNING: {} contains annotations from {} different audio files, but no source_file was specified, "
            "all annotations will be imported as if they belonged to the same recording. "
            "Please make sure this is the intended behavior ".format(filepath, n_recordings)
        )
    df["segment_onset"] = df["tbeg"].mul(1000).round().astype(int)
    df["segment_offset"] = (df["tbeg"] + df["tdur"]).mul(1000).round().astype(int)
    if name_mapping:
        assert isinstance(name_mapping, dict), \
            "keyword argument <name_mapping> should be a dictionary, found <{}>".format(type(name_mapping))
        df["speaker_type"] = df["name"].map(name_mapping)
    else:
        df["speaker_type"] = df["name"]

    if not df.shape[0]:
        logging.warning(
            "no lines found for inside {}, resulting DataFrame is empty".format(filepath))
    elif source_file:
        df = df[df["file"] == source_file]
        if not df.shape[0]:
            logging.warning(
                "no lines found for source_file <{}> inside {},"
                " resulting DataFrame is empty".format(source_file, filepath))

    return df

def from_its(filepath, speaker_mapping=None, recording_num=None) -> pd.DataFrame:
    """
    Reads an ITS file and return a data frame with columns {"segment_onset","segment_offset","speaker_type"}
    :param filepath: path to the ITS file to be read
    :type filepath: str
    :param recording_num: only keep lines belonging to that recording number, when not set, every line will be kept even if from different recordings
    :type recording_num: int
    :return: pandas DataFrame
    :rtype: pd.DataFrame
    """
    from lxml import etree

    xml = etree.parse(filepath)

    recordings = xml.xpath(
        "/ITS/ProcessingUnit/Recording"
        + ('[@num="{}"]'.format(recording_num) if recording_num else "")
    )
    timestamp_pattern = re.compile(r"^P(?:T?)(\d+(\.\d+)?)S$")

    def extract_from_regex(pattern, subject):
        match = pattern.search(subject)
        return match.group(1) if match else ""

    segments = []
    if len(recordings) > 1 and not recording_num:
        logging.warning(
            "WARNING: {} contains annotations from {} assembled recordings. "
            "No recording_num was specified so all annotations will be imported together.".format(filepath,
                                                                                                  len(recordings))
        )
    if recording_num and recording_num > len(recordings):
        logging.warning(
            "WARNING: file {} : recording_num {} does not exist. "
            "Returning empty DataFrame".format(filepath, recording_num, len(recordings))
        )

    for recording in recordings:
        segs = recording.xpath("./Pause/Segment|./Conversation/Segment")
        for seg in segs:
            onset = float(
                extract_from_regex(timestamp_pattern, seg.get("startTime"))
            )
            offset = float(
                extract_from_regex(timestamp_pattern, seg.get("endTime"))
            )

            segments.append(
                {
                    "segment_onset": int(round(onset * 1000)),
                    "segment_offset": int(round(offset * 1000)),
                    "speaker_type": speaker_mapping[seg.get("spkr")] if speaker_mapping else seg.get("spkr"),
                }
            )

    df = pd.DataFrame(segments, columns=['segment_onset', 'segment_offset', 'speaker_type'])

    return df


def from_txt(filepath) -> pd.DataFrame:
    """
    Reads a txt file and return a data frame. The input .txt should be a plain-text,
    tab-separated file with a header row that contains the column names.
    The three columns must be speaker_type , segment_onset , segment_offset
    :param filepath: path to the txt file to be read
    :type filepath: str
    :return: pandas DataFrame
    :rtype: pd.DataFrame
    """
    # TODO: for CLI interface, allow user to drop lines based on condition
    df = pd.read_csv(filepath, sep='\t')

    return df


def from_eaf(filepath) -> pd.DataFrame:
    """
    Reads a EAF file and return a data frame. All the existing tiers are imported
    and the name of the tier is used as the value for speaker_type
    :param filepath: path to the CSV file to be read
    :type filepath: str
    :return: pandas DataFrame
    :rtype: pd.DataFrame
    """
    #
    # TODO handle tiers in more depth, perhaps remove subtiers? Perhaps remove some tiers based on the name?
    # Perhaps map tier names to normalized speaker_type?
    #
    import pympi

    eaf = pympi.Elan.Eaf(filepath)
    segments = {}

    for tier_name in eaf.tiers:
        annotations = eaf.tiers[tier_name][0]

        for aid in annotations:
            (start_ts, end_ts, value, svg_ref) = annotations[aid]
            (start_t, end_t) = (eaf.timeslots[start_ts], eaf.timeslots[end_ts])

            segment = {
                "segment_onset": int(round(start_t)),
                "segment_offset": int(round(end_t)),
                "speaker_type": tier_name,
            }

            segments[aid] = segment

    return pd.DataFrame(segments.values())