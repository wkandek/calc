# A Simple Online Calculator
parsing logic from: https://www.dabeaz.com/ply/example.html  

curl http://localhost:8080/api?op=2+7 # json answer  
curl -d "2+9" -X POST http://localhost:8080/api  
curl http://calc.kandek.com:8080/api?op=2+7 # json answer  
curl -d "2+9" -X POST http://calc.kandek.com:8080/api  
browse to local:8080 for form interface  

I use it a lot for demos: python development -> docker -> kubernetes -> tracing
