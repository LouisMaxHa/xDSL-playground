module {
  func.func @xdsl_main(%arg0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %0 = llvm.inttoptr %arg0 : i64 to !llvm.ptr
    %1 = llvm.load %0 : !llvm.ptr -> i64
    return %1 : i64
  }
}

