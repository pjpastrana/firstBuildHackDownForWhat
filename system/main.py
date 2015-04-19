import threading
from mcr12 import *
import subprocess
import os
import sys
import time
from firebase import firebase
import datetime

SHELFIE_EXE = "/home/root/smart_shelf"
NUM_FORCE_SAMPLES = 5
BASE_FORCES = [0.0, 0.0, 0.0, 0.0]
WEIGHT = 0
FIREDB = firebase.FirebaseApplication('https://torrid-heat-7640.firebaseio.com', None)
MOCKING = True

def main():
    init()
    #create_and_start_upc_scan_thread()
    create_and_start_weight_change_thread()

def init():
    print "init start"
    calculate_base_forces()
    set_db_location_vals_to_empty_string()
    print "init done"
    
def calculate_base_forces():
    global WEIGHT
    if MOCKING:
        BASE_FORCES[0] = 10.0
        BASE_FORCES[1] = 10.0
        BASE_FORCES[2] = 10.0
        BASE_FORCES[3] = 10.0
        WEIGHT = 4
        print_array("base forces", BASE_FORCES)
        return
    
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
    WEIGHT = calculate_weight(BASE_FORCES)[0]
    print_array("base forces", BASE_FORCES)

def set_db_location_vals_to_empty_string():
    print "setting location to empty in DB"
    FIREDB.put('/locationStatus/q0', 'upc', "empty")
    FIREDB.put('/locationStatus/q1', 'upc', "empty")
    FIREDB.put('/locationStatus/q2', 'upc', "empty")
    FIREDB.put('/locationStatus/q3', 'upc', "empty")
    print "done resetting DB"

def create_and_start_upc_scan_thread():
    add_item_thread = threading.Thread(target=scan_has_ocurred)
    add_item_thread.start()

def create_and_start_weight_change_thread():
    weight_change_thread = threading.Thread(target=weight_change_ocurred)
    weight_change_thread.start()
    return
    
def scan_has_ocurred():
    while True:
        barcode = mock_get_barcode()
        print "barcode "+ barcode
        add_item(barcode)    

def add_item(barcode):
    global WEIGHT
    print "adding item"
    turn_lights_on()
    wait_for_weight_change()
    f_vals = compute_force()
    delta_f = compute_delta_force(f_vals)
    if(not valid_forces_for_add(delta_f) ):
        return
    weight = calculate_weight(delta_f)
    Quadrant = calculate_quadrant(delta_f)
    update_base_forces(f_vals)
    WEIGHT = weight[0]
    print_array("weight", weight)
    print_array("quadrant", quadrant)
    push_to_db(barcode, weight, quadrant)

def turn_lights_on():
    cmd = [SHELFIE_EXE, "l"]
    exec_command(cmd)

# weighting for the user to place item in the shelf
def wait_for_weight_change():
    print "waiting for weight change"
    time.sleep(5)
    
def compute_force():
    if MOCKING:
        force_values = [9.0, 8.0, 7.0, 6.0]
        print_array("force values", force_values)
        return force_values
    
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
    delta_f[0] = f_vals[0] - BASE_FORCES[0]
    delta_f[1] = f_vals[1] - BASE_FORCES[1]
    delta_f[2] = f_vals[2] - BASE_FORCES[2]
    delta_f[3] = f_vals[3] - BASE_FORCES[3]
    print_array("delta force", delta_f)
    return delta_f

def valid_forces_for_add(delta_f):
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
    print "pushing to db"
    timestamp = datetime.datetime.utcnow()
    FIREDB.put('/locationStatus/q'+str(quadrant[0]), 'upc' , str(upc))
    FIREDB.post('/eventLog/', {'upc':str(upc), 'weight':str(weight[0]), 'timestamp':timestamp})

def weight_change_ocurred():
    global WEIGHT
    while True:
        f_vals = compute_force()
        delta_f = compute_delta_force(f_vals)
        weight = calculate_weight(delta_f)[0]
        print "WEIGHT ",
        print WEIGHT,
        print " weight ",
        print weight
        print "(WEIGHT - WEIGHT * .10) ",
        print (WEIGHT - WEIGHT * .10)
        print weight <= (WEIGHT - WEIGHT * .10) 
        if(valid_forces_for_remove(delta_f) and weight <= (WEIGHT - WEIGHT * .10) ):
            remove_item()
        time.sleep(3)

def valid_forces_for_remove(delta_f):
    for i in range(len(delta_f)):
        if delta_f[i] > 0:
            print "delta forces for removing item should be negative"
            return False
    return True

def remove_item():
    print "item removed"

def calculate_anal_dig_values():
    if MOCKING:
        return [1, 2, 3, 4]
    cmd = [SHELFIE_EXE, "a"]
    vals = exec_command(cmd)
    return str_list_to_int_list(vals)

def calculate_resistance(ad_vals):
    if MOCKING:
        return [1.0, 2.0, 3.0, 4.0]
    cmd = [SHELFIE_EXE, "r", str(ad_vals[0]), str(ad_vals[1]), str(ad_vals[2]), str(ad_vals[3]) ]
    vals = exec_command(cmd)
    return str_list_to_float_list(vals)

def calculate_force_values(r_vals):
    if MOCKING:
        return [1.0, 2.0, 3.0, 4.0]
    cmd = [SHELFIE_EXE, "f", str(r_vals[0]), str(r_vals[1]), str(r_vals[2]), str(r_vals[3]) ]
    vals = exec_command(cmd)
    return str_list_to_float_list(vals)

def calculate_weight(f_vals):
    if MOCKING:
        return [3.0]
    cmd = [SHELFIE_EXE, "w", str(f_vals[0]), str(f_vals[1]), str(f_vals[2]), str(f_vals[3]) ]
    vals = exec_command(cmd)
    return str_list_to_float_list(vals)

def calculate_quadrant(f_vals):
    if MOCKING:
        return [4]
    cmd = [SHELFIE_EXE, "q", str(f_vals[0]), str(f_vals[1]), str(f_vals[2]), str(f_vals[3]) ]
    vals = exec_command(cmd)
    return str_list_to_int_list(vals)

def exec_command(cmd):
    if MOCKING:
        print_array("Executing commands", cmd)
        return ""
    proc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    values = output.split()
    return values

def str_list_to_int_list(str_list):
    cast_list_to_type(str_list, "i")

def str_list_to_float_list(str_list):
    cast_list_to_type(str_list, "f")


def cast_list_to_type(values, data_type):
    for i in range(len(values)):
        if data_type == "i":
            values[i] = int(values[i])
        else:
            values[i] = float(values[i])
    return values
        
def print_array(msg, array):
    print msg+": ",
    print array

##
# MOCKING FUNCTIONS FOR TESTING
##
def mock_get_barcode():
    while True:
        time.sleep(2)
        return "1234567"
        
# start process
if __name__ == "__main__":
    main()

