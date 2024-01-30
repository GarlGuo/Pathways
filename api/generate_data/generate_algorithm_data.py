from data_loader import GlobalData
import argparse
import numpy as np
import random

parser = argparse.ArgumentParser(
    description='process pathway data and generate csv & pickle pathway files'
)

np.random.seed(0)
random.seed(0)

parser.add_argument('--course_desc_data', action='store_true', default=False,
                    help='need to extract and process course desc file')
parser.add_argument('--course_title_data', action='store_true', default=False,
                    help='need to extract and process course title data')
parser.add_argument('--PC', action='store_true', default=False,
                    help='need to extract and process PC_sparse data')
parser.add_argument('--calibration', action='store_true', default=False,
                    help='need to extract and process calibration course mask data')
args = parser.parse_args()

g = GlobalData(course_data=True, pathway_data=True, major_and_minor_data=True)

if args.course_desc_data:
    g.process_course_desc_list()

if args.course_title_data:
    g.process_course_title()

if args.PC:
    g.process_PC()

if args.calibration:
    g.process_calibration_course_mask()
