module {
  llvm.func @xdsl_main(%arg0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %0 = llvm.mlir.constant(1 : i32) : i32
    %1 = llvm.alloca %0 x i64 {alignment = 32 : i64} : (i32) -> !llvm.ptr
    llvm.store %arg0, %1 : i64, !llvm.ptr
    %2 = llvm.load %1 : !llvm.ptr -> i64
    %3 = llvm.inttoptr %2 : i64 to !llvm.ptr
    %4 = llvm.load %3 : !llvm.ptr -> i64
    llvm.return %4 : i64
  }
  llvm.func @_mlir_ciface_xdsl_main(%arg0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %0 = llvm.call @xdsl_main(%arg0) : (i64) -> i64
    llvm.return %0 : i64
  }
}

