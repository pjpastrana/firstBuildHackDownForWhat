from multiprocessing import Pool
from mcr12 import *
import subprocess
import os
import sys
import time
from firebase import firebase
import datetime

SHELFIE_EXE = "/home/root/smart_shelf"
NUM_FORCE_SAMPLES = 5
NUM_WORKERS = 1
BASE_FORCES = [0.0, 0.0, 0.0, 0.0]
MIN_WEIGHT = -sys.maxint - 1
ITEMS_ADDED = 0
FIREDB = firebase.FirebaseApplication('https://torrid-heat-7640.firebaseio.com', None)

def main():
    pool = Pool(processes=NUM_WORKERS)
    init()
    while True:
        pool.apply_async(get_barcode, callback=add_item)
        #if ITEMS_ADDED > 0:
        #     pool.apply_async(check_weight_change, callback=remove_item)
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
def init():
    calculate_base_forces()
    set_db_location_vals_to_empty_string()

def set_db_location_vals_to_empty_string():
    FIREDB.put('/locationStatus/q0', 'upc', "empty")
    FIREDB.put('/locationStatus/q1', 'upc', "empty")
    FIREDB.put('/locationStatus/q2', 'upc', "empty")
    FIREDB.put('/locationStatus/q3', 'upc', "empty")

def calculate_base_forces():
    num_samples = NUM_FORCE_SAMPLES
    for i in range(num_samples):
        ad_vals = calculate_anal_dig_values()
        r_vals = calculate_resistance(ad_vals)
        f_vals = calculate_force_values(r_vals)
        BASE_FORCES[0] += f_vals[0]
        BASE_FORCES[1] += f_vals[1]
        BASE_FORCES[2] += f_vals[2]
        BASE_FORCES[3] += f_vals[3]
    BASE_FORCES[0] /= float(num_samples)
    BASE_FORCES[1] /= float(num_samples)
    BASE_FORCES[2] /= float(num_samples)
    BASE_FORCES[3] /= float(num_samples)
    print_array("base forces", BASE_FORCES)

def add_item(barcode):
    print "adding item"
    ITEMS_ADDED += 1
    wait_for_weight_change()
    f_vals = compute_force()
    delta_f = compute_delta_force(f_vals)
    if(not valid_forces_for_add(delta_f) ):
        return
    weight = calculate_weight(f_vals)
    quadrant = calculate_quadrant(f_vals)
    update_base_forces(f_vals)
    print_array("weight", weight)
    print_array("quadrant", quadrant)
    push_to_db(barcode, weight, quadrant)
    
def wait_for_weight_change():
    print "waiting for weight change"
    time.sleep(5)
    
def compute_force():
    print "computing avg force"
    num_samples = NUM_FORCE_SAMPLES
    force_values = [0.0, 0.0, 0.0, 0.0]
    for i in range(NUM_FORCE_SAMPLES):
        ad_vals = calculate_anal_dig_values()
        r_vals = calculate_resistance(ad_vals)
        f_vals = calculate_force_values(r_vals)
        force_values[0] += f_vals[0]
        force_values[1] += f_vals[1]
        force_values[2] += f_vals[2]
        force_values[3] += f_vals[3]
    force_values[0] /= float(num_samples)
    force_values[1] /= float(num_samples)
    force_values[2] /= float(num_samples)
    force_values[3] /= float(num_samples)
    print_array("force values", force_values)
    return force_values
    
def compute_delta_force(f_vals):
    print "computing delta force"
    delta_f = [0.0, 0.0, 0.0, 0.0]
    delta_f[0] = abs(BASE_FORCES[0] - f_vals[0])
    delta_f[1] = abs(BASE_FORCES[1] - f_vals[1])
    delta_f[2] = abs(BASE_FORCES[2] - f_vals[2])
    delta_f[3] = abs(BASE_FORCES[3] - f_vals[3])
    print_array("delta force", delta_f)
    return delta_f

def  valid_forces_for_add(delta_f):
    for i in range(len(delta_f)):
        if delta_f[i] < 0:
            print "delta forces for adding item should be positive"
            return False
    return True

def update_base_forces(f_vals):
    BASE_FORCES[0] = f_vals[0]
    BASE_FORCES[1] = f_vals[1]
    BASE_FORCES[2] = f_vals[2]
    BASE_FORCES[3] = f_vals[3]

def push_to_db(upc, weight, quadrant):
    if(weight < MIN_WEIGHT):
        MIN_WEIGHT = weight
    timestamp = datetime.datetime.utcnow()
    FIREDB.put('/locationStatus/q'+quadrant, 'upc' , upc)
    FIREDB.post('/eventLog/', {'upc':upc, 'weight':weight, 'timestamp':timestamp})

def check_weight_change():
    f_vals = compute_force()
    delta_f = compute_delta_force(f_vals)
    if(valid_forces_for_remove(delta_f) ):
        remove_item()
        #return

def  valid_forces_for_remove(delta_f):
    for i in range(len(delta_f)):
        if not (delta_f[i] > MIN_WEIGHT):
            #print "delta forces for removing should be grater than "+MIN_WEIGHT
            return False
    return True

#def remove_item(result):
def remove_item():
    ITEMS_ADDED -= 1
    print "item removed"

def calculate_anal_dig_values():
    cmd = [SHELFIE_EXE, "a"]
    return exec_command(cmd)

def calculate_resistance(ad_vals):
    cmd = [SHELFIE_EXE, "r", str(ad_vals[0]), str(ad_vals[1]), str(ad_vals[2]), str(ad_vals[3]) ]
    return exec_command(cmd)

def calculate_force_values(r_vals):
    cmd = [SHELFIE_EXE, "f", str(r_vals[0]), str(r_vals[1]), str(r_vals[2]), str(r_vals[3]) ]
    return exec_command(cmd)

def calculate_weight(f_vals):
    cmd = [SHELFIE_EXE, "w", str(f_vals[0]), str(f_vals[1]), str(f_vals[2]), str(f_vals[3]) ]
    return exec_command(cmd)

def calculate_quadrant(f_vals):
    cmd = [SHELFIE_EXE, "q", str(f_vals[0]), str(f_vals[1]), str(f_vals[2]), str(f_vals[3]) ]
    return exec_command(cmd)

def exec_command(cmd):
    proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    values = output.split()
    for i in range(len(values)):
        values[i] = float(values[i])
    return values
    
def print_array(msg, array):
    print msg+": ",
    print array
    
# start process
if __name__ == "__main__":
    main()

