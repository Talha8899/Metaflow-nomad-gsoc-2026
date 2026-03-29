#logic for printing the log 
import logging 
from logging.handlers import RotatingFileHandler

#this is the rapper function which make the decoratoe work
def log_action(func):
    def wrapper(*args,**kwargs):
        logger=get_log(func.__name__)
        logger.info(f"the fuction is start:{func.__name__}")
        #write try catcth so if error ccure during perogram execuion it will write in log file
        try:
            result=func(*args,**kwargs)
            logger.info(f"the fuction is end:{func.__name__}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} crash by {e}",exc_info=True)
    return wrapper

def get_log(name):
    
    #create the brain og logging its remanin same in every cae noly the name in bracket is chnage 
    logger=logging.getLogger(name)
    #set the level of the log like ddebug info warning wtc dbug hace high and covers all others
    logger.setLevel(logging.DEBUG)
    # to check the if there is alredeay pipe ,stream for log flow   creted or not 
    if not logger.handlers:   
    
        #set the formet for thr logs in next steps other can also uses 
        formater=logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        #file handler with filw name and aloslo the backupcopies of lile and saize the copies should b edeelted and new ons are make
        file_handler=RotatingFileHandler("app.log",maxBytes=5*1024*1024,backupCount=3)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formater)
        #consule handler
        console_handler=logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formater)
        #creat the out put stream like a pipe to flow ingormatimion eg logs to save at the same time in file and show on screen
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    #return the funcction defination to the function
    return logger
#call the fuction by giving the name whare data come from 
# note curretly dont add any log in it that store in the file it is the generic file impoert and use


@log_action
def division(a ,b):
    print("starting")
    result=a/b
    print(result)

if __name__== "__main__":
    division(1,0)