CAST_URL = "http://localhost:3000/"
UPDATE_EVERY_SECONDS = 30

MQ_ADDRESS = "<Ip address of your Futurehome hub>"
MQ_USERNAME = "<Futurehome mq username>"
MQ_PASSWORD = "<Futurehome mq password>"
MQ_PORT = 1884

MQ_MAIN_TOPIC = "pt:j1/mt:cmd/rt:app/rn:angry_dog/ad:1"
MQ_INCLUSION_TOPIC = "pt:j1/mt:evt/rt:ad/rn:google/ad:1"
MQ_SIREN_EVENT_TOPIC = "/rt:dev/rn:google/ad:1/sv:siren_ctrl"
MQ_MEDIA_EVENT_TOPIC = "/rt:dev/rn:google/ad:1/sv:media_player"
MQ_SIREN_COMMAND_TOPIC = "pt:j1/mt:cmd/rt:dev/rn:google/ad:1/sv:siren_ctrl"
MQ_MEDIA_COMMAND_TOPIC = "pt:j1/mt:cmd/rt:dev/rn:google/ad:1/sv:media_player"
