echo "RUNNING SERVICE START"
nohup python -m fastchat.serve.controller > controller.out 2>controller.err& 
echo "CONTROLLER RUNNING"
nohup python -m fastchat.serve.model_worker --model-name 'gpt-3.5-turbo' --model-path lmsys/vicuna-7b-v1.5 --num-gpus 1 > worker.out 2>worker.err& 
echo "MODEL_WORKER RUNNING"
nohup python -m fastchat.serve.openai_api_server --host 0.0.0.0 --port 8001 > api_server.out 2>api_server.err&
echo "API_SERVER RUNNING"
nohup python sql/setup.py --drop-tables&
nohup python sql/make_udfs.py&
echo "SETUP DONE"
nohup python -m streamlit run app/main.py > streamlit.out 2>streamlit.err&
jupyter lab --no-browser --allow-root --ip=0.0.0.0 --NotebookApp.token='' --NotebookApp.password=''
