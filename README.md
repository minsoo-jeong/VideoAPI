### Video API
---


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

![diagram](https://i.imgur.com/oPhXPOt.png)



### 

transnetv2: https://www.dropbox.com/s/53cl3l6x7q5luvg/transnetv2.onnx?dl=0