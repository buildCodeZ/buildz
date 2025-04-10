.PHONY: cpp_depend ALL
TARGETLIB = libcxf.a
TARGETLIB_CPP = cxf
TARGETDYN=cxf.so
SRC=$(wildcard loaderz/*.cpp) $(wildcard loaderz/**/*.cpp)
OBJ=$(SRC:.cpp=.o)
ALL:$(TARGETLIB) $(TARGETDYN)
	echo "$(SRC)"

$(TARGETDYN):$(OBJ)
	g++ -O3 -fPIC -shared -o $@ $^ -static-libstdc++ -static-libgcc
$(TARGETLIB): $(OBJ)
	ar -rc $@ $^
test: $(OBJ)
	g++ -O3 $^ -o $@
%.o:%.cpp
	g++ -O3 -fPIC -Wall -g -c $< -o $@

include cpp_depend
cpp_depend:
	g++ -MM $(SRC) > cpp_depend

clean:
	rm $(OBJ)