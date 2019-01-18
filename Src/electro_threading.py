from threading import Thread
class ThreadLooper:

    def __init__(self, target, timeout=-1, name="Processing_Thread" , onfinishexecution = None):
        self.executing = True
        self.execution_method = target
        self.timeout = timeout
        self.thread_name = name
        self.render_thread = None
        self.onfinishexec = onfinishexecution

    def execution_target(self):
        if self.timeout == -1:
            while self.executing:
                self.execution_method()
        else:
            for i in range(0, self.timeout):
                self.execution_method()
                print(i)

    def finish_execution(self):
        self.executing = False
        if self.onfinishexec is not None:
            self.onfinishexec()
        print(self.render_thread.name + " finished")

    def run(self):
        self.render_thread = Thread(target=self.execution_target)
        self.render_thread.setName(self.thread_name)
        self.render_thread.start()
        print(self.render_thread.name + " started")

    def wait(self):
        self.render_thread.join()

