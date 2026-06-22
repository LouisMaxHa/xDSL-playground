builtin.module {
  func.func @xdsl_main(%0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %c1 = llvm.mlir.constant(1 : i32) : i32
    %llvmAlloca = llvm.alloca %c1 x i64 {alignment = 32 : i64} : (i32) -> !llvm.ptr
    %addrAllocaXPtr = builtin.unrealized_conversion_cast %llvmAlloca : !llvm.ptr to !ptr_xdsl.ptr
    %addrAlloca = ptr_xdsl.from_ptr %addrAllocaXPtr : !ptr_xdsl.ptr -> memref<i64>
    memref.store %0, %addrAlloca[] : memref<i64>
    %addrLocal = memref.load %addrAlloca[] : memref<i64>
    %llvmPtr = llvm.inttoptr %addrLocal : i64 to !llvm.ptr
    %ptrPtr = builtin.unrealized_conversion_cast %llvmPtr : !llvm.ptr to !ptr_xdsl.ptr
    %deref = ptr_xdsl.from_ptr %ptrPtr : !ptr_xdsl.ptr -> memref<i64>
    %loaded = memref.load %deref[] : memref<i64>
    func.return %loaded : i64
  }
}