builtin.module {
  func.func @xdsl_main(%0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %addrAlloca = memref.alloca() : memref<i64>
    %1 = builtin.unrealized_conversion_cast %addrAlloca : memref<i64> to !llvm.ptr
    "llvm.store"(%0, %1) <{ordering = 0 : i64}> : (i64, !llvm.ptr) -> ()
    %addrLocal = builtin.unrealized_conversion_cast %addrAlloca : memref<i64> to !llvm.ptr
    %addrLocal_1 = "llvm.load"(%addrLocal) <{ordering = 0 : i64}> : (!llvm.ptr) -> i64
    %llvmPtr = llvm.inttoptr %addrLocal_1 : i64 to !llvm.ptr
    %loaded = "llvm.load"(%llvmPtr) <{ordering = 0 : i64}> : (!llvm.ptr) -> i64
    func.return %loaded : i64
  }
}