import docker
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DockerManager:
    _client: Optional[docker.DockerClient] = None
    _available: bool = False
    _checked: bool = False

    @classmethod
    def get_client(cls) -> Optional[docker.DockerClient]:
        if cls._client:
            return cls._client
        
        try:
            cls._client = docker.from_env()
            cls._client.ping()
            cls._available = True
        except Exception as e:
            logger.warning(f"无法连接到 Docker 守护进程: {e}")
            cls._available = False
            cls._client = None
        
        cls._checked = True
        return cls._client

    @classmethod
    def is_available(cls) -> bool:
        if not cls._checked:
            cls.get_client()
        return cls._available

    @classmethod
    def manage_watchtower(cls, enable: bool) -> bool:
        client = cls.get_client()
        if not client:
            return False

        container_name = "watchtower"
        
        # 1. 检查是否存在旧容器
        try:
            container = client.containers.get(container_name)
            if not enable:
                # 如果要禁用，且容器存在，则停止并删除
                logger.info("正在停止并删除 Watchtower 容器...")
                container.stop()
                container.remove()
                return True
            else:
                # 如果要启用，且容器已存在
                if container.status != 'running':
                    container.start()
                return True
        except docker.errors.NotFound:
            # 容器不存在
            if not enable:
                return True
            # 如果要启用且不存在，则创建
            pass
        except Exception as e:
            logger.error(f"操作 Watchtower 容器失败: {e}")
            return False

        if enable:
            try:
                logger.info("正在启动 Watchtower 容器...")
                # 启动 Watchtower
                # 命令: watchtower tgstate --interval 300 --cleanup
                # 挂载: /var/run/docker.sock:/var/run/docker.sock
                client.containers.run(
                    image="containrrr/watchtower:latest",
                    command="tgstate --interval 300 --cleanup",
                    name=container_name,
                    detach=True,
                    restart_policy={"Name": "always"},
                    volumes={
                        "/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}
                    }
                )
                return True
            except Exception as e:
                logger.error(f"启动 Watchtower 失败: {e}")
                return False
        
        return True

    @classmethod
    def get_watchtower_status(cls) -> bool:
        client = cls.get_client()
        if not client:
            return False
        try:
            container = client.containers.get("watchtower")
            return container.status == 'running'
        except docker.errors.NotFound:
            return False
        except Exception:
            return False
