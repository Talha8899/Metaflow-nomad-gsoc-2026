from metaflow import FlowSpec, step, retry, catch

class MyFirstFlow(FlowSpec):
    @step
    def start(self):
        print("i am starting ")
        self.next(self.example)

    @retry(times=2)
    @step
    def example(self):
        import random
        if random<0.5:
            raise Exception ("error")
        print("sucess")
        self.next(self.end)

    @step
    def end(self):
        print("this is the end")
    
if __name__ == '__main__':
    MyFirstFlow()