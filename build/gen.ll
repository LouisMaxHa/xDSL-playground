; ModuleID = 'LLVMDialectModule'
source_filename = "LLVMDialectModule"

define i64 @xdsl_main(i64 %0) {
  %2 = alloca i64, align 32
  store i64 %0, ptr %2, align 4
  %3 = load i64, ptr %2, align 4
  %4 = inttoptr i64 %3 to ptr
  %5 = load i64, ptr %4, align 4
  ret i64 %5
}

define i64 @_mlir_ciface_xdsl_main(i64 %0) {
  %2 = call i64 @xdsl_main(i64 %0)
  ret i64 %2
}

!llvm.module.flags = !{!0}

!0 = !{i32 2, !"Debug Info Version", i32 3}
