import sys, time

__version__ = 0.1
__author__ = 'tivaro'

try:
    from IPython.core.display import clear_output
    have_ipython = True
except ImportError:
    have_ipython = False

class ProgressBar:
    def __init__(self, iterations):
        self.started = time.time()
        self.iterations = iterations
        self.elapsed_iter = 0
        self.firstIter = True
        self.iterOffset = 1
        self.prog_bar = '[]'
        self.fill_char = '*'
        self.width = 40
        self.__update_amount(0)
        if have_ipython:
            self.animate = self.animate_ipython
        else:
            self.animate = self.animate_noipython

    def animate_ipython(self, iter=None, msg=None):
        if self.firstIter:
            self.started = time.time()
            self.iterOffset = iter or self.iterOffset
            self.firstIter = False

        if iter:
            self.elapsed_iter = iter + self.iterOffset
        else:
            self.elapsed_iter += 1
        self.update_iteration(msg=msg)
        try:
            clear_output()
        except Exception:
            # terminal IPython has no clear_output
            pass
        print '\r', self,
        sys.stdout.flush()
        
    @staticmethod    
    def sec2str(sec):
        if sec < 60:
            string = "%d sec" % sec
        elif sec < (60 * 60):
            string = "%d min" % (sec / 60)
        else:
            string = "%.1f h" % (sec / (60*60))
        return string

    def update_iteration(self,msg=None):

        #calculate statistics
        percentage = self.elapsed_iter / float(self.iterations) * 100.0
        duration = time.time() - self.started
        sec_per_iter = duration / self.elapsed_iter
        sec_to_go = (self.iterations - self.elapsed_iter) * sec_per_iter
        
        if self.elapsed_iter < self.iterations:
            percentage = min(percentage, 99)
            add_text   = ", to-go: " + ProgressBar.sec2str(sec_to_go)
            add_text  += " (%.2f sec/iter) " % sec_per_iter
        else:
            add_text   = "! duration: " + ProgressBar.sec2str(duration) + "\n"
            
        self.__update_amount(percentage)
        self.prog_bar += '  %d of %s complete' % (self.elapsed_iter, self.iterations)
        if msg:
            self.prog_bar += " [%s]" % msg        
        self.prog_bar += add_text


    def __update_amount(self, new_amount):
        percent_done = int(round((new_amount / 100.0) * 100.0))
        all_full = self.width - 2
        num_hashes = int(round((percent_done / 100.0) * all_full))
        self.prog_bar = '[' + self.fill_char * num_hashes + ' ' * (all_full - num_hashes) + ']'
        pct_place = (len(self.prog_bar) / 2) - len(str(percent_done))
        pct_string = '%d%%' % percent_done
        self.prog_bar = self.prog_bar[0:pct_place] + \
            (pct_string + self.prog_bar[pct_place + len(pct_string):])

    def __str__(self):
        return str(self.prog_bar)
    
if __name__ == "__main__":
        #print "A"
        p = ProgressBar(30)
        #print "b"
        for i in range(30):
            #print "\n\n", i, ">"
            #p.animate(i)
            p.animate()
            time.sleep(0.1)
        