import os
import sys
import re
from datetime import datetime

def ret_file_name_full(index,extention,number):
    exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
    date_prefix = datetime.today().strftime("%Y-%m-%d")
    out_path = os.path.join(exe_folder, 'out', date_prefix, number)
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    if extention=='.pdf':
        outFileName = os.path.join(out_path, f"A{index}{extention}")
    else:
        outFileName=os.path.join(out_path,number+extention)
    return outFileName
# def ret_file_name_full(index,extention,pdf_count):
#     exe_folder = os.path.dirname(str(os.path.abspath(sys.argv[0])))
#     date_prefix = datetime.today().strftime("%Y-%m-%d")
#     out_path = os.path.join(exe_folder, 'out', date_prefix, pdf_count)
#     if not os.path.exists(out_path):
#         os.makedirs(out_path)
#
#     if extention=='.pdf':
#         outFileName = os.path.join(out_path, f"{index}{extention}")
#     else:
#         excel_date_prefix = datetime.today().strftime("%Y%m%d_%H%M%S")
#         outFileName=os.path.join(out_path,pdf_count+"_"+excel_date_prefix+extention)
    return outFileName

def remove_invalid_paths(path_val):
    return re.sub(r'[\\/*?:"<>|\n]', "_", path_val)
