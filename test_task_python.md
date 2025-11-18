
# Task overview

Create two services that communicate with each other. One that periodically sends out predefined event payloads and another one that consumes them.  
  
The code for the task must be written in Python.  

## The first service (Event propagator)

Description: The service should periodically (every N seconds) send a predefined JSON object to a specific HTTP API endpoint.

Requirements for the first service:

1. The period of time should be measured in seconds.
 ✅ Done you can provide in config (interval)

2. The period of time between sent JSON objects(events) should be configurable via a configuration file or startup arguments.
✅ Done you can provide in config ()

3.  The HTTP API endpoint that the payloads are sent to should be configurable via a configuration file or startup arguments. 
✅ Done you can provide in config(url) 
  
4.  The predefined JSON objects(events) that can be sent should be read from a file.
 ✅ Done you can read from events.json 
    
5.  The location of the JSON objects(events) file should be configurable via a configuration file or startup arguments. 
✅  Done you can provide file of event in config 
    
6.  The algorithm for choosing a specific JSON object(event) to send at each period from all the objects read from file, should be random. 
✅  Done using random.choice
        
The array of JSON objects(events) that can be sent individually:  


    [
	    {
		    "event_type":"message",
		    "event_payload":"hello"
	    },
	    {
		    "event_type":"user_joined",
		    "event_payload":"Peter"
	    },
	    {
		    "event_type":"message",
		    "event_payload":"greetings"
	    },
	    {
		    "event_type":"message",
		    "event_payload":"no, thanks"
	    },
	    {
		    "event_type":"user_joined",
		    "event_payload":"Jack"
		},
	    {
		    "event_type":"message",
		    "event_payload":"yes, please"
	    },
	    {
		    "event_type":"user_joined",
		    "event_payload":"Thomas"
	    },
	    {
		    "event_type":"message",
		    "event_payload":"okay"
	    },
	    {
		    "event_type":"message",
		    "event_payload":"welcome"
	    },
	    {
		    "event_type":"user_left",
		    "event_payload":"Thomas"
	    },
	    {
		    "event_type":123,
		    "event_payload":{}
	    }
    ]

  

## The second service (Event consumer)

Description: The service should expose a HTTP API endpoint that accepts incoming JSON payloads and persists them somewhere: to a database (preferably)
or to a file.

Requirements for the first service:

7.  The service should expose a HTTP API endpoint that accepts incoming POST requests on the path `/event`
 ✅ Done

    
8.  The port for running HTTP API should be configurable via a configuration file or startup arguments.
 ✅ Done you can provide in config(port)
   
9.  The persistent storage parameters for the incoming payloads should be configurable via a configuration file or startup arguments.
 ✅ Done you can provide in config db_type



10.  The service should only accept payloads matching this JSON template:
✅ Done throws http errors

    [
	    {
		    "event_type": string,
		    "event_payload": string
	    }
    ]

Upon task completion:

-   Write an instruction on how to run the project (preferably a Makefile with a predefined launch command)

-   To manage dependencies provide a pyproject.toml fpr Poetry (preferable) or requirements.txt
    
-   Store the source code in some Git repo and invite:
	Dzmitry Kamenda		dzmitry.kamenda@cybercare.cc
	Ignas Šimkūnas		ignas.simkunas@cybercare.cc
	Karolis Pakalnis	karolis.pakalnis@cybercare.cc
