builtin.module {
  func.func @xdsl_main(%0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %c1 = llvm.mlir.constant(1 : i32) : i32
    %llvmAlloca = llvm.alloca %c1 x i64 {alignment = 32 : i64} : (i32) -> !llvm.ptr
    llvm.store %0, %llvmAlloca : i64, !llvm.ptr
    %addrLocal = llvm.load %llvmAlloca : !llvm.ptr -> i64
    %llvmPtr = llvm.inttoptr %addrLocal : i64 to !llvm.ptr
    %loaded = llvm.load %llvmPtr : !llvm.ptr -> i64
    func.return %loaded : i64
  }
}