module {
  llvm.func @xdsl_main(%arg0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %0 = llvm.mlir.constant(1 : index) : i64
    %1 = llvm.alloca %0 x i64 : (i64) -> !llvm.ptr
    %2 = llvm.mlir.poison : !llvm.struct<(ptr, ptr, i64)>
    %3 = llvm.insertvalue %1, %2[0] : !llvm.struct<(ptr, ptr, i64)> 
    %4 = llvm.insertvalue %1, %3[1] : !llvm.struct<(ptr, ptr, i64)> 
    %5 = llvm.mlir.constant(0 : index) : i64
    %6 = llvm.insertvalue %5, %4[2] : !llvm.struct<(ptr, ptr, i64)> 
    %7 = builtin.unrealized_conversion_cast %6 : !llvm.struct<(ptr, ptr, i64)> to memref<i64>
    %8 = builtin.unrealized_conversion_cast %7 : memref<i64> to !llvm.ptr
    llvm.store %arg0, %8 : i64, !llvm.ptr
    %9 = builtin.unrealized_conversion_cast %7 : memref<i64> to !llvm.ptr
    %10 = llvm.load %9 : !llvm.ptr -> i64
    %11 = llvm.inttoptr %10 : i64 to !llvm.ptr
    %12 = llvm.load %11 : !llvm.ptr -> i64
    llvm.return %12 : i64
  }
  llvm.func @_mlir_ciface_xdsl_main(%arg0: i64) -> i64 attributes {llvm.emit_c_interface} {
    %0 = llvm.call @xdsl_main(%arg0) : (i64) -> i64
    llvm.return %0 : i64
  }
}

