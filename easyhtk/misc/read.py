import xml.etree.ElementTree as ElementTree
from datetime import datetime


def _get_root(eaf):
    root = ElementTree.parse(eaf).getroot()
    return root


def _get_time_order(root):
    time_order = dict()
    for child in root.find('TIME_ORDER'):
        time_order[
            child.attrib.get('TIME_SLOT_ID')
        ] = child.attrib.get('TIME_VALUE')
    return time_order


def _get_tiers(root):
    tiers = dict()
    annotations = dict()
    for child in root.findall('TIER'):
        for sub_child in child.findall('ANNOTATION'):
            annotations[sub_child[0].attrib.get('ANNOTATION_ID')] = {
                'begin_time_slot': sub_child[0].attrib.get('TIME_SLOT_REF1'),
                'end_time_slot': sub_child[0].attrib.get('TIME_SLOT_REF2'),
                'annotation_value': sub_child[0][0].text
            }
        tiers[child.attrib.get('TIER_ID')] = annotations
        annotations = {}
    return tiers


def _get_times_ms(tiers, time_order):
    for key in tiers.keys():
        for sub_key in tiers[key].keys():
            for label in ['begin_time_', 'end_time_']:
                tiers[key][sub_key][label + 'value'] = int(
                    time_order[tiers[key][sub_key][label + 'slot']]
                )
            tiers[key][sub_key]['duration'] = int(
                tiers[key][sub_key]['end_time_value']) - int(
                tiers[key][sub_key]['begin_time_value'])
    return tiers


def _format_times(tiers):
    for key in tiers.keys():
        for sub_key in tiers[key].keys():
            tiers[key][sub_key]['begin_time_value_formatted'] = \
                datetime.utcfromtimestamp(
                    tiers[key][sub_key]['begin_time_value'] / 1000).strftime(
                    '%H:%M:%S.%f')
            tiers[key][sub_key]['end_time_value_formatted'] = \
                datetime.utcfromtimestamp(
                    tiers[key][sub_key]['end_time_value'] / 1000).strftime(
                    '%H:%M:%S.%f')
    return tiers


def read_eaf(eaf_path):
    root = _get_root(eaf_path)
    time_order = _get_time_order(root)
    tiers = _get_tiers(root)
    tiers = _get_times_ms(tiers, time_order)
    tiers = _format_times(tiers)
    return tiers
