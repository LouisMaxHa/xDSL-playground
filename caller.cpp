#include <cassert>
#include <cstdint>
#include <iostream>

extern "C" {
	int64_t _mlir_ciface_xdsl_main(int64_t addr);
}

int main() {
  int* addr = (int*)malloc(sizeof(int));
  (*addr) = 4;
  
  int64_t addr64 = (int64_t)addr;

  int64_t result = _mlir_ciface_xdsl_main(addr64);
  std::cout << "Read int*" << std::endl;
  std::cout << "EXPECTED '4', got '" << result << "'" << std::endl;
  return 0;
}
