Make sure:
- that you have Docker Desktop installed
- ports 3307 and 8007 are free for the containers

Clone the docker-production branch in a folder:
```bash
git clone -b docker-production https://github.com/delesray/poodle.git
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
http://localhost:8007/docs
