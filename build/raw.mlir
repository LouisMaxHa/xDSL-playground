builtin.module {
  func.func @xdsl_main(%0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %llvmPtr = llvm.inttoptr %0 : i64 to !llvm.ptr
    %loaded = "llvm.load"(%llvmPtr) <{ordering = 0 : i64}> : (!llvm.ptr) -> i64
    func.return %loaded : i64
  }
}