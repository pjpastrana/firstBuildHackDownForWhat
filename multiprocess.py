# from multiprocessing import Pool

# def f(x):
#     return x*x

# def hello():
#     print "hello world"

# if __name__ == '__main__':
#     pool = Pool(processes=1)              # start 4 worker processes

#     result = pool.apply_async(f, (10,), None, hello)    # evaluate "f(10)" asynchronously
#     # print "hackDownForWhat!"
#     # print result.get(timeout=100000000)           # prints "100" unless your computer is *very* slow

    

#     # Print pool.map(f, range(10))          # prints "[0, 1, 4,..., 81]"

#     # it = pool.imap(f, range(10))
#     # print it.next()                       # prints "0"
#     # print it.next()                       # prints "1"
#     # print it.next(timeout=1)              # prints "4" unless your computer is *very* slow

#     # import time
#     # result = pool.apply_async(time.sleep, (10,))
#     # print result.get(timeout=1)           # raises TimeoutError


from multiprocessing import Process
import os

def info(title):
    print title
    print 'module name:', __name__
    if hasattr(os, 'getppid'):  # only available on Unix
        print 'parent process:', os.getppid()
    print 'process id:', os.getpid()

def f(name):
    #info('function f')
    print 'hello', name

if __name__ == '__main__':
    #info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()
