FROM nvcr.io/nvidia/pytorch:23.04-py3
COPY ai-marketing/ ./
COPY requirements.txt ./
COPY email_demo_service_start.sh ./
RUN pip install --upgrade pip 
RUN pip install -r requirements.txt
RUN pip install -e .
RUN pip uninstall transformer-engine -y
CMD ./email_demo_service_start.sh
