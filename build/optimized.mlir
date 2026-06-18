module {
  func.func @xdsl_main(%arg0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %alloca = memref.alloca() : memref<i64>
    %0 = builtin.unrealized_conversion_cast %alloca : memref<i64> to !llvm.ptr
    llvm.store %arg0, %0 : i64, !llvm.ptr
    %1 = builtin.unrealized_conversion_cast %alloca : memref<i64> to !llvm.ptr
    %2 = llvm.load %1 : !llvm.ptr -> i64
    %3 = llvm.inttoptr %2 : i64 to !llvm.ptr
    %4 = llvm.load %3 : !llvm.ptr -> i64
    return %4 : i64
  }
}

