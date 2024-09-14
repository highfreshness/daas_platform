import re
import os
import json
import asyncio
from typing import List
from ast import literal_eval
from fastapi import HTTPException
from function.guacamole import create_guacamole_connection, delete_guacamole_connection


def remove_ansi_escape_sequences(text: str) -> str:
    # ANSI escape sequences 패턴
    ansi_escape_pattern = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    text = ansi_escape_pattern.sub("", text)
    # 개행 문자 제거
    text = text.replace("\n", " ")
    # 필요시 중복된 공백 제거
    plain_text = re.sub(" +", " ", text).strip()
    return plain_text


def create_hcl(user_config: dict) -> str:
    terraform_config = f"""
    terraform {{
        required_providers {{
            aws = {{
                source  = "hashicorp/aws"
                version = "~> 5.0"
            }}
        }}
    }}

    provider "aws" {{
        region = "ap-northeast-2"
    }}

    # EC2 설정 
    resource "aws_instance" "EC2" {{
        launch_template {{
            id      = "{user_config['template_id']}" 
            version = "$Latest"  
        }}
        tags = {{
            Name = "{user_config['user_id']+'_'+user_config['seq']}"
        }}
        get_password_data = true
    }}

    output "instance_id" {{
      value = aws_instance.EC2.id
    }}

    output "instance_private_ip" {{
        value = aws_instance.EC2.private_ip
    }}
    
    output "instance_tag_name" {{
        value = aws_instance.EC2.tags["Name"]
    }}
    """

    output_path = os.path.join(
        os.getcwd(), "user_tf", user_config["user_id"], user_config["seq"]
    )
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_path = os.path.join(
        output_path, f"{user_config['user_id']}_{user_config['seq']}.tf"
    )
    with open(file_path, "w") as file:
        file.write(terraform_config)
    return output_path


async def decrypt_password(instance_id: str, key_path: str = "./key.pem"):
    decrypt_command = [
        "aws",
        "ec2",
        "get-password-data",
        "--instance-id",
        f"{instance_id}",
        "--priv-launch-key",
        f"{key_path}",
    ]
    decrypt_process = await run_command(decrypt_command)
    return decrypt_process


async def run_command(command: List[str]):
    try:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            print((f"Command failed: {stderr.decode()}"))
            raise HTTPException(
                status_code=409, detail="확인할 수 없는 유저 정보 또는 상태입니다. "
            )
        return stdout.decode()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error"
        )


async def terraform_apply(output_path: str) -> str:
    init_command = ["terraform", f"-chdir={output_path}", "init"]
    await run_command(init_command)

    apply_command = ["terraform", f"-chdir={output_path}", "apply", "--auto-approve"]
    await run_command(apply_command)

    # Terraform 결과 추출
    terraform_result_path = os.path.join(output_path, "terraform.tfstate")
    with open(terraform_result_path, "r") as file:
        result_data = json.load(file)

    instance_id = result_data["outputs"]["instance_id"]["value"]
    instance_private_ip = result_data["outputs"]["instance_private_ip"]["value"]
    instance_tag_name = result_data["outputs"]["instance_tag_name"]["value"]

    # Password 복호화
    pass_data = await decrypt_password(instance_id)
    password = literal_eval(pass_data)["PasswordData"]

    # Guacamole Connection 생성
    await create_guacamole_connection(
        instance_tag_name,
        password,
        instance_private_ip,
    )
    return result_data


async def terraform_destroy(work_dir: str, connection_name: str) -> str:
    destroy_command = ["terraform", f"-chdir={work_dir}", "destroy", "--auto-approve"]
    destroy_process = await run_command(destroy_command)
    result = remove_ansi_escape_sequences(destroy_process)
    # Guacamole 연결 삭제
    await delete_guacamole_connection(connection_name)
    return result
