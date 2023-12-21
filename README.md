# Documentação tolstoi
## API de resolução de CATPCHAs


### Setup inicial:

* **no terminal**
```shell
docker build . -t tolstoi -f Dockerfile --progress=plain
docker run --name tolstoi --volume "D:\desenvolvimento\cefet\tolstoi:/app" -it -d -e DISPLAY=host.docker.internal:0 -p 5001:5001 -p 5000:5000 tolstoi /bin/bash
docker exec -it tolstoi /bin/bash
```

### commands:
* python3 app.py
* celery -A my_celery.celery_tasks.celery_app worker --loglevel=info


do diretorio base:
pip install --no-cache-dir mltu