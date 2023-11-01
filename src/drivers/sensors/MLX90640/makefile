default: all

MLX_api.o: MLX90640_API.c
	gcc -c MLX90640_API.c -o MLX_api.o

MLX_driver.o: MLX_Driver.c
	gcc -c MLX_Driver.c -o MLX_driver.o

all: MLX_api.o MLX_driver.o
	gcc MLX_api.o MLX_driver.o -o test -lm

clean:
	rm -rf *.o