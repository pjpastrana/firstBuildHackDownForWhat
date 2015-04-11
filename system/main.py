from multiprocessing import Pool
from mcr12 import *
import subprocess
import os

SHELFIE_EXE = "/home/root/smart_shelf"

def main():
    pool = Pool(processes=2)
    while True:
        pool.apply_async(get_barcode, callback=add_item)
        pool.apply_async(check_weight_change, callback=remove_item)
        #barcode = result.get(timeout=1)
        #print barcode
        #scan_has_ocurred()
        # pool.apply_async(scan_has_ocurred, callback = add_item)
        # pool.close()
        # pool.join()


# def scan_has_ocurred():
#     #pool = Pool(1)
#     pool.apply_async(get_barcode, callback = add_item)
#     #pool.close()
#     pool.join()
#     #return get_barcode("/dev/input/event2")

def check_weight_change():
    return

def add_item(barcode):
    print "adding item"
    print barcode
    ad_vals = calculate_anal_dig_values()
    print ad_vals
    r_vals = calculate_resistance(ad_vals)
    print r_vals
    f_vals = calculate_force_values(r_vals)
    print f_vals
    weight = calculate_weight(f_vals)
    print weight
    quadrant = calculate_quadrant(f_vals)
    print quadrant
    

def calculate_anal_dig_values():
    cmd = [SHELFIE_EXE, "a"]
    return exec_command(cmd)

def calculate_resistance(ad_vals):
    cmd = [SHELFIE_EXE, "r", ad_vals[0], ad_vals[1], ad_vals[2], ad_vals[3] ]
    return exec_command(cmd)

def calculate_force_values(r_vals):
    cmd = [SHELFIE_EXE, "f", r_vals[0], r_vals[1], r_vals[2], r_vals[3] ]
    return exec_command(cmd)

def calculate_weight(f_vals):
    cmd = [SHELFIE_EXE, "w", f_vals[0], f_vals[1], f_vals[2], f_vals[3] ]
    return exec_command(cmd)

def calculate_quadrant(f_vals):
    cmd = [SHELFIE_EXE, "q", f_vals[0], f_vals[1], f_vals[2], f_vals[3] ]
    return exec_command(cmd)

def exec_command(cmd):
    proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    values = output.split()
    return values
    

def remove_item(result):
    print "removing item"
    print result
    
# start process
if __name__ == "__main__":
    main()

