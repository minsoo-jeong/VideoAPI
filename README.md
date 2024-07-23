```
+--------------------+                        +------------------+                      +------------------+
|                    |                        |                  |                      |                  |
|       Client       |  ---[HTTP Request]---> |     FastAPI      | ---[Store Task]----> |      Redis       |
|                    |                        | (Gunicorn+Uvicorn)|                      | (Broker + Result)|
|                    |                        |                  | <---[Get Status]---- |                  |
+--------------------+                        +------------------+                      +------------------+
                                                                                               ^
                                                                                               |
                                                                                               |
                                                                                               |
                                                                                               v
                                                                                       +------------------+
                                                                                       |                  |
                                                                                       |  Celery Workers  |
                                                                                       |                  |
                                                                                       +--------+---------+
                                                                                                |
                                                                                                |
                                                                                                v
                                                                                       +------------------+
                                                                                       |                  |
                                                                                       |  Triton Inference|
                                                                                       |     Server       |
                                                                                       |                  |
                                                                                       +------------------+
```