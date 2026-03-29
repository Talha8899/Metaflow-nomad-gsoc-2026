from metaflow import FlowSpec, step

class MyFirstFlow(FlowSpec):
    #the step decorater help to create a flow  
    @step
    def start(self):
        print("hello talha i am starting ")
        #this lines tell the flow where to go next 
        self.next(self.end)

    @step
    def end(self):
        print("this is the end thank you")
    
if __name__ == '__main__':
    MyFirstFlow()