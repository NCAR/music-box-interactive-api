python3 interactive/rabbit_mq_model_runner.py &
python3 interactive/rabbit_mq_model_status_listener.py &
# python3 interactive/manage.py runserver 0.0.0.0:8000
python3 interactive/manage.py runserver_plus --cert-file acom.ucar.edu.crt --key-file acom.ucar.edu.key 0.0.0.0:8000
