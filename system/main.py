from multiprocessing import Pool
from mcr12 import *

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

def remove_item(result):
    print "removing item"
    print result
    
# start process
if __name__ == "__main__":
    main()
