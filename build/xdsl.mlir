builtin.module {
  func.func @xdsl_main(%0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %llvmPtr = llvm.inttoptr %0 : i64 to !llvm.ptr
    %ptrPtr = builtin.unrealized_conversion_cast %llvmPtr : !llvm.ptr to !ptr_xdsl.ptr
    %deref = ptr_xdsl.from_ptr %ptrPtr : !ptr_xdsl.ptr -> memref<i64>
    %loaded = memref.load %deref[] : memref<i64>
    func.return %loaded : i64
  }
}