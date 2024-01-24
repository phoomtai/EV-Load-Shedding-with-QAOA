import os

#ENV = "DEV"
ENV = "PROD"


## server
host = "0.0.0.0"
port = int(os.environ.get("PORT", 5000))


## info
app_name = "Choose DEF"
contacts = "https://www.linkedin.com/in/phoomtai-yindee-676b47256/"
code = "https://github.com/phoomtai"
fontawesome = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css"

about = "Load Shedding Solutions"