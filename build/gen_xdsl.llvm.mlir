module {
  llvm.func @xdsl_main(%arg0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %0 = llvm.inttoptr %arg0 : i64 to !llvm.ptr
    %1 = llvm.load %0 : !llvm.ptr -> i64
    llvm.return %1 : i64
  }
  llvm.func @_mlir_ciface_xdsl_main(%arg0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %0 = llvm.call @xdsl_main(%arg0) : (i64) -> i64
    llvm.return %0 : i64
  }
}

