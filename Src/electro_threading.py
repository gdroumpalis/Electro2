from threading import Thread
class ThreadLooper:

    def __init__(self, target, timeout=-1, name="Processing_Thread" , onfinishexecution = None):
        self.executing = True
        self.runnablemethod = target
        self.timeout = timeout
        self.threadname = name
        self.renderthread = None
        self.onfinishexec = onfinishexecution

    def execution_target(self):
        if self.timeout == -1:
            while self.executing:
                self.runnablemethod()
        else:
            for i in range(0, self.timeout):
                self.runnablemethod()
                print(i)

    def finish_execution(self):
        self.executing = False
        if self.onfinishexec is not None:
            self.onfinishexec()
        print(self.renderthread.name + " finished")

    def run(self):
        self.renderthread = Thread(target=self.execution_target)
        self.renderthread.setName(self.threadname)
        self.renderthread.start()
        print(self.renderthread.name + " started")

    def wait(self):
        self.renderthread.join()

