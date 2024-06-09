Make sure:
- that you have Docker Desktop installed
- ports 3306 and 8000 are free for the containers

Clone the docker branch in a folder:
```bash
git clone -b docker https://github.com/delesray/poodle.git
```

Navigate a terminal to poodle:
```bash
cd poodle
```

Build and run the containers:
```bash
docker-compose -f docker-compose.yml up --build
```

Open a browser and access:
http://localhost:8000/docs
