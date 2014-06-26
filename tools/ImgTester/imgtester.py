from multiprocessing.pool import ThreadPool
import requests
import optparse
import timeit
import time


parser = optparse.OptionParser()

parser.add_option("-u", "--url", action="store", dest="url", help="URL to test", default="https://www.weblab.deusto.es/webcam/proxied.py/arquimedes1")
parser.add_option("-n", "--number", action="store", dest="number", help="Number of times", default=2000)
parser.add_option("-t", "--threads", action="store", dest="threads", help="Number of threads", default=8)

(options, args) = parser.parse_args()

if options.url is None:
    parser.error("--url not specified")



pool = ThreadPool(options.threads)




def main():
    # Start the specified number of workers.
    pool.map(worker, range(options.threads), 1)

def carry_request():
    start = time.time()
    r = requests.get(options.url)
    data = r.text
    if r.status_code != 200:
        print "ERROR"
    end = time.time()
    report_elapsed(end - start)


elapsed_total = 0
elapsed_num = 0

def worker(n):
    while elapsed_num <= options.number:
        carry_request()

def report_elapsed(elapsed):
    global elapsed_num, elapsed_total
    elapsed_num += 1
    elapsed_total += elapsed
    print "Elapsed Average: %f" % (elapsed_total / elapsed_num)
    print "Elapsed Last: %f" % (elapsed)


main()