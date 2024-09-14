FROM ubuntu:22.04

EXPOSE 8000

WORKDIR /app

RUN apt-get update

RUN apt-get install -y curl unzip gpg wget lsb-release python3-venv vim

# AWS CLI 설치
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update

# Terraform-CLI 설치
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" \
    | tee /etc/apt/sources.list.d/hashicorp.list && \
    apt-get update && apt-get install -y terraform && apt-get clean

COPY . /app

# FastAPI 가상환경 생성 및 의존성 설치

RUN python3 -m venv venv && . venv/bin/activate && pip install --no-cache-dir -r requirements.txt 

CMD ["/bin/sh", "-c", ". venv/bin/activate && uvicorn main:app --host=0.0.0.0"]

