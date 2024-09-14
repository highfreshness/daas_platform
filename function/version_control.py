import os
import yaml
from github import Github
from fastapi import HTTPException

GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")
REPO_NAME = "SeSAC-Cloud-dev/k8s"
FILE_PATH = "mattermost/mattermost/mattermost-deployment.yaml"
BRANCH_NAME = "main"


def update_yaml(tag_name):
    try:
        # GitHub 인스턴스 생성
        g = Github(GITHUB_ACCESS_TOKEN)
        repo = g.get_repo(REPO_NAME)

        # 파일 내용 가져오기
        file = repo.get_contents(FILE_PATH, ref=BRANCH_NAME)
        content = file.decoded_content.decode()
        
        yaml_content = yaml.safe_load(content)
        yaml_content["spec"]["template"]["spec"]["containers"][0][
            "image"
        ] = f"214346124741.dkr.ecr.ap-northeast-2.amazonaws.com/cloudnexus/mattermost:{tag_name}"
        updated_content = yaml.safe_dump(
            yaml_content, indent=2, sort_keys=False, default_flow_style=False
        )
        # 변경사항 커밋
        repo.update_file(
            FILE_PATH, f"Update to tag {tag_name}", updated_content, file.sha
        )

        return "Configuration updated successfully"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
