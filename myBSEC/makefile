default: all

all: python_wrapper.o bsec_integration.o
	gcc -fPIC -shared python_wrapper.o bsec_integration.o -L./algo -lalgobsec -o bsec_python.so -lm 

python_wrapper.o: ./src/python_wrapper.c bsec_integration.o
	gcc -fPIC -c ./src/python_wrapper.c -o python_wrapper.o -lm

bsec_integration.o: ./src/bsec_integration_backend.c
	gcc -fPIC -c ./src/bsec_integration_backend.c -o bsec_integration.o -lm

clean:
	rm -rf *.o
	rm bsec_python.so